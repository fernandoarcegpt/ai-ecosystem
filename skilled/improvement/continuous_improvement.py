"""Evidence-driven continuous improvement coordinator."""

from __future__ import annotations

import hashlib
from collections import Counter
from typing import Any, Dict, Iterable, List


class ContinuousImprovementAgent:
    """Turn repeated runtime evidence into bounded improvement proposals."""

    def __init__(self, repetition_threshold: int = 2):
        if repetition_threshold < 1:
            raise ValueError("repetition_threshold must be positive")
        self.repetition_threshold = repetition_threshold

    @staticmethod
    def _proposal_id(kind: str, subject: str) -> str:
        digest = hashlib.sha256(f"{kind}:{subject}".encode()).hexdigest()[:10]
        return f"improvement-{digest}"

    def analyze_task_reports(
        self,
        reports: Iterable[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        block_categories: Counter[str] = Counter()
        failed_count = 0
        evidence: Dict[str, List[str]] = {}

        for report in reports:
            failed_count += int(
                report.get("status_distribution", {}).get("failed", 0)
            )
            for block in report.get("human_blocks", []):
                category = str(block.get("category", "unknown"))
                block_categories[category] += 1
                evidence.setdefault(category, []).extend(block.get("evidence", []))

        proposals: List[Dict[str, Any]] = []
        for category, count in sorted(block_categories.items()):
            if count < self.repetition_threshold:
                continue
            proposals.append(
                {
                    "id": self._proposal_id("block", category),
                    "kind": "repeated_block",
                    "subject": category,
                    "occurrences": count,
                    "evidence": list(dict.fromkeys(evidence.get(category, []))),
                    "recommended_action": (
                        f"Crear o reparar el ejecutor/proceso para bloqueos {category}"
                    ),
                    "risk": "low",
                    "automatic_action": "create_verified_improvement_task",
                    "success_metric": f"reducir bloqueos {category}",
                }
            )

        if failed_count >= self.repetition_threshold:
            proposals.append(
                {
                    "id": self._proposal_id("failure", "task-verification"),
                    "kind": "repeated_failure",
                    "subject": "task-verification",
                    "occurrences": failed_count,
                    "evidence": [f"{failed_count} tareas fallidas"],
                    "recommended_action": (
                        "Agregar una prueba de regresión para la causa dominante"
                    ),
                    "risk": "low",
                    "automatic_action": "create_verified_improvement_task",
                    "success_metric": "reducir tareas failed sin aumentar bloqueos",
                }
            )
        return proposals

    @staticmethod
    def evaluate_change(
        before: Dict[str, float],
        after: Dict[str, float],
        *,
        higher_is_better: Iterable[str] = (),
    ) -> Dict[str, Any]:
        positive = set(higher_is_better)
        deltas: Dict[str, float] = {}
        regressions: List[str] = []
        improvements: List[str] = []
        for metric in sorted(set(before) & set(after)):
            delta = float(after[metric]) - float(before[metric])
            deltas[metric] = delta
            improved = delta > 0 if metric in positive else delta < 0
            regressed = delta < 0 if metric in positive else delta > 0
            if improved:
                improvements.append(metric)
            elif regressed:
                regressions.append(metric)
        return {
            "accepted": bool(improvements) and not regressions,
            "deltas": deltas,
            "improvements": improvements,
            "regressions": regressions,
        }
