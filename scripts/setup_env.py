#!/usr/bin/env python3
"""
Environment setup script for AI Meme Video Agent
"""

import os
import sys
from pathlib import Path


def setup_environment():
    """Set up environment for the project"""

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🚀 Setting up AI Meme Video Agent environment...")

    # Check if .env exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print("📝 Please copy .env.example to .env and fill in your values:")
        print("   cp .env.example .env")
        print("   # Then edit .env with your API keys")
        return False

    # Check required environment variables
    from dotenv import load_dotenv

    load_dotenv()

    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("📝 Please set these in your .env file")
        return False

    print("✅ Environment setup complete!")
    print("🔧 Configuration loaded successfully")
    print("🚀 Ready to run the application")

    return True


if __name__ == "__main__":
    success = setup_environment()
    sys.exit(0 if success else 1)
