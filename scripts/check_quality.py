#!/usr/bin/env python3
"""
Code quality checker for AI Meme Video Agent
"""

import subprocess
import sys
from pathlib import Path


def check_quality():
    """Run all quality checks"""
    print("🔍 Running code quality checks...")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    checks = [
        (["black", "--check", "backend/", "tests/"], "Black formatting check"),
        (["isort", "--check-only", "backend/", "tests/"], "Import sorting check"),
        (["flake8", "backend/", "tests/"], "Code linting check"),
        (["mypy", "backend/"], "Type checking"),
    ]

    all_passed = True

    for cmd, description in checks:
        print(f"🔍 {description}...")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ {description} passed")
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed:")
            print(e.stdout)
            print(e.stderr)
            all_passed = False

    if all_passed:
        print("🎉 All quality checks passed!")
        return True
    else:
        print("💥 Some quality checks failed!")
        return False


if __name__ == "__main__":
    success = check_quality()
    sys.exit(0 if success else 1)
