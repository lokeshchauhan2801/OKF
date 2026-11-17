"""Pre-meeting check: loads the OKF bundle and makes one real DeepSeek call.

Run from the repository root:
    .venv/bin/python demo/check_setup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from assistant import ask_deepseek, load_concepts, retrieve_concepts

ROOT = Path(__file__).resolve().parents[1]
QUESTION = "How is revenue calculated?"


def main() -> int:
    load_dotenv(ROOT / ".env")
    concepts = load_concepts(ROOT / "bundles" / "acme_retail")
    print(f"[ok] Loaded {len(concepts)} OKF concepts from bundles/acme_retail")

    matches = retrieve_concepts(QUESTION, concepts)
    print(f"[ok] Retrieved for {QUESTION!r}: " + ", ".join(c.relative_path for c in matches))

    try:
        answer = ask_deepseek(QUESTION, matches)
    except (RuntimeError, ValueError) as exc:
        print(f"[fail] DeepSeek call failed: {exc}")
        return 1
    print("[ok] DeepSeek answered:\n")
    print(answer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
