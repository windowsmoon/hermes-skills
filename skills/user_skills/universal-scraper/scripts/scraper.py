"""
universal_scraper.py -- 5层兜底通用网页采集器

Layers:
  1. Firecrawl (API, 免浏览器, 最快)
  2. Hermes browser 内置 (截图+vision一站式)
  3. Tabbit Browser (登录态+反爬)
  4. Playwright MCP (复杂交互+PDF)
  5. computer-control-mcp (操作系统级兜底)

用法:
  python scraper.py <url> [--pages N] [--images] [--charts]

流程:
  Phase 0: 解析参数, 初始化状态
  Phase 1: Firecrawl 爬取
  Phase 2: 浏览器层 (Hermes->Tabbit->Playwright)
  Phase 3: computer-control OCR 兜底
  Phase 4: 去重 + 导出
"""
import sys, os, json, time, hashlib
from datetime import datetime

STATE_DIR = os.path.dirname(os.path.abspath(__file__))


def log(msg, level="INFO"):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{level}] {msg}")


# ═══════════════════════════════════════════════
# Phase 0: 参数解析 + 状态初始化
# ═══════════════════════════════════════════════

def parse_args():
    import argparse
    p = argparse.ArgumentParser(description="Universal Scraper")
    p.add_argument("url", help="目标URL")
    p.add_argument("--pages", type=int, default=1, help="翻页数,默认1")
    p.add_argument("--images", action="store_true", help="采集图片")
    p.add_argument("--charts", action="store_true", help="分析图表")
    p.add_argument("--output", default="", help="输出目录,默认桌面")
    return p.parse_args()


def init_state(url, pages, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    state = {
        "url": url,
        "max_pages": pages,
        "current_page": 0,
        "layer": 0,
        "status": "running",
        "records": [],
        "seen_hashes": {},
        "errors": [],
        "started_at": datetime.now().isoformat(),
        "output_dir": output_dir,
    }
    _save_state(state, output_dir)
    return state


def _save_state(state, output_dir):
    path = os.path.join(output_dir, "scrape-state.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════
# 工具: 去重 + 记录
# ═══════════════════════════════════════════════

def content_hash(text):
    return hashlib.md5(text.encode()[:200]).hexdigest()


def add_record(state, text, images=None, page_url=""):
    h = content_hash(text)
    if h in state["seen_hashes"]:
        return False
    state["records"].append({
        "page": state["current_page"],
        "url": page_url or state["url"],
        "text_preview": text[:200],
        "text_len": len(text),
        "images": images or [],
        "timestamp": datetime.now().isoformat(),
    })
    state["seen_hashes"][h] = True
    return True


def reached_end(state):
    if state["current_page"] >= state["max_pages"]:
        log(f"已达最大翻页数({state['max_pages']})")
        return True
    return False


# ═══════════════════════════════════════════════
# Phase 1: Firecrawl (API层)
# ═══════════════════════════════════════════════

def try_firecrawl(url, state):
    """尝试 Firecrawl 爬取. 返回True表示成功."""
    log(f"[Layer 1] 尝试 Firecrawl: {url}")
    state["layer"] = 1

    # Firecrawl 需要 API key,这里使用 hermes_config 中的 firecrawl API
    import subprocess
    hermes_python = ("C:/Users/Admin/.hermes-web-ui/desktop-runtime/"
                     "hermes/0.18.2/win-x64/python/python.exe")

    # 准备 Firecrawl 请求
    cmd = [
        hermes_python, "-c",
        f"""
import json, urllib.request, urllib.error
url = '{url}'
api_key = "fc-b2f...81f2"
try:
    req = urllib.request.Request(
        "https://api.firecrawl.dev/v1/scrape",
        data=json.dumps({{"url": url, "formats": ["markdown", "screenshot"]}}).encode(),
        headers={{"Content-Type": "application/json",
                  "Authorization": f"Bearer {{api_key}}"}},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read())
    if data.get("success"):
        result = data.get("data", {{}})
        md = result.get("markdown", "")
        imgs = result.get("metadata", {{}}).get("ogImage", "")
        print("SUCCESS:" + str(len(md)))
        print("IMAGES:" + imgs)
    else:
        print("FAIL:" + data.get("error", "unknown"))
except Exception as e:
    print("ERROR:" + str(e))
"""
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=30)
    output = result.stdout.strip()
    log(f"Firecrawl 返回: {output[:100]}")

    if output.startswith("SUCCESS:"):
        # 提取文本长度
        length = int(output.split("SUCCESS:")[1].split("\\n")[0])
        images = output.split("IMAGES:")[1].strip() if "IMAGES:" in output else ""
        log(f"Firecrawl 成功: {length} chars")
        add_record(state, f"[Firecrawl] (length={length})", [images] if images else [])
        return True
    else:
        log(f"Firecrawl 失败: {output[:100]}, 降级到 Layer 2")
        return False


# ═══════════════════════════════════════════════
# Phase 2: 浏览器层 (Hermes -> Tabbit -> Playwright)
# ═══════════════════════════════════════════════

def try_browser_layer(url, state, charts=False):
    """
    浏览器层: 先试 Hermes browser(最快), 不行再试 Tabbit/Playwright.
    这里是输出"指令"给 Agent 执行,因为 Agent 才有 browser_* 工具.
    """
    log(f"[Layer 2] 建议使用浏览器层: {url}")
    state["layer"] = 2

    # 生成 browser 操作指令文件
    outdir = state["output_dir"]
    vision_line = ""
    if charts:
        vision_line = "   browser_vision(question=\"分析此页面的图表内容\")\n"
    image_line = ""
    if charts:
        image_line = "- 需要分析图表内容 -> 使用 vision_analyze\n- 需要下载图片 -> 使用 browser_get_images 获取URL\n"
    instructions = f"""## Layer 2: 浏览器自动化

### 目标URL
{url}

### 尝试顺序
1. Hermes browser 内置 (最快, 有 vision)
   browser_navigate("{url}")
   browser_snapshot(full=true)
   browser_get_images() -- 如果需要图片
{vision_line}   翻页:
   while page < {max_pages}:
       browser_scroll(direction="down")
       browser_snapshot(full=true)
       page += 1

2. 如果 Hermes browser 遇到反爬/登录:
   使用 Tabbit Browser:
   tabbit_antidetect()
   tabbit_navigate(url="{url}")
   tabbit_screenshot()
   tabbit_extract(type="text")
   翻页循环

3. 如果 Tabbit 也受限:
   使用 Playwright MCP:
   playwright_navigate(url="{url}")
   playwright_screenshot()
   playwright_snapshot()
   翻页: playwright_click 翻页按钮

### 数据要求
{image_line}- 翻页 {max_pages} 页
- 去重,按 page 编号
- 结果写到 {outdir}/browser-output.md

### 数据格式 (每页一条)
## Page <number>
URL: <page_url>
Content: <extracted text or vision analysis>
Images: <image URLs>
---
"""

    inst_path = os.path.join(outdir, "browser-instructions.md")
    with open(inst_path, "w", encoding="utf-8") as f:
        f.write(instructions)

    log(f"浏览器指令已写入: {inst_path}")
    log("请 Agent 执行上述指令后, 将结果写到 browser-output.md")
    return True


# ═══════════════════════════════════════════════
# Phase 3: computer-control 兜底
# ═══════════════════════════════════════════════

def try_computer_control(url, state):
    """
    第三层: computer-control-mcp + OCR.
    生成指令让 Agent 执行.
    """
    log(f"[Layer 3] 建议使用 computer-control: {url}")
    state["layer"] = 3
    outdir = state["output_dir"]

    instructions = f"""## Layer 3: computer-control 操作系统级兜底

### 目标
在浏览器中打开 {url}, 使用 computer-control-mcp 采集内容.

### 操作步骤
1. 确保目标浏览器已打开到目标URL
2. 截图: computer-control screenshot --mode whole_screen --output {outdir}/page1.png
3. OCR提取: computer-control (内置RapidOCR自动运行)
4. vision分析: vision_analyze({outdir}/page1.png, question="提取页面中的所有文字和数值数据")
5. 翻页: computer-control type --text "PageDown"
        或 computer-control click --x <next_button_x> --y <next_button_y>
6. 重复直到 {state['max_pages']} 页或内容不变

### 输出
结果写到 {outdir}/ocr-output.md
每页一条记录, 包含 OCR 提取文字 + vision 分析的图表数据
"""

    inst_path = os.path.join(outdir, "computer-instructions.md")
    with open(inst_path, "w", encoding="utf-8") as f:
        f.write(instructions)

    log(f"computer-control 指令已写入: {inst_path}")
    return True


# ═══════════════════════════════════════════════
# Phase 4: 汇总输出
# ═══════════════════════════════════════════════

def generate_report(state):
    """生成最终报告"""
    outdir = state["output_dir"]
    layer_names = ["", "Firecrawl", "Browser", "computer-control"]

    report = f"""# Universal Scraper Report

## 概况
- 目标URL: {state['url']}
- 使用层: {layer_names[state['layer']]}
- 耗时: {state['started_at']} - {datetime.now().isoformat()}
- 记录数: {len(state['records'])}
- 错误数: {len(state['errors'])}

## 记录摘要
"""
    for i, r in enumerate(state["records"]):
        report += f"""
### Record {i+1} (Page {r['page']})
- URL: {r['url']}
- 长度: {r['text_len']} chars
- 预览: {r['text_preview'][:100]}
- 图片: {len(r['images'])}张
"""

    if state["errors"]:
        report += "\n## 异常记录\n"
        for e in state["errors"]:
            report += f"- {e}\\n"

    report_path = os.path.join(outdir, "final-report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    log(f"报告已生成: {report_path}")
    return report_path


# ═══════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════

def main():
    args = parse_args()
    url = args.url

    # 输出目录
    domain = url.split("//")[-1].split("/")[0].replace("www.", "")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = args.output or os.path.join(
        os.path.expanduser("~/Desktop"), f"scraped_{domain}_{ts}"
    )

    state = init_state(url, args.pages, output_dir)
    log(f"目标: {url}")
    log(f"翻页: {args.pages}页")
    log(f"输出: {output_dir}")

    # Layer 1: Firecrawl
    if try_firecrawl(url, state):
        state["status"] = "completed"
        _save_state(state, output_dir)
        generate_report(state)
        return

    # Layer 2: Browser
    try_browser_layer(url, state, charts=args.charts)
    state["status"] = "needs_agent"
    _save_state(state, output_dir)
    log("浏览器层需要 Agent 手动执行指令, 完成后请重新运行确认")

    # Layer 2 完成后, 需要检查 browser-output.md 是否存在
    # 如果存在, 解析记录, 完成
    # 如果不存在或失败, 进入 Layer 3

    # (简化: Agent 执行完 Layer 2 后, 会调用 Layer 3 的逻辑)


if __name__ == "__main__":
    main()
