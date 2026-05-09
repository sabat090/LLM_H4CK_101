#!/usr/bin/env python3
"""CLI flag submission tool for PromptLabs."""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.flag_checker import check_flag


def main():
    parser = argparse.ArgumentParser(description="Submit a flag for validation")
    parser.add_argument("--lab", required=True, help="Lab ID (e.g. 01, 01-H, 02a)")
    parser.add_argument("--flag", required=True, help="The flag string: FLAG{...}")
    args = parser.parse_args()

    success, message = check_flag(args.lab, args.flag)
    if success:
        print(f"[PASS] {message}")
    else:
        print(f"[FAIL] {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
