"""Contrato de salida fundamentada para el razonamiento neurosimbólico.

El LLM no debe reconstruir conclusiones desde el resultado crudo de los
motores. Este módulo convierte ese resultado en afirmaciones publicables con
alcance, soporte y una representación Markdown determinista.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Dict, Iterable, List, Optional


SCHEMA_VERSION = 1


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _stable_unique(values: Iterable[str]) -> List[str]:
    seen = set()
    output = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _fact_source(
    provenance: List[Dict[str, Any]],
    predicate: str,
    args: List[Any],
) -> Dict[str, Any]:
    """Encuentra el fragmento más específico que respalda un hecho fuente."""
    candidates = [
        item for item in provenance if item.get("kind") == "fact"
    ]
    strings = [str(arg) for arg in args if not isinstance(arg, (int, float))]
    numbers = [str(arg) for arg in args if isinstance(arg, (int, float))]
    for item in candidates:
        source_text = str(item.get("source_text", ""))
        if all(value.lower() in source_text.lower() for value in strings) and all(
            value in source_text for value in numbers
        ):
            return dict(item)
    return {"kind": "fact", "predicate": predicate}


def _engine_sections(result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    results = result.get("results", {}) or {}
    if result.get("engine_used") == "combined":
        return {
            "networkx": results.get("networkx_analysis") or {},
            "pydatalog": results.get("pydatalog_analysis") or {},
            "z3": results.get("z3_analysis") or {},
        }
    engine = str(result.get("engine_used", "none"))
    return {engine: results}


def _build_transfer_contract(
    result: Dict[str, Any],
    contract: Dict[str, Any],
) -> None:
    formalized = (
        result.get("analysis", {}).get("formalized_problem", {}) or {}
    )
    provenance = list(formalized.get("provenance", []))
    facts = list(formalized.get("facts", []))
    rules = list(formalized.get("rules", []))
    assumptions = list(formalized.get("assumptions", []))
    objectives = list(formalized.get("objectives", []))
    sections = _engine_sections(result)
    pd_result = sections.get("pydatalog", {})
    z3_result = sections.get("z3", {})
    support_index = contract["audit"].setdefault("support_index", {})

    ready: Dict[str, int] = {}
    source_fact_ids: Dict[tuple, str] = {}
    for index, raw_fact in enumerate(facts, start=1):
        if not isinstance(raw_fact, (list, tuple)) or not raw_fact:
            continue
        predicate = str(raw_fact[0])
        args = list(raw_fact[1:])
        fact_id = f"source_fact_{index}"
        fact = {
            "id": fact_id,
            "predicate": predicate,
            "args": args,
            "source": _fact_source(provenance, predicate, args),
        }
        contract["source_facts"].append(fact)
        support_index[fact_id] = fact
        source_fact_ids[tuple([predicate, *args])] = fact_id
        if predicate == "ready_boxes" and len(args) == 2:
            ready[str(args[0])] = int(args[1])

    units = list(ready)
    if not units:
        units = [
            str(spec.get("entity"))
            for name, spec in formalized.get("variables", {}).items()
            if name.startswith("receive_")
            and isinstance(spec, dict)
            and spec.get("entity")
        ]
    contract["scope"] = {
        "type": "explicit_entities",
        "entities": _stable_unique(units),
        "statement": (
            f"El resultado se limita a las {len(_stable_unique(units))} "
            "unidades formalizadas en el mensaje."
        ),
    }
    contract["assumptions"] = assumptions
    contract["objectives"] = objectives
    for assumption in assumptions:
        assumption_id = assumption.get("id")
        if assumption_id:
            support_index[f"assumption:{assumption_id}"] = assumption
    for objective in objectives:
        if objective.get("type") == "maximize_count":
            support_index["objective:transfer_count"] = objective

    rule_sources = {
        str(rule.get("name")): rule.get("source", {})
        for rule in rules
        if isinstance(rule, dict)
    }
    for name, source in rule_sources.items():
        support_index[f"rule:{name}"] = source
    states: Dict[str, set] = {unit: set() for unit in units}
    derived_ids: Dict[tuple, str] = {}
    for index, derived in enumerate(pd_result.get("derived_facts", []), start=1):
        predicate = str(derived.get("predicate", ""))
        args = list(derived.get("args", []))
        if not predicate or not args:
            continue
        derived_id = f"derived_fact_{index}"
        item = {
            "id": derived_id,
            "predicate": predicate,
            "args": args,
            "binding": dict(derived.get("binding", {})),
        }
        contract["derived_facts"].append(item)
        unit = str(args[0])
        states.setdefault(unit, set()).add(predicate)
        derived_ids[(predicate, unit)] = derived_id
        support_index[derived_id] = item

        if predicate == "blocked":
            support = [
                source_fact_ids.get(("missing_final_inventory", unit), ""),
                "rule:blocked_from_missing_inventory",
                derived_id,
            ]
            statement = (
                f"{unit} queda bloqueada por falta del inventario definitivo."
            )
        elif predicate == "requires_correction":
            support = [
                source_fact_ids.get(("inventory_inconsistent", unit), ""),
                "rule:correction_from_inconsistent_inventory",
                derived_id,
            ]
            statement = (
                f"{unit} requiere corregir las inconsistencias del inventario."
            )
        elif predicate == "cannot_receive":
            if "blocked" in states.get(unit, set()):
                cause = derived_ids.get(("blocked", unit), "")
                rule_id = "rule:cannot_receive_blocked"
            else:
                cause = derived_ids.get(("requires_correction", unit), "")
                rule_id = "rule:cannot_receive_correction"
            support = [cause, rule_id, derived_id]
            statement = (
                f"{unit} no es recibible bajo las reglas formalizadas."
            )
        else:
            continue
        contract["claims"].append(
            {
                "id": f"claim_{len(contract['claims']) + 1}",
                "kind": "derived_fact",
                "statement": statement,
                "scope": [unit],
                "supported_by": [value for value in support if value],
            }
        )

    capacity_constraint = next(
        (
            item
            for item in formalized.get("constraints", [])
            if item.get("type") == "weighted_sum_le"
        ),
        {},
    )
    if capacity_constraint:
        support_index["constraint:capacity"] = capacity_constraint

    solution = z3_result.get("solution_values", {}) or {}
    support_index["z3:model"] = {
        "solution_status": z3_result.get("solution_status"),
        "solution_values": solution,
    }
    selected = []
    decisions = []
    for unit in units:
        slug = "".join(
            char for char in str(unit).replace(" ", "_")
            if char.isalnum() or char == "_"
        )
        # El extractor elimina tildes; localizar por la entidad evita duplicar
        # esa normalización aquí.
        variable = next(
            (
                name
                for name, spec in formalized.get("variables", {}).items()
                if isinstance(spec, dict) and spec.get("entity") == unit
            ),
            f"receive_{slug}",
        )
        value = _as_bool(solution.get(variable, False))
        decision_support = ["z3:model"]
        for support_id in (
            "constraint:capacity",
            "assumption:listed_impediments_complete_for_scope",
        ):
            if support_id in support_index:
                decision_support.append(support_id)
        if "objective:transfer_count" in support_index:
            decision_support.append("objective:transfer_count")
        decision = {
            "variable": variable,
            "entity": unit,
            "selected": value,
            "boxes": ready.get(unit),
            "supported_by": decision_support,
        }
        decisions.append(decision)
        if value:
            selected.append(unit)
            contract["claims"].append(
                {
                    "id": f"claim_{len(contract['claims']) + 1}",
                    "kind": "solver_decision",
                    "statement": (
                        f"{unit} fue seleccionada por el optimizador dentro "
                        "del alcance y los supuestos formalizados."
                    ),
                    "scope": [unit],
                    "supported_by": decision["supported_by"],
                }
            )
    contract["solver_decisions"] = decisions

    selected_boxes = sum(ready.get(unit, 0) for unit in selected)
    target = next(
        (
            int(objective["target"])
            for objective in objectives
            if objective.get("type") == "maximize_count"
            and objective.get("target") is not None
        ),
        None,
    )
    limit = (capacity_constraint.get("value") or {}).get("limit")
    base_capacity = limit.get("base") if isinstance(limit, dict) else limit
    reorganization_used = _as_bool(solution.get("reorganize", False))
    effective_capacity = base_capacity
    if isinstance(limit, dict) and reorganization_used:
        effective_capacity = int(limit.get("base", 0)) + int(
            limit.get("conditional_gain", 0)
        )

    contract["summary"] = {
        "modeled_units": len(units),
        "selected_units": selected,
        "selected_count": len(selected),
        "selected_boxes": selected_boxes,
        "base_capacity": base_capacity,
        "effective_capacity": effective_capacity,
        "reorganization_used": reorganization_used,
        "target_transfer_count": target,
        "gap_to_target": max(target - len(selected), 0) if target is not None else None,
    }
    contract["claims"].append(
        {
            "id": f"claim_{len(contract['claims']) + 1}",
            "kind": "solver_summary",
            "statement": (
                f"El optimizador seleccionó {len(selected)} de las {len(units)} "
                f"unidades modeladas, por un total de {selected_boxes} cajas."
            ),
            "scope": units,
            "supported_by": [
                support_id
                for support_id in ("z3:model", "constraint:capacity")
                if support_id in support_index
            ],
        }
    )
    if target is not None:
        contract["claims"].append(
            {
                "id": f"claim_{len(contract['claims']) + 1}",
                "kind": "objective_comparison",
                "statement": (
                    f"Dentro de este alcance, la solución queda "
                    f"{max(target - len(selected), 0)} por debajo de la meta "
                    f"institucional de {target} transferencias."
                ),
                "scope": units,
                "supported_by": ["z3:model", "objective:transfer_count"],
            }
        )

    contract["not_determined"].extend(
        [
            {"field": "execution_timing", "reason": "not_present_in_input"},
            {"field": "responsible_party", "reason": "not_present_in_input"},
            {"field": "authorization_to_transfer", "reason": "not_present_in_input"},
        ]
    )
    contract["audit"]["rule_sources"] = rule_sources


def _build_generic_contract(
    result: Dict[str, Any],
    contract: Dict[str, Any],
) -> None:
    formalized = (
        result.get("analysis", {}).get("formalized_problem", {}) or {}
    )
    contract["scope"] = {
        "type": "formalized_problem",
        "entities": list(formalized.get("entities", [])),
        "statement": "El resultado se limita a la estructura formalizada.",
    }
    contract["assumptions"] = list(formalized.get("assumptions", []))
    contract["objectives"] = list(formalized.get("objectives", []))
    contract["not_determined"] = list(formalized.get("unknowns", []))
    sections = _engine_sections(result)
    support_index = contract["audit"].setdefault("support_index", {})

    nx_result = sections.get("networkx", {})
    if nx_result and nx_result.get("is_acyclic") is not None:
        support_index["networkx:analysis"] = {
            "status": nx_result.get("status"),
            "is_acyclic": nx_result.get("is_acyclic"),
            "cycles_found": nx_result.get("cycles_found", []),
            "topological_order": nx_result.get("topological_order"),
        }
        statement = (
            "El grafo formalizado es acíclico."
            if nx_result.get("is_acyclic")
            else f"El grafo contiene {len(nx_result.get('cycles_found', []))} ciclo(s)."
        )
        contract["claims"].append(
            {
                "id": "claim_1",
                "kind": "engine_result",
                "statement": statement,
                "scope": list(formalized.get("entities", [])),
                "supported_by": ["networkx:analysis"],
            }
        )

    pd_result = sections.get("pydatalog", {})
    for derived in pd_result.get("derived_facts", []):
        item = {
            "id": f"derived_fact_{len(contract['derived_facts']) + 1}",
            "predicate": derived.get("predicate"),
            "args": list(derived.get("args", [])),
        }
        contract["derived_facts"].append(item)
        support_index[item["id"]] = item
        support_index["pydatalog:inference"] = {
            "queries_executed": pd_result.get("queries_executed", []),
            "status": pd_result.get("status"),
        }
        contract["claims"].append(
            {
                "id": f"claim_{len(contract['claims']) + 1}",
                "kind": "derived_fact",
                "statement": f"Hecho derivado: {item['predicate']}{tuple(item['args'])}.",
                "scope": list(item["args"]),
                "supported_by": [item["id"], "pydatalog:inference"],
            }
        )

    z3_result = sections.get("z3", {})
    if z3_result and z3_result.get("solution_status") not in {None, "unknown"}:
        support_index["z3:model"] = {
            "status": z3_result.get("status"),
            "solution_status": z3_result.get("solution_status"),
            "solution_values": z3_result.get("solution_values", {}),
            "unsat_core": z3_result.get("unsat_core", []),
        }
        contract["solver_decisions"] = [
            {
                "solution_status": z3_result.get("solution_status"),
                "solution_values": z3_result.get("solution_values", {}),
                "supported_by": ["z3:model"],
            }
        ]
        contract["claims"].append(
            {
                "id": f"claim_{len(contract['claims']) + 1}",
                "kind": "solver_result",
                "statement": (
                    "Z3 determinó que el conjunto formalizado es "
                    f"{z3_result.get('solution_status')}."
                ),
                "scope": list(formalized.get("entities", [])),
                "supported_by": ["z3:model"],
            }
        )


def render_grounded_markdown(contract: Dict[str, Any]) -> str:
    """Renderiza solo campos del contrato; no agrega recomendaciones."""
    status = contract.get("status")
    if status != "success":
        reason = contract.get("error") or contract.get("review_reason") or status
        return (
            "## Resultado neurosimbólico no concluyente\n\n"
            f"Estado: `{status}`. Motivo: {reason}.\n\n"
            "No se emitió una conclusión operativa determinista."
        )

    lines = ["## Resultado neurosimbólico determinista", ""]
    scope = contract.get("scope", {}) or {}
    if scope.get("statement"):
        lines.extend([f"**Alcance:** {scope['statement']}", ""])

    summary = contract.get("summary", {}) or {}
    if summary.get("modeled_units") is not None:
        lines.extend(["### Resultado del plan", ""])
        for decision in contract.get("solver_decisions", []):
            entity = decision.get("entity")
            boxes = decision.get("boxes")
            if not entity:
                continue
            if decision.get("selected"):
                state = "seleccionada por el optimizador"
            else:
                derived = {
                    item.get("predicate")
                    for item in contract.get("derived_facts", [])
                    if (item.get("args") or [None])[0] == entity
                }
                if "blocked" in derived:
                    state = "bloqueada por inventario definitivo faltante"
                elif "requires_correction" in derived:
                    state = "requiere corrección del inventario"
                else:
                    state = "no seleccionada"
            box_text = f" — {boxes} cajas" if boxes is not None else ""
            lines.append(f"- {entity}{box_text}: {state}.")
        lines.append("")
        lines.append(
            f"Se seleccionaron **{summary.get('selected_count', 0)} de "
            f"{summary.get('modeled_units', 0)} unidades**, con "
            f"**{summary.get('selected_boxes', 0)} cajas**."
        )
        if summary.get("effective_capacity") is not None:
            capacity_label = (
                "capacidad efectiva"
                if summary.get("reorganization_used")
                else "capacidad base"
            )
            lines.append(
                f"El volumen seleccionado queda dentro de la {capacity_label} "
                f"de **{summary['effective_capacity']} cajas**."
            )
        if summary.get("target_transfer_count") is not None:
            lines.append(
                f"Dentro de este alcance faltan **{summary.get('gap_to_target', 0)}** "
                f"para alcanzar la meta de {summary['target_transfer_count']} "
                "transferencias; esto no limita el universo institucional a "
                "las unidades analizadas."
            )
        lines.append("")
    else:
        lines.extend(["### Conclusiones respaldadas", ""])
        for claim in contract.get("claims", []):
            lines.append(f"- {claim.get('statement')}")
        lines.append("")

    assumptions = contract.get("assumptions", [])
    if assumptions:
        lines.extend(["### Supuestos explícitos", ""])
        for assumption in assumptions:
            lines.append(f"- {assumption.get('description', assumption)}")
        lines.append("")

    unknowns = contract.get("unknowns", [])
    not_determined = contract.get("not_determined", [])
    if unknowns or not_determined:
        labels = {
            "execution_timing": "el plazo o momento de ejecución",
            "responsible_party": "la persona o unidad responsable",
            "authorization_to_transfer": "la autorización para ejecutar la transferencia",
        }
        lines.extend(["### No determinado por la evidencia", ""])
        for item in unknowns:
            lines.append(f"- {item.get('description', item)}")
        for item in not_determined:
            field = item.get("field") if isinstance(item, dict) else str(item)
            lines.append(f"- {labels.get(field, field)}")
        lines.append("")

    lines.extend(
        [
            "La salida anterior describe factibilidad bajo el modelo; no "
            "equivale a una autorización ni fija ejecución inmediata.",
            "",
            f"`run_id: {contract.get('run_id')}`",
        ]
    )
    return "\n".join(lines).strip()


def build_grounded_contract(
    symbolic_result: Optional[Dict[str, Any]],
    *,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Construye el único contrato permitido para respuestas deterministas."""
    result = symbolic_result or {}
    run_id = run_id or uuid.uuid4().hex
    formalized = result.get("analysis", {}).get("formalized_problem", {}) or {}
    status = str(result.get("status", "skipped"))
    sections = _engine_sections(result) if result else {}
    contract: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "engine_used": result.get("engine_used", "none"),
        "scope": {},
        "source_facts": [],
        "derived_facts": [],
        "solver_decisions": [],
        "assumptions": [],
        "objectives": [],
        "unknowns": list(formalized.get("unknowns", [])),
        "not_determined": [],
        "claims": [],
        "engines": {
            name: data.get("status", "missing")
            for name, data in sections.items()
        },
        "audit": {
            "execution_time_seconds": result.get("execution_time"),
            "formalization_errors": list(result.get("formalization_errors", [])),
        },
        "error": result.get("error"),
    }
    indicators = formalized.get("structural_indicators", {}) or {}
    if status == "human_review" or indicators.get("human_review"):
        contract["review_reason"] = indicators.get(
            "review_reason",
            result.get("analysis", {}).get("review_reason", "human_review"),
        )
    elif status == "success":
        predicates = {
            str(fact[0])
            for fact in formalized.get("facts", [])
            if isinstance(fact, (list, tuple)) and fact
        }
        if "ready_boxes" in predicates:
            _build_transfer_contract(result, contract)
        else:
            _build_generic_contract(result, contract)

    support_index = contract["audit"].get("support_index", {})
    unresolved_support = sorted(
        {
            support_id
            for claim in contract.get("claims", [])
            for support_id in claim.get("supported_by", [])
            if support_id not in support_index
        }
    )
    contract["audit"]["unresolved_support"] = unresolved_support
    if status == "success" and unresolved_support:
        contract["status"] = "error"
        contract["error"] = "unresolved_claim_support"
        contract["claims"] = []

    hash_input = {
        key: value
        for key, value in contract.items()
        if key not in {"run_id", "audit"}
    }
    contract["audit"]["result_hash"] = hashlib.sha256(
        json.dumps(
            hash_input,
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        ).encode("utf-8")
    ).hexdigest()
    contract["rendered_markdown"] = render_grounded_markdown(contract)
    return contract
