"""Authorized evaluation-dataset builder with deterministic splits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


REQUIRED_FIELDS = {
    "id",
    "task",
    "input",
    "expected_output",
    "success_criteria",
    "provenance",
    "authorized",
}


class EvaluationDatasetBuilder:
    """Validate examples before they can enter train/validation/eval sets."""

    def __init__(self):
        self.examples: List[Dict[str, Any]] = []

    @staticmethod
    def _split(example_id: str) -> str:
        bucket = int(hashlib.sha256(example_id.encode()).hexdigest()[:8], 16) % 100
        if bucket < 80:
            return "train"
        if bucket < 90:
            return "validation"
        return "evaluation"

    def add(self, example: Dict[str, Any]) -> Dict[str, Any]:
        missing = REQUIRED_FIELDS - set(example)
        if missing:
            raise ValueError(f"Missing dataset fields: {sorted(missing)}")
        if example.get("authorized") is not True:
            raise ValueError("Dataset example is not authorized")
        if not example.get("success_criteria"):
            raise ValueError("success_criteria must not be empty")
        if any(item.get("id") == example["id"] for item in self.examples):
            raise ValueError(f"Duplicate example id: {example['id']}")
        normalized = dict(example)
        normalized["split"] = self._split(str(example["id"]))
        normalized.setdefault("expected_actions", [])
        normalized.setdefault("failure_modes", [])
        normalized.setdefault("edge_case", False)
        self.examples.append(normalized)
        return normalized

    def quality_report(self) -> Dict[str, Any]:
        splits = CounterLike(item["split"] for item in self.examples)
        return {
            "total": len(self.examples),
            "splits": dict(splits),
            "with_expected_actions": sum(
                bool(item.get("expected_actions")) for item in self.examples
            ),
            "edge_cases": sum(bool(item.get("edge_case")) for item in self.examples),
            "ready_for_comparative_evaluation": bool(
                splits.get("validation") and splits.get("evaluation")
            ),
        }

    def write_jsonl(self, output_dir: str) -> Dict[str, str]:
        destination = Path(output_dir).expanduser().resolve()
        destination.mkdir(parents=True, exist_ok=True)
        outputs: Dict[str, str] = {}
        for split in ("train", "validation", "evaluation"):
            target = destination / f"{split}.jsonl"
            lines = [
                json.dumps(item, ensure_ascii=False, sort_keys=True)
                for item in self.examples
                if item["split"] == split
            ]
            target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            outputs[split] = str(target)
        return outputs

    @staticmethod
    def recommend_fine_tuning(
        evaluations: Iterable[Dict[str, Any]],
        *,
        minimum_examples: int = 100,
        minimum_gain: float = 0.05,
    ) -> Dict[str, Any]:
        rows = list(evaluations)
        if len(rows) < minimum_examples:
            return {
                "recommended": False,
                "reason": "insufficient_evaluation_examples",
                "required": minimum_examples,
                "available": len(rows),
            }
        prompt_scores = [float(row["prompt_score"]) for row in rows]
        candidate_scores = [float(row["candidate_score"]) for row in rows]
        gain = sum(candidate_scores) / len(rows) - sum(prompt_scores) / len(rows)
        return {
            "recommended": gain >= minimum_gain,
            "reason": "measured_gain" if gain >= minimum_gain else "gain_too_small",
            "measured_gain": gain,
            "minimum_gain": minimum_gain,
        }


def CounterLike(values: Iterable[str]) -> Dict[str, int]:
    result: Dict[str, int] = {}
    for value in values:
        result[value] = result.get(value, 0) + 1
    return result
