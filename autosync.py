"""Compatibility entry point: run the reviewed, fail-closed PowerShell sync."""
import subprocess
import sys

if __name__ == "__main__":
    try:
        result = subprocess.run([
            r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "-NoProfile", "-NonInteractive", "-File",
            r"D:\hermes-data\task-maintenance\github-sync.ps1",
            *sys.argv[1:],
        ], timeout=600, check=False)
        sys.exit(result.returncode)
    except (OSError, subprocess.TimeoutExpired):
        print("Sync launcher failed or timed out; inspect the local sync log.")
        sys.exit(10)
