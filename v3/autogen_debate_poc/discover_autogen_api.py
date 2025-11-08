#!/usr/bin/env python3
"""
Install and configure latest stable pyautogen.
Test the API to understand the correct usage.
"""
import subprocess
import sys

print("🔄 Installing latest stable pyautogen...")
print("=" * 60)

# Install latest stable
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-U", "pyautogen"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"❌ Installation failed: {result.stderr}")
    sys.exit(1)

print("✅ Installation complete\n")

# Check what was installed
print("=" * 60)
print("Checking installed packages...")
print("=" * 60)

result = subprocess.run(
    [sys.executable, "-m", "pip", "show", "pyautogen"],
    capture_output=True,
    text=True
)
print(result.stdout)

# Test imports and discover API
print("=" * 60)
print("Discovering AutoGen API...")
print("=" * 60)

try:
    # Try autogen-agentchat (new API)
    from autogen_agentchat import agents, teams, messages
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    
    print("✅ Using autogen-agentchat (new API)")
    print("\nAvailable in agents module:")
    agent_classes = [name for name in dir(agents) if not name.startswith('_')]
    for cls in agent_classes[:10]:  # Show first 10
        print(f"   - {cls}")
    
    print("\nAvailable in teams module:")
    team_classes = [name for name in dir(teams) if not name.startswith('_')]
    for cls in team_classes[:10]:
        print(f"   - {cls}")
    
    print("\n🎯 This is the NEW AutoGen API (0.7.x)")
    print("   Uses: model_client instead of llm_config")
    print("   Architecture: Agent teams with message passing")
    
except ImportError as e1:
    print(f"New API not available: {e1}")
    
    try:
        # Try classic autogen
        import autogen
        from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
        
        print("✅ Using classic autogen API")
        print(f"Version: {autogen.__version__}")
        print("\nAvailable classes:")
        print("   - AssistantAgent")
        print("   - UserProxyAgent")
        print("   - GroupChat")
        print("   - GroupChatManager")
        
        print("\n🎯 This is the CLASSIC AutoGen API")
        print("   Uses: llm_config with config_list")
        
    except ImportError as e2:
        print(f"❌ Classic API also not available: {e2}")
        sys.exit(1)

print("\n" + "=" * 60)
print("✅ AutoGen API discovery complete!")
print("=" * 60)
