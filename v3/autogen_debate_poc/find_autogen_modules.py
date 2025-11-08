#!/usr/bin/env python3
"""Find what AutoGen modules are actually available."""
import sys
import pkgutil

print("🔍 Searching for AutoGen modules...")
print("=" * 60)

# Find all installed packages
all_packages = {pkg.name for pkg in pkgutil.iter_modules()}

autogen_packages = sorted([pkg for pkg in all_packages if 'autogen' in pkg.lower()])

print("Found AutoGen-related packages:")
for pkg in autogen_packages:
    print(f"  ✅ {pkg}")

if not autogen_packages:
    print("  ❌ No AutoGen packages found")
    sys.exit(1)

# Try importing each one
print("\n" + "=" * 60)
print("Testing imports...")
print("=" * 60)

for pkg_name in autogen_packages:
    try:
        mod = __import__(pkg_name)
        print(f"\n✅ {pkg_name}")
        
        # Show submodules
        if hasattr(mod, '__path__'):
            submodules = [name for _, name, _ in pkgutil.iter_modules(mod.__path__)]
            if submodules:
                print(f"   Submodules: {', '.join(submodules[:5])}")
                
        # Show key attributes
        attrs = [name for name in dir(mod) if not name.startswith('_')]
        if attrs:
            print(f"   Key exports: {', '.join(attrs[:8])}")
            
    except Exception as e:
        print(f"❌ {pkg_name}: {e}")

print("\n" + "=" * 60)
print("Let's check autogen_agentchat specifically...")
print("=" * 60)

try:
    import autogen_agentchat
    print(f"✅ autogen_agentchat imported")
    print(f"   Version: {autogen_agentchat.__version__ if hasattr(autogen_agentchat, '__version__') else 'unknown'}")
    
    # Check for agents
    if hasattr(autogen_agentchat, 'agents'):
        print("\n   agents module available:")
        from autogen_agentchat import agents
        agent_items = [name for name in dir(agents) if not name.startswith('_') and name[0].isupper()]
        for item in agent_items[:10]:
            print(f"      - {item}")
    
    # Check for teams
    if hasattr(autogen_agentchat, 'teams'):
        print("\n   teams module available:")
        from autogen_agentchat import teams
        team_items = [name for name in dir(teams) if not name.startswith('_') and name[0].isupper()]
        for item in team_items[:10]:
            print(f"      - {item}")
            
except ImportError as e:
    print(f"❌ Could not import autogen_agentchat: {e}")

print("\n" + "=" * 60)
print("✅ Module discovery complete")
print("=" * 60)
