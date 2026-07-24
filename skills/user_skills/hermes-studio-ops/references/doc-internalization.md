# 文档本地内化 (Document Local Internalization)

A technique for making the agent understand Hermes documentation by reading it into context.

## When to Do It

- User provides Hermes Agent docs (llms-full.txt, Hermes Studio manuals, PDFs)
- User asks you to "文档内化" (internalize documentation)
- You need to understand Hermes capability boundaries to answer questions better

## The Workflow

### Step 1: Get the docs

**Preferred: fetch the canonical llms-full.txt**
```
https://hermes-agent.nousresearch.com/docs/llms-full.txt
```
This is the entire Hermes Agent documentation in a single file (~3.1MB / 66K lines). Always prefer this over partial docs.

**Fallback: read user-provided files**
- `.txt` files — use `read_file(path, limit=N)` with pagination
- `.docx` (Word) — `read_file` auto-extracts to readable text
- `.pdf` — `read_file` auto-extracts if text-based; scanned PDFs return error → request `.docx` conversion

### Step 2: Scan the structure

Don't read every word — scan headers to understand layout:

```python
# Scan TOC by extracting # / ## / ### header lines
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if line.startswith('# ') or line.startswith('## ') or line.startswith('### '):
        print(f"{i}: {line}")
```

### Step 3: Read key sections

Priority order for maximum capability gain:

1. **Memory Providers** → Hindsight, Honcho, etc.
2. **Skills System** → How to create/register skills
3. **Tools & Toolsets** → What tools are available
4. **Config API** → How to configure via REST
5. **Scheduled Tasks (Cron)** → Automation
6. **Profiles** → Multi-agent setup
7. **Kanban** → Task management
8. **Checkpoints** → Rollback capability
9. **Delegation** → Sub-agent architecture
10. **Context Files** → SOUL.md, AGENTS.md

### Step 4: Save the knowledge

Save to memory: which docs were read, where they're stored, key findings.

### Step 5: Apply

Use the knowledge to guide task execution. E.g., knowing Hindsight tools exist lets you use them instead of explaining they don't.

## Windows-Specific Gotchas

1. **`#` in filenames** — Read_file fails on `# Hermes Agent — Full Documentation.txt`. Fix: use Python `os.listdir()` + `open()` in `execute_code`.
2. **Shell encoding** — git-bash/MSYS garbles Chinese characters. Use `execute_code` Python scripts instead of `terminal` for reliable output.
3. **Long paths** — MSYS can't handle paths with spaces or special chars well. Use forward-slash `/c/Users/...` or raw `C:\\...` strings.
4. **文档版本滞后** — PDF 手册可能比实际安装版本旧。Hermes Studio v0.6.12 手册说"无工作流可视化UI"，但 v0.6.27 实际有。**检查实际 Web UI (`http://127.0.0.1:8748`) 比只看 PDF 文档更可靠。** 优先用 llms-full.txt（自动同步官方文档），PDF 仅作参考。搜索文档时用 `re.finditer` 在 execute_code 中精准定位章节。

## User-Facing Output

When reporting results, use:
- ✅ / ❌ / ⏳ status markers per item
- Table format for comparisons
- Concise "what's next" at the end
- Root cause + fix for failures, not verbose play-by-play
