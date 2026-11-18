"""Pre-meeting check: loads the OKF bundle and asks one question both ways.

Run from the repository root:
    .venv/bin/python check_setup.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from dotenv import load_dotenv

from assistant import find_concepts, format_inr, get_answer, load_concepts, messages_with_okf, messages_without_okf

QUESTION = "What was our revenue in fiscal year 2026?"


def main() -> int:
    load_dotenv(Path(__file__).resolve().parent / ".env")
    concepts = load_concepts()
    print(f"[ok] Loaded {len(concepts)} OKF concepts from bundles/acme_retail")

    matches = find_concepts(QUESTION, concepts)
    print("[ok] Matching OKF files: " + ", ".join(c.relative_path for c in matches))

    try:
        for label, messages in [
            ("WITHOUT OKF", messages_without_okf(QUESTION)),
            ("WITH OKF", messages_with_okf(QUESTION, matches)),
        ]:
            answer = get_answer(messages)
            counted = [str(i) for i in answer.counted_ids]
            print(f"\n=== {label}: {format_inr(answer.total)}  (orders {', '.join(counted)})")
            print(answer.summary)
    except (RuntimeError, ValueError) as exc:
        print(f"[fail] DeepSeek call failed: {exc}")
        return 1
    print("\nExpected: about ₹1,200 without OKF (it guesses an April–March fiscal year) and ₹1,300 with OKF.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
