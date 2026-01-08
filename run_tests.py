#!/usr/bin/env python3
"""
Test runner for PotterPi
Runs all unit and functional tests
"""

import sys
import subprocess


def run_tests(args=None):
    """
    Run pytest with specified arguments

    Args:
        args: List of additional pytest arguments
    """
    cmd = ["python3", "-m", "pytest"]

    if args:
        cmd.extend(args)
    else:
        # Default: run all tests with coverage
        cmd.extend([
            "tests/",
            "-v",
            "--tb=short"
        ])

    print("Running PotterPi Tests")
    print("=" * 50)
    print(f"Command: {' '.join(cmd)}")
    print("=" * 50)

    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point"""
    # Parse arguments
    args = sys.argv[1:] if len(sys.argv) > 1 else None

    # Run tests
    exit_code = run_tests(args)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
