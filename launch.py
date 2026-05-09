"""PromptLabs — Interactive lab launcher."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

LABS = {
    "01": {
        "name": "System Prompt Leakage",
        "app_dir": "module-01-prompt-leakage/01-explore/lab/app",
        "port": 8001,
    },
    "01H": {
        "name": "System Prompt Leakage (Hardened)",
        "app_dir": "module-01-prompt-leakage/04-reflect/lab-hardened/app",
        "port": 8010,
    },
    "02": {
        "name": "Direct Prompt Injection",
        "app_dir": "module-02-direct-injection/01-explore/lab/app",
        "port": 8002,
    },
    "02H": {
        "name": "Direct Prompt Injection (Hardened)",
        "app_dir": "module-02-direct-injection/04-reflect/lab-hardened/app",
        "port": 8003,
    },
    "03": {
        "name": "Indirect Prompt Injection",
        "app_dir": "module-03-indirect-injection/01-explore/lab/app",
        "port": 8004,
    },
    "03H": {
        "name": "Indirect Prompt Injection (Hardened)",
        "app_dir": "module-03-indirect-injection/04-reflect/lab-hardened/app",
        "port": 8005,
    },
    "04": {
        "name": "SSRF via LLM Output",
        "app_dir": "module-04-ssrf-output/01-explore/lab/app",
        "port": 8006,
    },
    "04H": {
        "name": "SSRF via LLM Output (Hardened)",
        "app_dir": "module-04-ssrf-output/04-reflect/lab-hardened/app",
        "port": 8007,
    },
}


def show_menu() -> str:
    print("\n" + "=" * 55)
    print("  PromptLabs — LLM Security Training Labs")
    print("=" * 55)
    print()

    modules = [
        ("01", "02", "03", "04"),
    ]
    for key, lab in LABS.items():
        suffix = " (H)" if key.endswith("H") else "    "
        print(f"  [{key:>3}]  {lab['name']:<45} :{lab['port']}")

    print()
    print("  [q]   Quit")
    print()
    return input("  Select a lab: ").strip()


def launch(lab_key: str) -> None:
    lab = LABS.get(lab_key.upper())
    if lab is None:
        # Try appending H for --hard flag
        lab = LABS.get(lab_key.upper() + "H")
    if lab is None:
        print(f"Unknown lab: {lab_key}")
        print(f"Available: {', '.join(LABS.keys())}")
        sys.exit(1)

    model = os.getenv("LLM_MODEL", "qwen2.5:7b")
    provider = os.getenv("LLM_PROVIDER", "ollama")

    print(f"\n  Launching: {lab['name']}")
    print(f"  Provider:  {provider} / {model}")
    print(f"  URL:       http://127.0.0.1:{lab['port']}")
    print(f"  Press Ctrl+C to stop\n")

    env = os.environ.copy()
    env.setdefault("LLM_MODEL", model)
    env.setdefault("LLM_PROVIDER", provider)

    try:
        subprocess.run(
            [
                sys.executable, "-m", "uvicorn",
                "main:app",
                "--app-dir", lab["app_dir"],
                "--host", "127.0.0.1",
                "--port", str(lab["port"]),
            ],
            env=env,
        )
    except KeyboardInterrupt:
        print("\n  Lab stopped.")


def main():
    parser = argparse.ArgumentParser(description="PromptLabs launcher")
    parser.add_argument("--module", "-m", help="Module number (01, 02, 03, 04)")
    parser.add_argument("--hard", action="store_true", help="Launch hardened variant")
    parser.add_argument("--port", type=int, help="Override default port")
    args = parser.parse_args()

    if args.module:
        key = args.module.zfill(2)
        if args.hard:
            key += "H"
        if args.port:
            LABS[key.upper()]["port"] = args.port
        launch(key)
    else:
        while True:
            choice = show_menu()
            if choice.lower() == "q":
                break
            if choice.upper() in LABS:
                launch(choice)
            else:
                print(f"  Invalid choice: {choice}")


if __name__ == "__main__":
    main()
