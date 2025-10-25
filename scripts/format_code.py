#!/usr/bin/env python3
"""
Code formatting script for AI Meme Video Agent
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stdout)
        print(e.stderr)
        return False

def main():
    """Format all code"""
    print("🎨 Formatting AI Meme Video Agent code...")
    
    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    commands = [
        (["black", "backend/", "tests/", "scripts/"], "Black formatting"),
        (["isort", "backend/", "tests/", "scripts/"], "Import sorting"),
        (["flake8", "backend/", "tests/"], "Code linting"),
        (["mypy", "backend/"], "Type checking")
    ]
    
    success = True
    for cmd in commands:
        if not run_command(cmd[0], cmd[1]):
            success = False
    
    if success:
        print("🎉 All code quality checks passed!")
    else:
        print("💥 Some code quality checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()