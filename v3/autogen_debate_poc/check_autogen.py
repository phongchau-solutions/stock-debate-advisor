#!/usr/bin/env python3
"""
Check AutoGen installation and configuration.
This script verifies pyautogen is installed correctly.
"""
import sys
import subprocess

print("🔍 Checking AutoGen Setup")
print("=" * 60)

# Check Python version
print(f"Python version: {sys.version}")
if sys.version_info < (3, 11):
    print("⚠️  Warning: Python 3.11+ recommended for best compatibility")
else:
    print("✅ Python version compatible")

print("\n" + "=" * 60)
print("Installing pyautogen...")
print("=" * 60)

# Install pyautogen
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "pyautogen>=0.2.0"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ pyautogen installed successfully")
else:
    print(f"❌ Installation failed: {result.stderr}")
    sys.exit(1)

# Test import
print("\n" + "=" * 60)
print("Testing AutoGen imports...")
print("=" * 60)

try:
    import autogen
    print(f"✅ autogen version: {autogen.__version__}")
    
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    print("✅ Core classes imported:")
    print("   - AssistantAgent")
    print("   - UserProxyAgent")
    print("   - GroupChat")
    print("   - GroupChatManager")
    
    print("\n" + "=" * 60)
    print("🎉 AutoGen is ready for LLM-powered agents!")
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
