# Hindsight Python Stdlib Fix (2026-07-22)

## Problem
Hindsight wasn't working because:
1. Hermes deleted old `0.18.0` runtime (original Hindsight install) to free disk space
2. Current `0.18.2` Python is stripped-down — missing `encodings`, `importlib`, `DLLs`
3. `hindsight-client` package was installed but Python couldn't import it

## Diagnosis

```python
# Run this to confirm the issue
import subprocess, os
py = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python/python.exe")
result = subprocess.run([py, "-c", "import hindsight_client"], capture_output=True, text=True)
# Expected: ModuleNotFoundError: No module named 'encodings'
```

## Working Fix

```python
import os, shutil, subprocess

py019 = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.19.0/win-x64/python")
py0182 = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.18.2/win-x64/python")

# Step 1: Copy stdlib from 0.19.0 to 0.18.2
shutil.copytree(os.path.join(py019, "Lib", "encodings"),
                os.path.join(py0182, "Lib", "encodings"))
shutil.copytree(os.path.join(py019, "DLLs"),
                os.path.join(py0182, "DLLs"))

# Step 2: Copy boot modules
for mod in ["_bootsubsearcher.py", "genericpath.py", "os.py", "posixpath.py", 
            "ntpath.py", "linecache.py", "functools.py", "reprlib.py"]:
    src = os.path.join(py019, "Lib", mod)
    dst = os.path.join(py0182, "Lib", mod)
    if os.path.isfile(src):
        shutil.copy2(src, dst)

# Step 3: Install hindsight-client in 0.19.0 Python
env = os.environ.copy()
env["PYTHONHOME"] = py019
subprocess.run([os.path.join(py019, "python.exe"), "-m", "pip", "install", "hindsight-client"],
    env=env, timeout=120)

# Step 4: Copy packages to 0.18.2
sp_019 = os.path.join(py019, "Lib", "site-packages")
sp_0182 = os.path.join(py0182, "Lib", "site-packages")
for pkg in ["hindsight_client", "hindsight_client_api", "aiohttp_retry"]:
    src = os.path.join(sp_019, pkg)
    dst = os.path.join(sp_0182, pkg)
    if os.path.isdir(src) and not os.path.isdir(dst):
        shutil.copytree(src, dst)
```

## Alternative: Use PYTHONHOME

```python
import os, subprocess
py019 = os.path.expanduser("~/.hermes-web-ui/desktop-runtime/hermes/0.19.0/win-x64/python/python.exe")
env = os.environ.copy()
env["PYTHONHOME"] = os.path.dirname(os.path.dirname(py019))
result = subprocess.run([py019, "-c", "import hindsight_client; print('OK')"], env=env)
```

## Key Lesson

**Always set `PYTHONHOME`** when running Python scripts via subprocess in Hermes environment. The `execute_code` sandbox doesn't inherit Hermes's internal `PYTHONHOME` setting, causing imports to fail even for correctly installed packages.
