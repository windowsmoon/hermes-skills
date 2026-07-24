#!/usr/bin/env python3
"""
obsidian-import.py — Parse documents and import directly into Obsidian vault.

Usage:
    python obsidian-import.py <input_dir> [--cpu] [--lang LANG]

Scans input_dir for PDFs, images, PPTX, DOCX, XLSX, runs MinerU on each,
deposits .md files into D:\Obsidian\Note\_parsed\ with metadata frontmatter,
and skips already-processed files (tracked by .mineru_done markers).

Environment:
    MINERU_MODEL_SOURCE=modelscope  (set automatically for China users)
"""

import argparse, glob, json, os, subprocess, sys, time
from pathlib import Path

OBSIDIAN_VAULT = Path(r"D:\Obsidian\Note")
DEFAULT_OUTPUT = OBSIDIAN_VAULT / "_parsed"
SUPPORTED = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif",
             ".docx", ".pptx", ".xlsx"}
MARKER_EXT = ".mineru_done"


def find_mineru():
    scripts = os.path.expanduser(
        "~/.hermes-web-ui/desktop-runtime/hermes/*/win-x64/python/Scripts"
    )
    matches = sorted(glob.glob(scripts))
    if matches:
        for p in [os.path.join(matches[-1], "mineru.exe"),
                  os.path.join(matches[-1], "mineru")]:
            if os.path.exists(p):
                return p
    return "mineru"


def is_done(fpath, out_dir):
    marker = out_dir / f"{fpath.stem}{MARKER_EXT}"
    if marker.exists() and marker.read_text().strip() == str(fpath.stat().st_mtime):
        return (out_dir / f"{fpath.stem}.md").exists()
    return False


def mark_done(fpath, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{fpath.stem}{MARKER_EXT}").write_text(str(fpath.stat().st_mtime))


def scan(input_dir, recursive):
    files = []
    if recursive:
        for root, _, names in os.walk(input_dir):
            for n in names:
                p = Path(root) / n
                if p.suffix.lower() in SUPPORTED:
                    files.append(p)
    else:
        for n in os.listdir(input_dir):
            p = input_dir / n
            if p.is_file() and p.suffix.lower() in SUPPORTED:
                files.append(p)
    ext_order = {".pdf":3, ".pptx":2, ".docx":2, ".xlsx":2}
    files.sort(key=lambda p: (ext_order.get(p.suffix.lower(), 1), p.name))
    return files


def parse_one(mineru, fpath, out_dir, backend, lang):
    print(f"  Parsing {fpath.name}...", end=" ", flush=True)
    tmp = out_dir / fpath.stem
    tmp.mkdir(parents=True, exist_ok=True)
    cmd = [mineru, "-p", str(fpath.resolve()), "-o", str(tmp.resolve()),
           "-b", backend, "-l", lang]
    env = {**os.environ, "MINERU_MODEL_SOURCE": "modelscope"}
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, env=env)
        if r.returncode != 0:
            print(f"FAILED")
            return False
        mds = list(tmp.glob("*.md"))
        if not mds:
            print("no MD output")
            return False
        src = mds[0]
        dst = out_dir / f"{fpath.stem}.md"
        content = src.read_text(encoding="utf-8")
        with open(dst, "w", encoding="utf-8") as f:
            f.write(f"---\ntitle: {fpath.stem}\nsource: {fpath.name}\n"
                    f"parsed_by: MinerU\nparsed_at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n---\n\n{content}")
        mark_done(fpath, out_dir)
        print(f"OK → {dst.name}")
        return True
    except subprocess.TimeoutExpired:
        print("TIMEOUT"); return False
    except Exception as e:
        print(f"ERROR: {e}"); return False


def main():
    parser = argparse.ArgumentParser(description="Parse docs → Obsidian vault")
    parser.add_argument("input_dir", type=Path, help="Source directory")
    parser.add_argument("-o", "--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("-b", "--backend", default="hybrid-engine",
                        choices=["pipeline", "hybrid-engine"])
    parser.add_argument("-l", "--lang", default="ch")
    parser.add_argument("-r", "--recursive", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    mineru = find_mineru()
    if not (shutil.which(mineru) or os.path.exists(mineru)):
        print(f"MinerU not found at {mineru}"); sys.exit(1)
    if not args.input_dir.is_dir():
        print(f"Input not found: {args.input_dir}"); sys.exit(1)

    files = scan(args.input_dir, args.recursive)
    print(f"Found {len(files)} files in {args.input_dir}")
    by_type = {}
    for f in files:
        by_type.setdefault(f.suffix.lower(), []).append(f)
    for ext, lst in sorted(by_type.items()):
        print(f"  {ext}: {len(lst)}")
    if args.dry_run:
        return

    args.output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {args.output_dir}  Backend: {args.backend}\n")

    ok = fail = skip = 0
    for f in files:
        if is_done(f, args.output_dir):
            print(f"  SKIP (done): {f.name}"); skip += 1; continue
        if parse_one(mineru, f, args.output_dir, args.backend, args.lang):
            ok += 1
        else:
            fail += 1

    print(f"\n{'='*50}")
    print(f"Total={len(files)}  OK={ok}  Skip={skip}  Fail={fail}")
    print(f"Output: {args.output_dir}")


if __name__ == "__main__":
    import shutil
    main()
