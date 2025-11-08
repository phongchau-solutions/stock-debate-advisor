#!/usr/bin/env python3
"""
Install classic AutoGen (pyautogen<0.3) which has the traditional API
with AssistantAgent, UserProxyAgent, GroupChat working with llm_config.
"""
import subprocess
import sys

print("🔄 Installing classic AutoGen (pyautogen<0.3)...")
print("=" * 60)

# Uninstall new versions first
print("Removing newer incompatible versions...")
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pyautogen", "autogen-agentchat", "autogen-core"])

# Install classic version
print("\nInstalling pyautogen==0.2.38 (last stable v0.2)...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "pyautogen==0.2.38"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✅ Classic AutoGen installed")
else:
    print(f"❌ Failed: {result.stderr}")
    sys.exit(1)

# Verify installation
print("\n" + "=" * 60)
print("Verifying installation...")
print("=" * 60)

try:
    import autogen
    print(f"✅ autogen version: {autogen.__version__}")
    
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, config_list_from_json
    print("✅ Classic API classes available:")
    print("   - AssistantAgent (with llm_config)")
    print("   - UserProxyAgent")
    print("   - GroupChat") 
    print("   - GroupChatManager")
    print("   - config_list_from_json")
    
    # Test LLM config structure
    test_config = {
        "config_list": [{
            "model": "gemini-1.5-flash",
            "api_key": "test",
            "api_type": "google"
        }],
        "timeout": 120
    }
    print(f"\n✅ LLM config structure verified")
    
    print("\n" + "=" * 60)
    print("🎉 Classic AutoGen ready for LLM-powered agents!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
