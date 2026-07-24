#!/usr/bin/env python3
"""文档解析流水线 — PDF/PPTX/DOCX/XLSX/图片批量转Markdown写入Obsidian。"""

import argparse, json, os, subprocess, sys, time
from pathlib import Path

OBSIDIAN_VAULT = Path(r"D:\Obsidian\Note")
DEFAULT_OUTPUT = OBSIDIAN_VAULT / "_parsed"
PYTHON = r"C:\Users\Admin\.hermes-web-ui\desktop-runtime\hermes\0.19.0\win-x64\python\python.exe"
SCRIPTS_DIR = Path(PYTHON).parent / "Scripts"
MINERU_EXE = SCRIPTS_DIR / "mineru.exe"

SUPPORTED_SUFFIXES = {
    ".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif",
    ".docx", ".pptx", ".xlsx",
}
MARKER_FILE = ".mineru_done"

def scan_directory(input_dir, recursive):
    files = []
    if recursive:
        for root, _, filenames in os.walk(input_dir):
            for f in filenames:
                path = Path(root) / f
                if path.suffix.lower() in SUPPORTED_SUFFIXES:
                    files.append(path)
    else:
        for f in os.listdir(input_dir):
            path = input_dir / f
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
                files.append(path)
    ext_order = {".txt":0,".md":0,".jpg":1,".jpeg":1,".png":1,".bmp":1,".tiff":1,".tif":1,".docx":2,".pptx":2,".xlsx":2,".pdf":3}
    files.sort(key=lambda p: (ext_order.get(p.suffix.lower(),9), p.name))
    return files

def is_already_processed(file_path, output_dir):
    marker = output_dir / f"{file_path.stem}{MARKER_FILE}"
    if marker.exists():
        with open(marker) as f:
            if f.read().strip() == str(file_path.stat().st_mtime):
                if (output_dir / f"{file_path.stem}.md").exists():
                    return True
    return False

def mark_as_processed(file_path, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    marker = output_dir / f"{file_path.stem}{MARKER_FILE}"
    with open(marker, 'w') as f:
        f.write(str(file_path.stat().st_mtime))

def parse_file(file_path, output_dir, backend, lang):
    print(f"  \U0001f504 \u89e3\u6790: {file_path.name} ...", end=" ", flush=True)
    file_out = output_dir / file_path.stem
    file_out.mkdir(parents=True, exist_ok=True)
    
    cmd = [str(MINERU_EXE), "-p", str(file_path.absolute()), "-o", str(file_out.absolute()), "-b", backend, "-l", lang]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
            env={**os.environ, "MINERU_MODEL_SOURCE": "modelscope"})
        if result.returncode == 0:
            md_files = list(file_out.glob("*.md"))
            if md_files:
                src = md_files[0]
                dst = output_dir / f"{file_path.stem}.md"
                with open(src, encoding='utf-8') as f:
                    content = f.read()
                with open(dst, 'w', encoding='utf-8') as f:
                    f.write(f"---\ntitle: {file_path.stem}\nsource: {file_path.name}\nparsed_by: MinerU\nparsed_at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n---\n\n{content}")
                print(f"\u2705 \u2192 {dst.name}")
                mark_as_processed(file_path, output_dir)
                return True
            else:
                print(f"\u26a0\ufe0f \u65e0MD\u8f93\u51fa")
                return False
        else:
            print(f"\u274c \u5931\u8d25")
            return False
    except subprocess.TimeoutExpired:
        print(f"\u23f0 \u8d85\u65f6")
        return False
    except Exception as e:
        print(f"\u274c \u5f02\u5e38: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="\u6587\u6863\u89e3\u6790\u6d41\u6c34\u7ebf \u2192 Obsidian")
    parser.add_argument("input_dir", type=Path, help="\u8f93\u5165\u76ee\u5f55")
    parser.add_argument("--output-dir", "-o", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--backend", "-b", default="hybrid-engine", choices=["pipeline","hybrid-engine"])
    parser.add_argument("--lang", "-l", default="ch")
    parser.add_argument("--recursive", "-r", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    if not MINERU_EXE.exists():
        print(f"\u274c MinerU\u672a\u5b89\u88c5: {MINERU_EXE}")
        sys.exit(1)
    if not args.input_dir.exists():
        print(f"\u274c \u8f93\u5165\u76ee\u5f55\u4e0d\u5b58\u5728: {args.input_dir}")
        sys.exit(1)
    
    print(f"\U0001f50d \u626b\u63cf\u76ee\u5f55: {args.input_dir}")
    files = scan_directory(args.input_dir, args.recursive)
    if not files:
        print("  \u6ca1\u6709\u53d1\u73b0\u652f\u6301\u7684\u6587\u4ef6")
        return
    print(f"  \u53d1\u73b0 {len(files)} \u4e2a\u6587\u4ef6:")
    by_type = {}
    for f in files:
        by_type.setdefault(f.suffix.lower(), []).append(f)
    for ext, flist in sorted(by_type.items()):
        print(f"    {ext}: {len(flist)} \u4e2a")
    if args.dry_run:
        print("\n\U0001f3c1 Dry-run \u5b8c\u6210")
        return
    
    args.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n\U0001f4e4 \u8f93\u51fa\u76ee\u5f55: {args.output_dir}")
    print(f"\u2699\ufe0f \u540e\u7aef: {args.backend}\n")
    
    success = failed = skipped = 0
    for file_path in files:
        if is_already_processed(file_path, args.output_dir):
            print(f"  \u23ed\ufe0f \u8df3\u8fc7: {file_path.name}")
            skipped += 1
            continue
        if parse_file(file_path, args.output_dir, args.backend, args.lang):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"\U0001f4ca \u6c47\u603b: \u603b\u8ba1={len(files)} \u2705={success} \u23ed\ufe0f={skipped} \u274c={failed}")
    print(f"  \u8f93\u51fa: {args.output_dir}")

if __name__ == "__main__":
    main()
