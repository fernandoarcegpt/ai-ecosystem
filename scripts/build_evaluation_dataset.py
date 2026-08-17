#!/usr/bin/env python3
"""Build the repository-owned synthetic acceptance dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from improvement.dataset_builder import EvaluationDatasetBuilder


FAMILIES = [
    ("graph-cycle", "Detecta el ciclo A -> B -> C -> A", "networkx"),
    ("graph-dag", "Ordena A -> B -> C", "networkx"),
    ("constraint-unsat", "Resuelve x > 10 y x < 5", "z3"),
    ("constraint-sat", "Resuelve x + y = 10 con x >= 1", "z3"),
    ("logic-ancestor", "Ana es madre de Luis; Luis es padre de Marta", "pydatalog"),
    ("plain-chat", "Hola, ¿cómo estás?", "none"),
    ("implementation", "Implementar y verificar el cambio", "task-router"),
    ("human-block", "Ejecutar QA sin ejecutor", "human-gate"),
    ("memory", "Continúa el trabajo anterior", "memory"),
]


def build(output_dir: str) -> dict:
    builder = EvaluationDatasetBuilder()
    for repetition in range(1, 9):
        for family, prompt, expected in FAMILIES:
            identifier = f"{family}-{repetition:02d}"
            builder.add(
                {
                    "id": identifier,
                    "task": family,
                    "input": prompt,
                    "expected_output": {"route": expected},
                    "expected_actions": ["classify", "execute", "verify"],
                    "success_criteria": [f"route equals {expected}"],
                    "failure_modes": ["invented evidence", "unverified success"],
                    "provenance": {
                        "source": "repository-acceptance-cases",
                        "synthetic": True,
                    },
                    "authorized": True,
                    "edge_case": family in {"constraint-unsat", "human-block"},
                }
            )
    outputs = builder.write_jsonl(output_dir)
    report = builder.quality_report()
    manifest = {
        "schema_version": 1,
        "purpose": "routing and orchestration acceptance evaluation",
        "contains_user_data": False,
        "fine_tuning_authorized": False,
        "quality": report,
        "files": {key: Path(value).name for key, value in outputs.items()},
    }
    Path(output_dir, "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", nargs="?", default="datasets/evaluation")
    args = parser.parse_args()
    manifest = build(args.output_dir)
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    if not manifest["quality"]["ready_for_comparative_evaluation"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
