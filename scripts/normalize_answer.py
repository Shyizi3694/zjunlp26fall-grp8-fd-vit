#!/usr/bin/env python3
"""Expose answer normalization helper for ad-hoc usage and validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

from fdvit.evaluation import normalize_answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("text", help="Text to normalize")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(normalize_answer(args.text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
