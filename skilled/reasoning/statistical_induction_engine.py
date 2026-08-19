"""Inducción estadística auditable con árboles de decisión de scikit-learn.

Esta capacidad NO se presenta como inducción lógica simbólica. Aprende un
patrón predictivo desde ejemplos tabulares, reporta métricas de validación y
expone las reglas del árbol como evidencia inspeccionable.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

import numpy as np
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, export_text

from .engine_contracts import EngineResult, ReasoningCapability, ReasoningProfile


class StatisticalInductionEngineAdapter:
    name = "sklearn_tree_induction"
    capabilities: Sequence[ReasoningCapability] = (
        ReasoningCapability.STATISTICAL_INDUCTION,
    )
    priority = 50

    def _spec(self, problem: Any) -> Dict[str, Any]:
        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        return dict(indicators.get("statistical_induction_spec") or {})

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        spec = self._spec(problem)
        return profile.requires(ReasoningCapability.STATISTICAL_INDUCTION) and bool(
            spec.get("features") and spec.get("target") and spec.get("examples")
        )

    @staticmethod
    def _matrix(examples: list[Dict[str, Any]], features: list[str]) -> np.ndarray:
        rows = []
        for index, example in enumerate(examples):
            missing = [name for name in features if name not in example]
            if missing:
                raise ValueError(f"Example {index} is missing features: {missing}")
            try:
                rows.append([float(example[name]) for name in features])
            except (TypeError, ValueError) as exc:
                raise ValueError("Decision-tree features must be numeric") from exc
        return np.asarray(rows, dtype=float)

    def execute(
        self,
        problem: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        spec = self._spec(problem)
        try:
            features = [str(value) for value in spec.get("features", [])]
            target = str(spec.get("target") or "")
            examples = list(spec.get("examples") or [])
            task = str(spec.get("task") or "classification").lower()
            if not features:
                raise ValueError("statistical_induction_spec.features is required")
            if not target:
                raise ValueError("statistical_induction_spec.target is required")
            if len(examples) < 4:
                raise ValueError("At least 4 examples are required for statistical induction")
            if any(target not in example for example in examples):
                raise ValueError(f"All examples must contain target: {target}")
            if task not in {"classification", "regression"}:
                raise ValueError("task must be classification or regression")

            X = self._matrix(examples, features)
            y = np.asarray([example[target] for example in examples])
            random_state = int(spec.get("random_state", 42))
            max_depth_raw = spec.get("max_depth", 4)
            max_depth = None if max_depth_raw is None else int(max_depth_raw)
            test_size = float(spec.get("test_size", 0.25))
            if not 0 < test_size < 1:
                raise ValueError("test_size must be between 0 and 1")

            stratify = None
            if task == "classification":
                unique, counts = np.unique(y, return_counts=True)
                if len(unique) < 2:
                    raise ValueError("Classification requires at least two target classes")
                # Solo estratificar cuando cada clase tiene representación
                # suficiente para la partición.
                if counts.min() >= 2:
                    stratify = y

            X_train, X_test, y_train, y_test = train_test_split(
                X,
                y,
                test_size=test_size,
                random_state=random_state,
                stratify=stratify,
            )

            if task == "classification":
                model = DecisionTreeClassifier(
                    max_depth=max_depth,
                    random_state=random_state,
                )
            else:
                model = DecisionTreeRegressor(
                    max_depth=max_depth,
                    random_state=random_state,
                )
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            if task == "classification":
                metrics = {
                    "accuracy": float(accuracy_score(y_test, predictions)),
                }
                classes = [str(value) for value in getattr(model, "classes_", [])]
            else:
                metrics = {
                    "mean_absolute_error": float(mean_absolute_error(y_test, predictions)),
                    "r2": float(r2_score(y_test, predictions)) if len(y_test) >= 2 else None,
                }
                classes = []

            prediction_requests = list(spec.get("predict") or [])
            requested_predictions = []
            for index, row in enumerate(prediction_requests):
                missing = [name for name in features if name not in row]
                if missing:
                    raise ValueError(f"Prediction row {index} is missing features: {missing}")
                vector = np.asarray([[float(row[name]) for name in features]], dtype=float)
                value = model.predict(vector)[0]
                if hasattr(value, "item"):
                    value = value.item()
                requested_predictions.append(
                    {
                        "input": {name: row[name] for name in features},
                        "prediction": value,
                    }
                )

            rules = export_text(model, feature_names=features)
            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="success",
                data={
                    "task": task,
                    "features": features,
                    "target": target,
                    "training_examples": len(examples),
                    "train_examples": len(X_train),
                    "test_examples": len(X_test),
                    "metrics": metrics,
                    "classes": classes,
                    "tree_depth": int(model.get_depth()),
                    "leaf_count": int(model.get_n_leaves()),
                    "rules": rules,
                    "predictions": requested_predictions,
                },
                evidence={
                    "validation_metrics": metrics,
                    "learned_rules": rules,
                },
                validation={
                    "valid": True,
                    "holdout_evaluated": True,
                    "test_examples": len(X_test),
                },
                warnings=[
                    "This is statistical induction from finite examples, not a logical proof."
                ],
                transfer_payload={
                    "statistical_predictions": requested_predictions,
                    "learned_tree_rules": rules,
                },
                deterministic=False,
            )
        except Exception as exc:
            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="formalization_error",
                formalization_errors=[str(exc)],
                validation={"valid": False},
                deterministic=False,
            )
