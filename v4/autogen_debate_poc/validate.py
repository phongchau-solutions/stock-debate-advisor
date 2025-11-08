#!/usr/bin/env python3
"""
Validation Script - Check v4 Gemini Debate PoC Setup

Run: python validate.py
"""
import os
import sys
import json
from pathlib import Path

def check_file_exists(path: str, description: str) -> bool:
    """Check if file exists."""
    exists = Path(path).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_module_imports() -> bool:
    """Check if required modules can be imported."""
    modules = {
        "sqlalchemy": "Database ORM",
        "requests": "HTTP client",
        "pandas": "Data processing",
        "dotenv": "Environment management",
    }
    
    print("\n📦 Checking Python Imports:")
    all_ok = True
    for module, desc in modules.items():
        try:
            __import__(module)
            print(f"✅ {module:<20} ({desc})")
        except ImportError:
            print(f"❌ {module:<20} ({desc}) - NOT INSTALLED")
            all_ok = False
    
    # Optional but important
    optional = {
        "google.generativeai": "Gemini API",
        "yfinance": "Stock data",
        "pandas_ta": "Technical indicators",
    }
    
    print("\n📦 Optional Modules:")
    for module, desc in optional.items():
        try:
            __import__(module)
            print(f"✅ {module:<30} ({desc})")
        except ImportError:
            print(f"⚠️  {module:<30} ({desc}) - optional")
    
    return all_ok

def check_environment() -> bool:
    """Check environment variables."""
    print("\n🔑 Environment Variables:")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        masked = gemini_key[:10] + "..." if len(gemini_key) > 10 else gemini_key
        print(f"✅ GEMINI_API_KEY: {masked}")
    else:
        print(f"⚠️  GEMINI_API_KEY: NOT SET (required for running debates)")
    
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        print(f"✅ DATABASE_URL: {db_url[:40]}..." if len(db_url) > 40 else f"✅ DATABASE_URL: {db_url}")
    else:
        print(f"ℹ️  DATABASE_URL: NOT SET (optional, falls back to SQLite)")
    
    return bool(gemini_key)

def check_project_structure() -> bool:
    """Check that all required files exist."""
    print("\n📁 Project Structure:")
    
    required_files = {
        "app.py": "Main application",
        "requirements.txt": "Dependencies",
        "Dockerfile": "Container definition",
        "docker-compose.yml": "Multi-service orchestration",
        "agents/base_agent.py": "Agent base class",
        "agents/fundamental_agent.py": "Fundamental analyst",
        "agents/technical_agent.py": "Technical analyst",
        "agents/sentiment_agent.py": "Sentiment analyst",
        "agents/moderator_agent.py": "Moderator",
        "agents/judge_agent.py": "Judge",
        "services/gemini_service.py": "Gemini LLM service",
        "services/data_service.py": "Data fetching service",
        "services/debate_orchestrator.py": "Debate orchestration",
        "db/models.py": "Database models",
        "prompts/fundamental.txt": "Fundamental prompt",
        "prompts/technical.txt": "Technical prompt",
        "prompts/sentiment.txt": "Sentiment prompt",
        "prompts/moderator.txt": "Moderator prompt",
        "prompts/judge.txt": "Judge prompt",
        "README.md": "User guide",
        "DEPLOYMENT.md": "Deployment guide",
        "PROJECT_SUMMARY.md": "Project overview",
    }
    
    all_exist = True
    for filepath, desc in required_files.items():
        exists = check_file_exists(filepath, desc)
        all_exist = all_exist and exists
    
    return all_exist

def check_syntax() -> bool:
    """Check Python file syntax."""
    print("\n🐍 Python Syntax Check:")
    
    python_files = [
        "app.py",
        "agents/base_agent.py",
        "agents/fundamental_agent.py",
        "agents/technical_agent.py",
        "agents/sentiment_agent.py",
        "agents/moderator_agent.py",
        "agents/judge_agent.py",
        "services/gemini_service.py",
        "services/data_service.py",
        "services/debate_orchestrator.py",
        "db/models.py",
    ]
    
    all_ok = True
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                compile(f.read(), filepath, 'exec')
            print(f"✅ {filepath}")
        except SyntaxError as e:
            print(f"❌ {filepath}: {e}")
            all_ok = False
        except FileNotFoundError:
            print(f"❌ {filepath}: NOT FOUND")
            all_ok = False
    
    return all_ok

def check_docker() -> bool:
    """Check Docker and docker-compose."""
    print("\n🐳 Docker Check:")
    
    # Check docker
    result = os.system("docker --version > /dev/null 2>&1")
    docker_ok = result == 0
    status = "✅" if docker_ok else "⚠️ "
    print(f"{status} Docker: {'installed' if docker_ok else 'NOT FOUND'}")
    
    # Check docker-compose
    result = os.system("docker-compose --version > /dev/null 2>&1 || docker compose version > /dev/null 2>&1")
    compose_ok = result == 0
    status = "✅" if compose_ok else "⚠️ "
    print(f"{status} Docker Compose: {'installed' if compose_ok else 'NOT FOUND'}")
    
    return docker_ok and compose_ok

def check_requirements() -> bool:
    """Parse and validate requirements.txt."""
    print("\n📋 Requirements.txt:")
    
    try:
        with open("requirements.txt", "r") as f:
            lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
        
        print(f"✅ Found {len(lines)} dependencies:")
        for line in lines[:5]:
            print(f"   - {line}")
        if len(lines) > 5:
            print(f"   ... and {len(lines) - 5} more")
        
        return len(lines) > 0
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

def main():
    """Run all validation checks."""
    print("=" * 70)
    print("v4 Gemini Multi-Agent Stock Debate PoC - Setup Validation")
    print("=" * 70)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Python Syntax", check_syntax),
        ("Python Imports", check_module_imports),
        ("Environment Variables", check_environment),
        ("Requirements.txt", check_requirements),
        ("Docker Setup", check_docker),
    ]
    
    results = {}
    for name, check_func in checks:
        print()
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ Error during {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    print()
    
    if passed == total:
        print("🎉 All checks passed! You're ready to run debates.")
        print("\nQuick start:")
        print("  1. Export API key: export GEMINI_API_KEY='your-key'")
        print("  2. Run debate: python app.py --stock VNM --rounds 3")
        print("  3. Check results: cat results.json")
        return 0
    elif passed >= total - 2:
        print("⚠️  Most checks passed. Some optional components are missing.")
        print("You can still run with reduced functionality.")
        print("\nTo fix:")
        print("  - Install missing modules: pip install -r requirements.txt")
        print("  - Set GEMINI_API_KEY: export GEMINI_API_KEY='your-key'")
        return 1
    else:
        print("❌ Critical issues detected. Please fix before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
