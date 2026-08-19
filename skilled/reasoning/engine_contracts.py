"""Contratos extensibles para motores de razonamiento neurosimbólico.

Este módulo prepara el núcleo actual para incorporar nuevos motores sin cambiar
el comportamiento existente de NetworkX, PyDatalog y Z3. No ejecuta motores ni
reemplaza al ``NeurosymbolicCoordinator``; define contratos comunes que las
siguientes fases podrán adoptar de forma incremental.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Mapping, Optional, Protocol, Sequence, Tuple


class ReasoningCapability(str, Enum):
    """Capacidades ortogonales que puede requerir un problema formalizado."""

    GRAPH = "graph"
    LOGIC = "logic"
    CONSTRAINTS = "constraints"
    PLANNING = "planning"
    PROBABILISTIC = "probabilistic"
    CAUSAL = "causal"
    COUNTERFACTUAL = "counterfactual"
    ABDUCTIVE = "abductive"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    STATISTICAL_INDUCTION = "statistical_induction"
    ANALOGICAL = "analogical"


def _normalize_capability(value: ReasoningCapability | str) -> ReasoningCapability:
    if isinstance(value, ReasoningCapability):
        return value
    return ReasoningCapability(str(value))


_LEGACY_MODE_CAPABILITIES: Mapping[str, Tuple[ReasoningCapability, ...]] = {
    "none": (),
    "graphs": (ReasoningCapability.GRAPH,),
    "constraints": (ReasoningCapability.CONSTRAINTS,),
    "logic": (ReasoningCapability.LOGIC,),
}


@dataclass(frozen=True)
class ReasoningProfile:
    """Vista multi-capacidad derivada de un ``SymbolicProblem`` existente.

    ``legacy_mode`` conserva compatibilidad con ``ReasoningMode`` mientras el
    sistema migra gradualmente a selección por capacidades.
    """

    capabilities: Tuple[ReasoningCapability, ...]
    legacy_mode: str
    human_review: bool = False
    review_reason: Optional[str] = None

    @classmethod
    def from_problem(cls, problem: Any) -> "ReasoningProfile":
        mode = getattr(problem, "mode", "none")
        legacy_mode = str(getattr(mode, "value", mode or "none"))

        inferred: List[ReasoningCapability] = []
        if getattr(problem, "relations", None):
            inferred.append(ReasoningCapability.GRAPH)
        if getattr(problem, "facts", None) or getattr(problem, "rules", None):
            inferred.append(ReasoningCapability.LOGIC)
        if (
            getattr(problem, "constraints", None)
            or (getattr(problem, "items", None) and getattr(problem, "people", None))
        ):
            inferred.append(ReasoningCapability.CONSTRAINTS)

        # Compatibilidad para problemas construidos manualmente que todavía
        # dependen solo de ReasoningMode y no tienen estructura poblada.
        if not inferred:
            inferred.extend(_LEGACY_MODE_CAPABILITIES.get(legacy_mode, ()))

        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        declared = indicators.get("required_capabilities", ())
        if isinstance(declared, str):
            declared = [declared]
        for raw in declared or ():
            try:
                inferred.append(_normalize_capability(raw))
            except ValueError:
                # Una capacidad desconocida no debe activar un motor por error.
                continue

        capabilities = tuple(dict.fromkeys(inferred))
        return cls(
            capabilities=capabilities,
            legacy_mode=legacy_mode,
            human_review=bool(indicators.get("human_review")),
            review_reason=indicators.get("review_reason"),
        )

    def requires(self, capability: ReasoningCapability | str) -> bool:
        try:
            normalized = _normalize_capability(capability)
        except ValueError:
            return False
        return normalized in self.capabilities

    def to_dict(self) -> Dict[str, Any]:
        return {
            "capabilities": [capability.value for capability in self.capabilities],
            "legacy_mode": self.legacy_mode,
            "human_review": self.human_review,
            "review_reason": self.review_reason,
        }


@dataclass
class EngineResult:
    """Sobre común para resultados de cualquier motor formal verificable."""

    engine: str
    capabilities: Tuple[ReasoningCapability, ...]
    status: str
    data: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    formalization_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    transfer_payload: Dict[str, Any] = field(default_factory=dict)
    deterministic: Optional[bool] = True
    executed: bool = True

    @property
    def successful(self) -> bool:
        return self.status == "success" and not self.formalization_errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine": self.engine,
            "capabilities": [capability.value for capability in self.capabilities],
            "status": self.status,
            "data": self.data,
            "evidence": self.evidence,
            "validation": self.validation,
            "formalization_errors": list(self.formalization_errors),
            "warnings": list(self.warnings),
            "transfer_payload": self.transfer_payload,
            "deterministic": self.deterministic,
            "executed": self.executed,
        }


class EngineAdapter(Protocol):
    """Interfaz mínima que deberán implementar los adaptadores de motores."""

    name: str
    capabilities: Sequence[ReasoningCapability]
    priority: int

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        """Indicar si el motor puede ejecutar el problema formalizado."""
        ...

    def execute(self, problem: Any, context: Optional[Dict[str, Any]] = None) -> EngineResult:
        """Ejecutar el motor sin reinterpretar lenguaje natural."""
        ...


class EngineRegistry:
    """Registro determinista de adaptadores, sin ejecutar motores por sí mismo."""

    def __init__(self, adapters: Optional[Iterable[EngineAdapter]] = None):
        self._adapters: Dict[str, EngineAdapter] = {}
        for adapter in adapters or ():
            self.register(adapter)

    def register(self, adapter: EngineAdapter, *, replace: bool = False) -> None:
        name = str(adapter.name).strip()
        if not name:
            raise ValueError("Engine adapter name cannot be empty")
        if name in self._adapters and not replace:
            raise ValueError(f"Engine adapter already registered: {name}")
        self._adapters[name] = adapter

    def unregister(self, name: str) -> Optional[EngineAdapter]:
        return self._adapters.pop(name, None)

    def get(self, name: str) -> Optional[EngineAdapter]:
        return self._adapters.get(name)

    def names(self) -> Tuple[str, ...]:
        return tuple(self._adapters)

    def candidates_for(self, capability: ReasoningCapability | str) -> Tuple[EngineAdapter, ...]:
        normalized = _normalize_capability(capability)
        candidates = [
            adapter
            for adapter in self._adapters.values()
            if normalized in tuple(adapter.capabilities)
        ]
        return tuple(
            sorted(
                candidates,
                key=lambda adapter: (-int(getattr(adapter, "priority", 0)), adapter.name),
            )
        )

    def build_plan(
        self,
        profile: ReasoningProfile,
        problem: Any = None,
    ) -> Tuple[str, ...]:
        """Selecciona adaptadores que cubran las capacidades requeridas.

        Es deliberadamente simple: cubre primero el mayor número de capacidades
        pendientes y desempata por prioridad/nombre. La ejecución y transferencia
        entre motores siguen perteneciendo al coordinador actual.
        """

        remaining = set(profile.capabilities)
        selected: List[str] = []
        available = list(self._adapters.values())

        while remaining:
            ranked = []
            for adapter in available:
                supported = set(adapter.capabilities) & remaining
                if not supported:
                    continue
                if problem is not None and not adapter.can_handle(problem, profile):
                    continue
                ranked.append(
                    (
                        len(supported),
                        int(getattr(adapter, "priority", 0)),
                        adapter.name,
                        adapter,
                    )
                )

            if not ranked:
                missing = ", ".join(sorted(capability.value for capability in remaining))
                raise LookupError(f"No registered engine covers: {missing}")

            _, _, _, chosen = sorted(
                ranked,
                key=lambda item: (-item[0], -item[1], item[2]),
            )[0]
            selected.append(chosen.name)
            remaining -= set(chosen.capabilities)
            available = [adapter for adapter in available if adapter.name != chosen.name]

        return tuple(selected)
