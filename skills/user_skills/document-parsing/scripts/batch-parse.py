#!/usr/bin/env python3
"""
batch-parse.py — Batch document parser using MinerU.

Usage:
    python batch-parse.py <input_dir> <output_dir> [--cpu] [--json]

Scans input_dir for supported files (.pdf, .png, .jpg, .jpeg, .bmp,
.tiff, .pptx, .docx, .xlsx), runs MinerU on each, deposits .md files
into output_dir, and prints a summary.

Supports:
  - GPU (auto): default, uses CUDA if available
  - CPU only: pass --cpu (maps to `-b pipeline`)
  - JSON output: pass --json (instead of Markdown)

Model download happens on first run — may take 5-15 min.
"""

import argparse
import glob
import os
import subprocess
import sys
import time

SUPPORTED_EXTENSIONS = {
    ".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff",
    ".pptx", ".docx", ".xlsx",
}
COPY_EXTENSIONS = {".md", ".txt", ".json", ".canvas"}


def find_mineru():
    """Locate the mineru CLI."""
    # Check Hermes bundled Python first
    scripts = os.path.expanduser(
        "~/.hermes-web-ui/desktop-runtime/hermes/*/win-x64/python/Scripts"
    )
    matches = sorted(glob.glob(scripts))
    if matches:
        candidate = os.path.join(matches[-1], "mineru.exe")
        if os.path.exists(candidate):
            return candidate
        candidate = os.path.join(matches[-1], "mineru")
        if os.path.exists(candidate):
            return candidate
    # Fall back to PATH
    return "mineru"


def parse_file(mineru_bin, input_path, output_dir, cpu, json_output):
    """Parse a single file. Returns True on success."""
    os.makedirs(output_dir, exist_ok=True)
    cmd = [mineru_bin, "-p", input_path, "-o", output_dir]
    if cpu:
        cmd += ["-b", "pipeline"]
    if json_output:
        cmd += ["--json"]

    print(f"  Parsing {os.path.basename(input_path)}...", end=" ", flush=True)
    t0 = time.time()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=900  # 15 min for first-run model download
        )
        elapsed = time.time() - t0
        if result.returncode == 0:
            print(f"OK ({elapsed:.1f}s)")
            return True
        else:
            stderr = result.stderr[-300:] if result.stderr else ""
            print(f"FAILED ({elapsed:.1f}s): {stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT (>900s)")
        return False
    except FileNotFoundError:
        print(f"mineru not found — install with: pip install 'mineru[all]'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Batch parse documents using MinerU"
    )
    parser.add_argument("input_dir", help="Directory containing source files")
    parser.add_argument("output_dir", help="Directory for parsed output")
    parser.add_argument("--cpu", action="store_true",
                        help="Use CPU-only backend (-b pipeline)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of Markdown")
    args = parser.parse_args()

    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir)

    if not os.path.isdir(input_dir):
        print(f"Error: input_dir '{input_dir}' does not exist")
        sys.exit(1)

    mineru = find_mineru()
    print(f"MinerU: {mineru}")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print(f"CPU:    {'yes' if args.cpu else 'no (GPU auto)'}")
    print()

    # Gather files
    parse_targets = []
    copy_targets = []
    skipped = []

    for fname in sorted(os.listdir(input_dir)):
        fpath = os.path.join(input_dir, fname)
        if not os.path.isfile(fpath):
            continue
        ext = os.path.splitext(fname)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            parse_targets.append(fpath)
        elif ext in COPY_EXTENSIONS:
            copy_targets.append(fpath)
        else:
            skipped.append(fname)

    # Phase 1: Copy already-text files
    if copy_targets:
        print(f"Copying {len(copy_targets)} text files...")
        for fpath in copy_targets:
            dest = os.path.join(output_dir, os.path.basename(fpath))
            with open(fpath, "rb") as src, open(dest, "wb") as dst:
                dst.write(src.read())
            print(f"  Copied {os.path.basename(fpath)}")

    # Phase 2: Parse documents
    successes = []
    failures = []

    if parse_targets:
        print(f"\nParsing {len(parse_targets)} documents...")
        for fpath in parse_targets:
            ok = parse_file(mineru, fpath, output_dir, args.cpu, args.json)
            if ok:
                successes.append(os.path.basename(fpath))
            else:
                failures.append(os.path.basename(fpath))
    else:
        print("No documents to parse.")

    # Summary
    print("\n" + "=" * 50)
    print(f"Summary:")
    print(f"  Parsed OK:     {len(successes)}")
    print(f"  Failed:        {len(failures)}")
    print(f"  Copied (text): {len(copy_targets)}")
    print(f"  Skipped:       {len(skipped)}")
    if failures:
        print(f"\nFailed files:")
        for f in failures:
            print(f"  - {f}")
    if skipped:
        print(f"\nUnsupported files (skipped):")
        for f in skipped:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
