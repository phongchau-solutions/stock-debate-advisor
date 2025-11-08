#!/usr/bin/env python3
"""Check what AutoGen packages are installed."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pip", "list"],
    capture_output=True,
    text=True
)

print("📦 Installed AutoGen-related packages:")
print("=" * 60)
for line in result.stdout.split('\n'):
    if 'autogen' in line.lower():
        print(f"  {line}")

print("\n" + "=" * 60)
print("Checking package details...")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "-m", "pip", "show", "pyautogen"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print(result.stdout)
else:
    print("❌ pyautogen not found")
    print("\nTrying to install explicitly...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-U", "pyautogen"])
