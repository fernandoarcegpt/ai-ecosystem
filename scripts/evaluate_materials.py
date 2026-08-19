#!/usr/bin/env python3
"""Evaluate local books/materials and print a machine-readable report."""

from __future__ import annotations

import argparse
import json

from improvement.corpus_evaluator import CorpusEvaluator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--chunk-characters", type=int, default=12000)
    args = parser.parse_args()
    report = CorpusEvaluator(args.chunk_characters).evaluate(args.paths)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
