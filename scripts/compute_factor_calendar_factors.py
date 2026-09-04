#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from factor_calendar_runtime.runtime import run_factor_compute


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute raw Factor Calendar values from a long-form point-in-time "
            "market and fundamental panel."
        )
    )
    parser.add_argument("--input", required=True, help="Path to input JSON.")
    parser.add_argument(
        "--output",
        help="Optional output directory override.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = run_factor_compute(args.input, output_dir=args.output)
    except Exception as exc:
        print(
            json.dumps(
                {"ok": False, "error": str(exc)},
                ensure_ascii=False,
                indent=2,
            ),
            flush=True,
        )
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
