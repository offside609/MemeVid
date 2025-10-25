#!/usr/bin/env python3
"""
Test runner script for AI Meme Video Agent
"""

import os
import subprocess
import sys
from pathlib import Path


def run_tests(test_type="all", verbose=True, coverage=True):
    """Run tests with specified options"""

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    print("🧪 Running AI Meme Video Agent Tests...")
    print(f"📁 Working directory: {project_root}")

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if verbose:
        cmd.append("-v")

    # Add coverage
    if coverage:
        cmd.extend(
            [
                "--cov=backend",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-report=xml:coverage.xml",
            ]
        )

    # Add test type filters
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "fast":
        cmd.extend(["-m", "not slow"])
    elif test_type == "agent":
        cmd.extend(["-m", "agent"])
    elif test_type == "api":
        cmd.extend(["-m", "api"])

    # Add test paths
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    else:
        cmd.append("tests/")

    print(f"🚀 Running command: {' '.join(cmd)}")

    # Run tests
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="Run AI Meme Video Agent tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "fast", "agent", "api"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument(
        "--no-verbose", action="store_true", help="Run without verbose output"
    )
    parser.add_argument(
        "--no-coverage", action="store_true", help="Run without coverage reporting"
    )

    args = parser.parse_args()

    success = run_tests(
        test_type=args.type, verbose=not args.no_verbose, coverage=not args.no_coverage
    )

    if success:
        print("\n🎉 Test run completed successfully!")
        if not args.no_coverage:
            print("📊 Coverage report generated in htmlcov/")
    else:
        print("\n💥 Test run failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
