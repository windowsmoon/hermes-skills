---
name: document-parsing
description: >
  当用户需要从PDF/PPTX/DOCX/XLSX/图片中提取文本和结构化内容时使用。
  支持批量处理、Markdown输出、OCR识别、Obsidian集成。
  不要用于：网页内容提取（走web_extract）、纯图片OCR识别（走vision_analyze）、视频字幕提取。
  触发词：解析文档、读取PDF、提取文字、文档转Markdown、OCR识别
author: hermes-agent
version: "1.0.0"
tags:
  - ocr
  - document
  - pdf
  - parsing
  - mineru
  - paddleocr
  - markdown
triggers:
  - 解析文档
  - 读取PDF
  - 提取文字
  - 文档转Markdown
  - OCR识别

---

# Document Parsing

Convert complex documents (scanned PDFs, PPT slides, images, DOCX, XLSX) into structured Markdown or JSON. The agent automatically classifies files by extension, dispatches to the appropriate engine, and deposits results in a target directory (e.g., an Obsidian vault).

## MinerU 三种接入方式（本地/云端/MCP）

| 方式 | 命令/地址 | 费用 | 适合场景 |
|------|----------|------|---------|
| **CLI（本地）** | `mineru -p input -o output` | ✅ **完全免费，无限量** | 大文件、离线、不限页数 |
| **REST API（云端）** | `mineru.net/api/v4/extract/task` | ✅ 每天 1000 页免费 | 高精度 VLM 模型、批量处理 |
| **MCP Server（云端）** | `mcp.mineru.net/mcp` | ✅ 免费额度 | Agent 工作流原生集成 |

### 选择策略

| 场景 | 推荐方式 |
|------|---------|
| 文件 > 200MB 或 > 200 页 | CLI（本地，无限制） |
| 需要最高精度（VLM 模型） | REST API（云端算力更强） |
| 需要 Agent 自主调用 | MCP Server（MCP 协议原生接入） |
| 小文件快速处理（≤ 10MB/20 页） | Agent 轻量 API（免 Token，`/api/v1/agent/parse/url`） |
| 完全离线环境 | CLI（本地已装好） |

### 云端 API 使用

```python
import requests
token = "你的 MinerU Token"  # 从 https://mineru.net/apiManage 获取
url = "https://mineru.net/api/v4/extract/task"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "url": "https://cdn-mineru.openxlab.org.cn/demo/example.pdf",
    "model_version": "vlm"  # pipeline / vlm(推荐) / MinerU-HTML
}
resp = requests.post(url, headers=header, json=data)
print(resp.json())
```

### MCP 配置

```json
{
  "mcpServers": {
    "mineru": {
      "type": "streamableHttp",
      "url": "https://mcp.mineru.net/mcp",
      "env": { "MINERU_API_TOKEN": "your token" }
    }
  }
}
```

## Which Engine to Use

| Criterion | MinerU | PaddleOCR |
|-----------|--------|-----------|
| Stars | 74.9k ⭐ | 85.7k ⭐ |
| **Input formats** | PDF, images, **PPTX, DOCX, XLSX** ✅ | PDF, images |
| **Output format** | Markdown / JSON | Markdown / JSON / DOCX |
| CLI command | `mineru -p <input> -o <output>` | `paddleocr --image_dir=... --type=structure` |
| CPU mode | `-b pipeline` | Native CPU support |
| Framework | PyTorch (lighter) | PaddlePaddle (heavier) |
| **OCR quality** | Good (built-in VLM + pipeline) | Excellent (dedicated OCR engine) |
| Dependency size | ~2-3 GB (models auto-downloaded) | ~3-5 GB (incl. PaddlePaddle) |

**Recommendation**: Use **MinerU** as the primary engine. It handles more input formats natively, has a simpler CLI, and its PyTorch dependency plays better with the Hermes bundled Python environment. Fall back to PaddleOCR only when MinerU's OCR quality on a specific document is insufficient (rare — test first).

## Install MinerU

### Prerequisites

- Python 3.10+ (Hermes bundled Python 3.12 works)
- ~3GB free disk for model downloads (auto-downloaded on first run)
- Internet access to HuggingFace or ModelScope

### Installation

```bash
cd "$(dirname "$(python -c 'import sys;print(sys.executable)')")/.."

# Option A: uv (recommended with Hermes bundled Python)
uv pip install "mineru[all]"

# Option B: pip
pip install "mineru[all]"

# If in China / HuggingFace blocked, set model source before first run:
export MINERU_MODEL_SOURCE=modelscope
```

### Verify Installation

```bash
mineru --help
```

Expected output shows `-p` (input path) and `-o` (output dir) flags.

## CLI Usage

### Single file

```bash
# Auto-detect file type, output Markdown
mineru -p input.pdf -o output_dir/

# CPU-only mode (no GPU)
mineru -p input.pdf -o output_dir/ -b pipeline

# JSON output (instead of Markdown)
mineru -p input.pdf -o output_dir/ --json
```

### Batch directory

Mineru accepts a directory — it processes every supported file inside:

```bash
# Process all files in a directory
mineru -p /path/to/mixed/files/ -o /path/to/output/
```

### Supported input types (auto-detected by extension)

| Extension | Type | Notes |
|-----------|------|-------|
| `.pdf` | PDF | Scanned or digital. OCR auto-applied |
| `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff` | Images | Full page OCR |
| `.pptx` | PowerPoint | Extracts text + slide layout |
| `.docx` | Word | Extracts text + formatting |
| `.xlsx` | Excel | Extracts tables + text |

### Model download

Models are auto-downloaded from HuggingFace on first run (~2GB total). If downloads fail:

```bash
# Switch to ModelScope mirror (China users)
export MINERU_MODEL_SOURCE=modelscope

# Or pre-download models
mineru --download-models
```

## Obsidian Vault Integration

For direct import into `D:\Obsidian\Note\_parsed`:

- **Script**: `scripts/obsidian-import.py` — scans a directory, processes new/changed files, writes `.md` with metadata frontmatter, skips already-imported files via `.mineru_done` markers.
- **Reference**: `references/obsidian-import.md` — detailed workflow, manual import, force-reparse instructions.

```bash
# One-shot: process a directory into Obsidian
python scripts/obsidian-import.py D:\待处理文档 --cpu
```

## Agent Integration Pattern

See `scripts/batch-parse.py` for a generic runnable script, or `scripts/obsidian-import.py` for a version that deposits directly into an Obsidian vault.

### From execute_code

```python
import subprocess, os, json

def find_mineru():
    """Locate mineru CLI in Hermes bundled Python."""
    scripts = os.path.expanduser(
        "~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python/Scripts"
    )
    mineru = os.path.join(scripts, "mineru.exe")
    if os.path.exists(mineru):
        return mineru
    # Fall back to pip show
    result = subprocess.run(
        [sys.executable, "-m", "pip", "show", "mineru"],
        capture_output=True, text=True
    )
    return "mineru"  # hope it's on PATH

def parse_document(input_path, output_dir, backend="auto"):
    """Parse a single document to Markdown."""
    cmd = [mineru, "-p", input_path, "-o", output_dir]
    if backend == "cpu":
        cmd += ["-b", "pipeline"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return result.returncode == 0

def batch_parse(input_dir, output_dir, backend="auto"):
    """Parse all supported documents in a directory."""
    supported = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".pptx", ".docx", ".xlsx"}
    results = {"success": [], "failed": []}
    for fname in os.listdir(input_dir):
        ext = os.path.splitext(fname)[1].lower()
        if ext in supported:
            fpath = os.path.join(input_dir, fname)
            ok = parse_document(fpath, output_dir, backend)
            if ok:
                results["success"].append(fname)
            else:
                results["failed"].append(fname)
    return results
```

### Copy results to Obsidian

After parsing, each document creates an `.md` file in the output directory. Move or symlink these into the Obsidian vault:

```python
import shutil

obsidian_vault = "D:/Obsidian/Note/Inbox"
for md_file in glob.glob(f"{output_dir}/**/*.md", recursive=True):
    shutil.copy2(md_file, obsidian_vault)
```

## File Format Resolution Order

When the user says "process this directory for me":

```
1. Scan input_dir for all files
2. Group by extension:
   - .pdf, .png, .jpg, .jpeg, .bmp, .tiff → MinerU parse
   - .pptx, .docx, .xlsx              → MinerU parse
   - .md, .txt                         → copy directly (already text)
   - .canvas (Obsidian)                → copy directly
   - .json                             → copy directly
   - other                             → skip with warning
3. Run MinerU batch on all parseable files
4. Move/copy all resulting .md + .json into Obsidian vault
5. Report summary: N succeeded, M failed, K skipped
```

## Pitfalls

- **Reference**: MinerU 云端 API 详情 → `references/mineru-cloud-api.md`
- **Models download on first run**: MinerU downloads ~2GB of models from HuggingFace. First invocation may take 5-15 minutes on a slow connection. Do NOT abort mid-download — set a generous timeout (900s) for the first run.
- **HuggingFace blocked in China**: Set `export MINERU_MODEL_SOURCE=modelscope` before the first run to use the ModelScope mirror.
- **CPU mode is slow**: `-b pipeline` uses CPU-only OCR. A 10-page scanned PDF may take several minutes. GPU (CUDA) is ~10x faster.
- **MinerU in Hermes bundled Python**: If uv/pip can't find a compatible PyTorch wheel for `win-x64`, try `pip install torch --index-url https://download.pytorch.org/whl/cpu` first.
- **Terminal garbled output**: On Windows git-bash, use `execute_code` with `subprocess.run(capture_output=True, text=True)` instead of `terminal()` to avoid binary encoding issues.


## Token 配置

MinerU API Token 保存在 `~/.hermes/.env`（`MINERU_API_TOKEN`），不要硬编码在 SKILL.md 中。Token 来源：mineru.net → API 管理页面 → 创建 Token。

## 云端 API 使用流程（已验证）

### Agent 轻量 API（免 Token，即用）
```bash
# 上传文件解析（≤10MB，≤20页）
curl -X POST https://mineru.net/api/v1/agent/parse/file \
  -F "file=@document.pdf" -F "model_version=pipeline"

# URL 解析
curl -X POST https://mineru.net/api/v1/agent/parse/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/doc.pdf", "model_version": "pipeline"}'
```

### 精准解析 API（需 Token，已验证通过）
- 端点：`POST https://mineru.net/api/v4/extract/task`
- 查询：`GET https://mineru.net/api/v4/extract/task/{task_id}`
- 每日免费：1000 页（最高优先级）
- 模型：`pipeline`（默认）、`vlm`（推荐，精度最高）、`MinerU-HTML`
- 输出：ZIP 含 Markdown + JSON，可选导出 docx/html/latex
- 认证：Header `Authorization: Bearer {token}`
- 参数：`url`（必选，文件 URL）、`enable_table`、`enable_formula`、`language`、`page_ranges`、`extra_formats`、`is_ocr`
- 注意：不支持直接上传文件，需先上传到可访问 URL

### MCP Server（暂不可用）
- MinerU 提供 MCP Server，类型为 `streamableHttp`
- URL: `https://mcp.mineru.net/mcp`
- 认证：`MINERU_API_TOKEN` 环境变量
- **⚠️ 限制**：Hermes Studio 目前仅支持 `stdio` 类型 MCP Server，不原生支持 `streamableHttp`。尝试注册会因 npm 包不存在而超时。需等待 Hermes 更新或编写本地代理中转脚本。
- 替代方案：直接用 REST API（封装在 doc-parser-pipeline 脚本中）

## 三种模式快速选择

| 场景 | 推荐模式 | 备注 |
|------|---------|------|
| >200MB 或离线 | 本地 CLI（已装） | 无限制，GPU/CPU 皆可 |
| 需要最高精度（VLM） | 云端精准 API（Token 已配） | 已测试通过，1秒解析 |
| 小文件快速处理 | Agent 轻量 API（免 Token） | IP 限频，即用 |
| Agent 工作流原生集成 | MCP Server ⏳ | 等待 Hermes 支持 |
