#!/usr/bin/env python3
"""
PyPI Wheel Download Bypass — for network-constrained environments.

When `uv pip install` or `pip install` repeatedly times out on large packages,
download the wheel via Python's built-in urllib (which handles constrained
networks better than pip/uv in some environments), then install from local file.

Usage:
    python pip-wheel-bypass.py <package-name> [--target-dir DIR]
"""

import json, urllib.request, subprocess, sys, os, argparse

def main():
    parser = argparse.ArgumentParser(description='Download wheel from PyPI and install locally')
    parser.add_argument('package', help='Package name (e.g. "xhs-cli", "hindsight-all")')
    parser.add_argument('--python', help='Python executable to install into')
    parser.add_argument('--target-dir', default=os.path.expanduser('~/.hermes/downloads'),
                        help='Where to save the downloaded wheel')
    args = parser.parse_args()

    os.makedirs(args.target_dir, exist_ok=True)

    # 1. Get package metadata from PyPI JSON API
    url = f"https://pypi.org/pypi/{args.package}/json"
    print(f"Fetching {url}...")
    data = json.loads(urllib.request.urlopen(urllib.request.Request(url)).read())
    info = data['info']
    version = info['version']
    print(f"{args.package} v{version}")

    # 2. Find the wheel file (prefer none-any pure Python wheel)
    releases = data['releases'][version]
    wheel = None
    for r in releases:
        if r['filename'].endswith('.whl'):
            if 'none-any' in r['filename']:
                wheel = r
                break
            if wheel is None:
                wheel = r

    if not wheel:
        print(f"No wheel found for {args.package} v{version}")
        sys.exit(1)

    # 3. Download
    local_path = os.path.join(args.target_dir, wheel['filename'])
    print(f"Downloading {wheel['filename']} ({wheel['size']/1024:.0f}KB)...")
    urllib.request.urlretrieve(wheel['url'], local_path)
    print(f"Saved to {local_path}")

    # 4. Install
    if args.python:
        print("Installing...")
        r = subprocess.run(['uv', 'pip', 'install', '--python', args.python, local_path],
                          capture_output=True, text=True, timeout=120)
        if r.returncode == 0:
            print("✅ Installed successfully")
        else:
            print(f"❌ Install failed: {r.stderr[:200]}")
            sys.exit(1)

if __name__ == '__main__':
    main()
