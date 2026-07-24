import sys, subprocess

# Check torch
result = subprocess.run([sys.executable, "-c", "import torch; print(torch.__version__)"], capture_output=True, text=True, timeout=30)
print(f"torch check: exit={result.returncode}, out={result.stdout.strip()}, err={result.stderr[:100]}")

# Check gfpgan
result = subprocess.run([sys.executable, "-c", "import gfpgan; print(gfpgan.__file__)"], capture_output=True, text=True, timeout=30)
print(f"gfpgan check: exit={result.returncode}, out={result.stdout.strip()}, err={result.stderr[:100]}")

# Check basicsr
result = subprocess.run([sys.executable, "-c", "import basicsr; print(basicsr.__file__)"], capture_output=True, text=True, timeout=30)
print(f"basicsr check: exit={result.returncode}, out={result.stdout.strip()}, err={result.stderr[:100]}")
