# Obsidian Vault Import Pipeline

After MinerU parses documents into Markdown, import them into an Obsidian vault for RAG/LLM retrieval.

## Default Output Path

`D:\Obsidian\Note\_parsed\`

Each parsed document generates:
- `xxx.md` — Markdown with frontmatter (title, source, parsed_by, parsed_at)
- `xxx.mineru_done` — Marker file (mtime of source, to skip re-parsing unchanged files)

## One-Shot Import (agent-invoked)

Use the `obsidian-import.py` script for directory-level processing:

```bash
python scripts/obsidian-import.py D:\待处理文档 --cpu
```

The script:
1. Scans the input directory for supported files
2. Skips files already imported (based on `.mineru_done` marker + source mtime)
3. Calls `mineru.exe` on each new/changed file
4. Writes `.md` with YAML frontmatter to `_parsed/`
5. Reports summary

## Manual Import from batch-parse.py

After running `batch-parse.py`:

```python
import shutil, glob
obsidian_vault = "D:/Obsidian/Note/Inbox"
for md in glob.glob(f"{output_dir}/**/*.md", recursive=True):
    shutil.copy2(md, obsidian_vault)
```

## Repeated Runs

The `.mineru_done` marker uses the source file's `st_mtime`. If the source file is modified (e.g., you replace a scanned PDF with a higher-resolution version), the mtime changes and the script re-parses it on the next run.

To force re-parse of a specific file, delete its `.mineru_done` marker:

```bash
rm "D:\Obsidian\Note\_parsed\filename.mineru_done"
```

## Supported Formats and Limitations

| Format | MinerU Support | Notes |
|--------|---------------|-------|
| `.pdf` | Full | Scanned PDFs auto-OCR'd; digital PDFs text-extracted |
| `.pptx` | Full | Extracts slide text, preserves structure |
| `.docx` | Full | Extracts paragraphs, headings, tables |
| `.xlsx` | Full | Extracts cell contents per sheet |
| `.png/.jpg` | Full | Full-page OCR |
| `.bmp/.tiff` | Full | Full-page OCR |

Limitations:
- MinerU does NOT preserve complex PPT animations or slide transitions
- Excel formulas are read as computed values, not formula strings
- Handwritten text OCR quality varies by handwriting legibility
