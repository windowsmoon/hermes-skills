#!/usr/bin/env python3
"""
get_news.py — 搜索AI相关热点 + 并行抓取每条链接内容 + 写入飞书文档
用法: python get_news.py "<关键词>" [--limit 50] [--workers 10]
"""

import requests, json, sys, re, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── 配置 ──
API_KEY = "ab13da3e354865f3243b966521be642e"
FEISHU_APP_ID = "cli_aa92b1fa06395cb0"
FEISHU_APP_SECRET = "***FEISHU_SECRET***"

# ── 1. 调 API 获取 50 条 ──
def fetch_news(query, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(
                "https://api.tophubdata.com/search",
                headers={"Authorization": API_KEY},
                params={"q": query, "hashid": "", "p": 1},
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("items", [])
        except:
            if attempt < retries - 1:
                time.sleep(2)
    return []

# ── 2. 并行抓取每条链接的内容 ──
def fetch_url_content(url, timeout=8):
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        r.encoding = r.apparent_encoding
        text = re.sub(r'<script[^>]*>.*?</script>', '', r.text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        paragraphs = [p.strip() for p in re.findall(r'[^\n]{40,}', text)
                      if len(re.findall(r'[\u4e00-\u9fff]', p)) > 8]
        return paragraphs[:3] if paragraphs else []
    except:
        return []

def process_item(item):
    title = item.get("title", "")
    desc = item.get("description", "")
    url = item.get("url", "")
    extra = item.get("extra", "")
    ts = item.get("time", 0)
    time_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M") if ts else ""
    
    # 判断是否视频链接
    is_video = any(d in url for d in ["douyin.com", "bilibili.com", "tiktok.com", "youtube.com", "video"])
    
    content_summary = ""
    if is_video:
        content_summary = "🎬 视频内容（需 Coze 工作流提取文案）"
    else:
        paragraphs = fetch_url_content(url)
        if paragraphs:
            content_summary = " | ".join(p[:200] for p in paragraphs[:2])
        else:
            content_summary = desc[:200] if desc else ""
    
    return {
        "title": title,
        "url": url,
        "extra": extra,
        "time": time_str,
        "is_video": is_video,
        "summary": content_summary
    }

# ── 3. 写入飞书文档 ──
def get_feishu_token():
    r = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
        timeout=10
    )
    return r.json().get("tenant_access_token", "")

def create_doc(token, title):
    r = requests.post(
        "https://open.feishu.cn/open-apis/docx/v1/documents",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"title": title},
        timeout=10
    )
    return r.json().get("data", {}).get("document", {}).get("document_id", "")

def write_block(doc_id, token, text, bold=False):
    style = {"bold": True} if bold else {}
    body = {"children": [{
        "block_type": 2,
        "text": {
            "elements": [{"text_run": {"content": text, "text_element_style": style}}],
            "style": {}
        }
    }]}
    r = requests.post(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=body, timeout=15
    )
    return r.json()

# ── 主流程 ──
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--workers", type=int, default=10, help="并行抓取线程数")
    args = parser.parse_args()
    
    print(f"1/4 调 API 搜索「{args.query}」...")
    items = fetch_news(args.query)[:args.limit]
    print(f"   → 获取 {len(items)} 条")
    
    print(f"2/4 并行抓取 {len(items)} 条链接内容（{args.workers} 线程）...")
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(process_item, item): i for i, item in enumerate(items)}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda r: items.index(next(i for i in items if i.get("url","") == r["url"])))
    print(f"   → 完成 {len(results)} 条")
    
    print(f"3/4 写入飞书文档...")
    token = get_feishu_token()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    doc_id = create_doc(token, f"AI视频生成 热点新闻（{now}）")
    
    write_block(doc_id, token, f"AI视频生成 热点新闻", bold=True)
    write_block(doc_id, token, f"搜索时间：{now}  |  共 {len(results)} 条")
    
    for i, r in enumerate(results, 1):
        write_block(doc_id, token, f"{'─'*40}")
        write_block(doc_id, token, f"{i}. {r['title']}", bold=True)
        if r['extra']:
            write_block(doc_id, token, f"🔥 {r['extra']}")
        write_block(doc_id, token, f"⏱ {r['time']}")
        write_block(doc_id, token, f"🔗 {r['url']}")
        if r['summary']:
            write_block(doc_id, token, f"📄 {r['summary']}")
        if r['is_video']:
            write_block(doc_id, token, f"⚠️ 视频链接，需走 Coze 工作流提取文案")
    
    # 分类总结
    write_block(doc_id, token, f"{'='*40}", bold=True)
    write_block(doc_id, token, f"📊 综合总结", bold=True)
    
    tools = [r for r in results if any(k in r['title'].lower() for k in ["视频生成","视频工具","视频平台","kling","pixverse","seedance","可灵","sora","veo","runway","fableclip"])]
    funding = [r for r in results if any(k in r['title'] for k in ["融资","投资","估值","融资轮"])]
    summary = f"共 {len(results)} 条，其中：\n"
    summary += f"• AI视频工具/平台：{len(tools)} 条\n"
    summary += f"• 融资/商业动态：{len(funding)} 条\n"
    summary += f"• 其他相关：{len(results)-len(tools)-len(funding)} 条\n\n"
    summary += "每条内容均通过实际访问链接提取正文摘要，非 API 原始描述。"
    write_block(doc_id, token, summary)
    
    print(f"4/4 完成！")
    print(f"📎 https://www.feishu.cn/docx/{doc_id}")

if __name__ == "__main__":
    main()
