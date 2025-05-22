#!/usr/bin/env python3
"""
Helper script to run tests with coverage.
"""
import os
import sys
import subprocess

def main():
    """Run tests with coverage."""
    print("Running tests with coverage...\n")

    # Run the tests with coverage
    result = subprocess.run(
        ["coverage", "run", "-m", "unittest", "discover", "-s", "tests"],
        check=False
    )

    if result.returncode != 0:
        print("\nTests failed!")
        sys.exit(result.returncode)

    # Generate the coverage report
    subprocess.run(["coverage", "report", "-m"], check=False)

if __name__ == "__main__":
    main() 