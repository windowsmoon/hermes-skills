#!/usr/bin/env python3
"""
unified_search.py — 统一搜索：网络（Tavily + Exa + Firecrawl）+ 本地 Obsidian

用法：
  python unified_search.py <查询词> [--sources web,obsidian,all] [--max 5]

Hermes Agent 调用方式：execute_code 执行或 terminal 调用
"""

import os, sys, json, argparse
from datetime import datetime
try:
    import requests
except ImportError:
    import urllib.request as requests

# ── 配置 ──
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "")
EXA_KEY = os.environ.get("EXA_API_KEY", "")
FIRECRAWL_KEY = os.environ.get("FIRECRAWL_API_KEY", "")
MITA_KEY = os.environ.get("MITA_API_KEY", "")

OBSIDIAN_VAULT = "D:/Obsidian/Note"
OBSIDIAN_SCRIPT = os.path.expanduser("~/AppData/Local/hermes/rag_obsidian/query_obsidian.py")




def search_openwebsearch(query, max_results=5):
    """open-webSearch — 多引擎搜索，无需 API Key
    支持引擎: bing, baidu, csdn, duckduckgo, exa, brave, juejin, sogou, startpage
    """
    import subprocess, json, os as _os
    
    npx_path = "C:/Program Files/nodejs/npx.cmd"
    engine = _os.environ.get("OWS_ENGINE", "bing")
    
    try:
        result = subprocess.run(
            [npx_path, "-y", "open-websearch", "search", query,
             "--engine", engine, "--limit", str(max_results), "--json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"source": f"open-webSearch({engine})", "error": result.stderr[:200], "results": []}
        
        raw = json.loads(result.stdout)
        # open-webSearch 返回套了两层: {status, data: {results: [...]}}
        items = raw.get("data", {}).get("results", []) if isinstance(raw.get("data"), dict) else raw.get("results", [])
        results = []
        for r in items:
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", r.get("link", "")),
                "content": r.get("description", r.get("content", ""))[:400],
                "score": r.get("score", 0)
            })
        return {
            "source": f"open-webSearch({engine})",
            "results": results
        }
    except json.JSONDecodeError:
        return {"source": f"open-webSearch({engine})", "error": "JSON parse error", "results": []}
    except Exception as e:
        return {"source": f"open-webSearch({engine})", "error": str(e)[:100], "results": []}



def search_tavily(query, max_results=5):
    """Tavily 搜索 — AI 摘要 + 结构化结果"""
    if not TAVILY_KEY:
        return {"source": "Tavily", "error": "No API key", "results": []}
    # 限制 max_results 不超过 10（Tavily 免费版上限）
    actual_max = min(max_results, 10)
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": TAVILY_KEY, "query": query, "max_results": actual_max,
                  "include_answer": True, "include_raw_content": False},
            timeout=15
        )
        data = resp.json()
        results = []
        for r in data.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:300],
                "score": r.get("score", 0)
            })
        return {
            "source": "Tavily",
            "answer": data.get("answer", ""),
            "results": results
        }
    except Exception as e:
        return {"source": "Tavily", "error": str(e), "results": []}


def search_exa(query, max_results=5):
    """Exa 搜索 — 语义搜索引擎
    支持 category (research paper/news/article/company/pdf)
    支持 contents.text 获取正文内容
    """
    if not EXA_KEY:
        return {"source": "Exa", "error": "No API key", "results": []}
    
    # 从环境变量读取 category
    actual_category = os.environ.get("EXA_CATEGORY", "")
    
    try:
        body = {
            "query": query,
            "numResults": max_results,
            "useAutoprompt": True,
            "contents": {"text": True}  # 获取正文内容
        }
        if actual_category:
            body["category"] = actual_category
        
        resp = requests.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": EXA_KEY, "Content-Type": "application/json"},
            json=body,
            timeout=15
        )
        data = resp.json()
        results = []
        for r in data.get("results", []):
            text = r.get("text", "") or r.get("contents", {}).get("text", "") or ""
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": text[:500],
                "score": r.get("score", 0)
            })
        return {
            "source": "Exa",
            "category": actual_category or "default",
            "results": results
        }
    except Exception as e:
        return {"source": "Exa", "error": str(e), "results": []}




def search_mita(query, max_results=10, scope="web"):
    """秘塔搜索 API — metaso.cn
    支持分页：每页最多10条，自动翻页直到凑够 max_results
    支持 scope: web, academic, news, wiki, video
    支持 conciseSnippet, includeSummary 选项
    """
    key = os.environ.get("MITA_API_KEY", "")
    if not key:
        return {"source": "秘塔", "error": "No API key", "results": []}
    
    # 从环境变量读取 scope
    actual_scope = os.environ.get("MITA_SCOPE", scope)
    
    results = []
    page = 1
    max_pages = (max_results + 9) // 10  # 每页10条，算出需要几页
    if max_pages > 7:
        max_pages = 7  # 安全上限，最多70条
    
    try:
        while page <= max_pages and len(results) < max_results:
            resp = requests.post(
                "https://metaso.cn/api/v1/search",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "q": query,
                    "scope": actual_scope,
                    "count": 10,
                    "page": page,
                    "conciseSnippet": True,
                    "includeSummary": True
                },
                timeout=15
            )
            data = resp.json()
            page_results = data.get("webpages", [])
            if not page_results:
                break
            
            for r in page_results:
                if len(results) >= max_results:
                    break
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "content": r.get("snippet", "")[:500],
                    "score": 1.0 if r.get("score") == "high" else 0.5,
                    "date": r.get("date", ""),
                    "position": r.get("position", 0)
                })
            
            page += 1
            # credits 不递减（免费额度按账号维度，不限频次）
        
        return {
            "source": "秘塔",
            "scope": actual_scope,
            "credits": data.get("credits", 0) if results else 0,
            "total": data.get("total", 0) if results else 0,
            "pages_fetched": page - 1,
            "results": results
        }
    except Exception as e:
        return {"source": "秘塔", "error": str(e), "results": []}


def search_firecrawl(query, max_results=5):
    """Firecrawl 搜索 — 网页抓取搜索引擎（v0 API）"""
    if not FIRECRAWL_KEY:
        return {"source": "Firecrawl", "error": "No API key", "results": []}
    try:
        resp = requests.post(
            "https://api.firecrawl.dev/v0/search",
            headers={"Authorization": f"Bearer {FIRECRAWL_KEY}", "Content-Type": "application/json"},
            json={"query": query, "maxResults": max_results},
            timeout=15
        )
        data = resp.json()
        results = []
        for r in data.get("data", []):
            results.append({
                "title": r.get("title", r.get("url", "")),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],
                "score": 0
            })
        return {"source": "Firecrawl", "results": results}
    except Exception as e:
        return {"source": "Firecrawl", "error": str(e), "results": []}


def search_obsidian(query, max_results=5):
    """本地 Obsidian 笔记搜索（RAG）"""
    if not os.path.exists(OBSIDIAN_SCRIPT):
        return {"source": "Obsidian", "error": "RAG script not found", "results": []}
    try:
        import subprocess
        r = subprocess.run(
            [sys.executable, OBSIDIAN_SCRIPT, query, str(max_results)],
            capture_output=True, text=True, timeout=30
        )
        output = r.stdout.strip()
        results = []
        for line in output.split('\n')[:max_results]:
            if '\t' in line:
                parts = line.split('\t')
                results.append({
                    "title": parts[0].strip(),
                    "content": parts[1].strip() if len(parts) > 1 else "",
                    "score": 1.0
                })
        return {"source": "Obsidian", "results": results}
    except Exception as e:
        return {"source": "Obsidian", "error": str(e), "results": []}


def main():
    parser = argparse.ArgumentParser(description="统一搜索：网络 + 本地笔记")
    parser.add_argument("query", help="搜索关键词")
    parser.add_argument("--scope", default="article",
                        choices=["news", "article", "web", "academic"],
                        help="搜索范围优先级：article→news→web→academic，默认article")
    parser.add_argument("--sources", default="all", 
                        choices=["all", "web", "obsidian", "tavily", "exa", "firecrawl", "mita", "ows"])
    parser.add_argument("--max", type=int, default=10, help="每个来源最多结果数")
    args = parser.parse_args()

    sources = []
    # 根据 --scope 设置各工具的搜索范围
    scope = args.scope
    # 秘塔 scope 映射
    mita_scope_map = {"news": "news", "article": "web", "web": "web", "academic": "academic"}
    # Exa category 映射
    exa_cat_map = {"news": "news", "article": "article", "web": "web", "academic": "research paper"}
    os.environ["MITA_SCOPE"] = mita_scope_map.get(scope, "web")
    os.environ["EXA_CATEGORY"] = exa_cat_map.get(scope, "web")
    
    if args.sources == "all":
        sources = [search_tavily, search_exa, search_firecrawl, search_mita, search_openwebsearch, search_obsidian]
    elif args.sources == "web":
        sources = [search_tavily, search_exa, search_firecrawl]
    elif args.sources == "tavily":
        sources = [search_tavily]
    elif args.sources == "exa":
        sources = [search_exa]
    elif args.sources == "firecrawl":
        sources = [search_firecrawl]
    elif args.sources == "mita":
        sources = [search_mita]
    elif args.sources == "ows":
        sources = [search_openwebsearch]
    elif args.sources == "obsidian":
        sources = [search_obsidian]

    output = {
        "query": args.query,
        "timestamp": datetime.now().isoformat(),
        "results": {}
    }

    for search_fn in sources:
        result = search_fn(args.query, args.max)
        output["results"][result["source"]] = result

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
