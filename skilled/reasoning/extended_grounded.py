"""Contrato fundamentado para resultados producidos por MetaReasoner."""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = 2


def _claim(statement: str, support_id: str, kind: str = "engine_result") -> Dict[str, Any]:
    return {
        "id": "",
        "kind": kind,
        "statement": statement,
        "scope": [],
        "supported_by": [support_id],
    }


def _engine_claims(name: str, envelope: Dict[str, Any], support_id: str) -> List[Dict[str, Any]]:
    data = dict(envelope.get("data") or {})
    claims: List[Dict[str, Any]] = []

    if name == "unified_planning":
        actions = list(data.get("actions") or [])
        if data.get("plan_found"):
            claims.append(_claim(f"Se encontró un plan clásico válido: {actions}.", support_id, "planning"))
        else:
            claims.append(_claim("No se encontró un plan clásico que alcance los objetivos formalizados.", support_id, "planning"))
    elif name == "z3_temporal":
        status = data.get("solution_status")
        claims.append(_claim(f"Las restricciones temporales son {status}.", support_id, "temporal"))
        if data.get("schedule"):
            claims.append(_claim(f"Horario formal obtenido: {data.get('schedule')}.", support_id, "temporal_schedule"))
    elif name == "shapely_pyproj":
        for item in data.get("queries", []) or []:
            claims.append(
                _claim(
                    f"Consulta espacial {item.get('op')}({item.get('left')}, {item.get('right')}) = {item.get('value')}.",
                    support_id,
                    "spatial",
                )
            )
    elif name == "pgmpy":
        for item in data.get("queries", []) or []:
            claims.append(
                _claim(
                    f"Inferencia {item.get('type')} para {item.get('variables')} con evidencia {item.get('evidence')}: {item.get('result')}.",
                    support_id,
                    "probabilistic",
                )
            )
    elif name == "dowhy":
        effect = dict(data.get("causal_effect") or {})
        if effect:
            claims.append(
                _claim(
                    f"Efecto causal estimado de {effect.get('treatment')} sobre {effect.get('outcome')}: {effect.get('effect_estimate')} mediante {effect.get('method_name')}.",
                    support_id,
                    "causal",
                )
            )
        counterfactual = dict(data.get("counterfactual") or {})
        if counterfactual:
            claims.append(
                _claim(
                    f"Se calcularon muestras contrafactuales bajo las intervenciones {counterfactual.get('interventions')}: {counterfactual.get('counterfactual_samples')}.",
                    support_id,
                    "counterfactual",
                )
            )
    elif name == "clingo_abduction":
        explanations = data.get("minimal_explanations", [])
        if data.get("solution_status") == "explained":
            claims.append(_claim(f"Explicaciones abductivas mínimas compatibles: {explanations}.", support_id, "abductive"))
        else:
            claims.append(_claim("No existe una explicación abductiva compatible dentro de las hipótesis permitidas.", support_id, "abductive"))
    elif name == "sklearn_tree_induction":
        claims.append(
            _claim(
                f"El modelo inductivo estadístico obtuvo métricas de validación {data.get('metrics')} sobre {data.get('test_examples')} ejemplos de prueba.",
                support_id,
                "statistical_induction",
            )
        )
        for prediction in data.get("predictions", []) or []:
            claims.append(
                _claim(
                    f"Predicción estadística para {prediction.get('input')}: {prediction.get('prediction')}.",
                    support_id,
                    "statistical_prediction",
                )
            )
    elif name == "networkx":
        raw = data
        if raw.get("is_acyclic") is not None:
            claims.append(_claim(f"El grafo formalizado tiene is_acyclic={raw.get('is_acyclic')}.", support_id, "graph"))
    elif name == "pydatalog":
        for fact in data.get("derived_facts", []) or []:
            claims.append(_claim(f"Hecho lógico derivado: {fact}.", support_id, "derived_fact"))
    elif name == "z3":
        claims.append(_claim(f"Z3 obtuvo solution_status={data.get('solution_status')} con valores {data.get('solution_values', {})}.", support_id, "constraints"))
    elif name == "legacy_combined":
        claims.append(_claim(f"Pipeline simbólico legacy: {data.get('combined_conclusion', 'análisis completado')}.", support_id, "combined"))

    return claims


def render_extended_grounded_markdown(contract: Dict[str, Any]) -> str:
    status = contract.get("status")
    if status != "success":
        reason = contract.get("review_reason") or contract.get("error") or status
        return (
            "## Resultado neurosimbólico no concluyente\n\n"
            f"Estado: `{status}`. Motivo: {reason}.\n\n"
            "No se publicó una conclusión porque la formalización o la ejecución no fue suficiente."
        )

    lines = ["## Resultado neurosimbólico verificable", ""]
    plan = contract.get("reasoning_plan", [])
    if plan:
        lines.extend([f"**Plan de razonamiento:** {' → '.join(plan)}", ""])

    deterministic = contract.get("deterministic")
    lines.extend([
        f"**Naturaleza del resultado:** {'determinista' if deterministic else 'incluye inferencia no determinista/estadística'}.",
        "",
        "### Conclusiones respaldadas",
        "",
    ])
    for claim in contract.get("claims", []):
        lines.append(f"- {claim.get('statement')}")

    warnings = contract.get("warnings", [])
    if warnings:
        lines.extend(["", "### Advertencias y supuestos", ""])
        for warning in warnings:
            lines.append(f"- {warning}")

    if contract.get("formalization_source"):
        lines.extend([
            "",
            "### Trazabilidad de formalización",
            "",
            f"- Fuente de la formalización: `{contract.get('formalization_source')}`.",
        ])
        if contract.get("formalization_source") == "hermes_tool_arguments":
            lines.append(
                "- Los motores verifican el cálculo sobre la estructura recibida; la correspondencia semántica entre esa estructura y el texto original depende de la formalización del tool y debe revisarse si el caso es sensible."
            )

    lines.extend(["", f"`run_id: {contract.get('run_id')}`"])
    return "\n".join(lines).strip()


def build_extended_grounded_contract(
    symbolic_result: Optional[Dict[str, Any]],
    *,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    result = symbolic_result or {}
    run_id = run_id or uuid.uuid4().hex
    status = str(result.get("status", "skipped"))
    analysis = dict(result.get("analysis") or {})
    results = dict(result.get("results") or {})
    formalized = dict(analysis.get("formalized_problem") or {})
    indicators = dict(formalized.get("structural_indicators") or {})
    engine_results = dict(results.get("engine_results") or {})

    contract: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "engine_used": result.get("engine_used", "none"),
        "reasoning_plan": list(results.get("reasoning_plan") or analysis.get("reasoning_plan") or []),
        "required_capabilities": list(results.get("required_capabilities") or []),
        "engines": {name: envelope.get("status", "missing") for name, envelope in engine_results.items()},
        "deterministic": results.get("deterministic"),
        "scope": {
            "type": "formalized_problem",
            "entities": list(formalized.get("entities", [])),
            "statement": "El resultado se limita a la estructura formalizada y a los motores ejecutados.",
        },
        "claims": [],
        "warnings": [],
        "assumptions": list(formalized.get("assumptions", [])),
        "unknowns": list(formalized.get("unknowns", [])),
        "formalization_source": indicators.get("formalization_source"),
        "audit": {
            "execution_time_seconds": result.get("execution_time"),
            "formalization_errors": list(result.get("formalization_errors", [])),
            "support_index": {},
            "knowledge_transfers": list(results.get("knowledge_transfers", [])),
        },
        "error": result.get("error"),
    }

    if status == "human_review":
        contract["review_reason"] = analysis.get("review_reason") or "human_review"
    elif status == "success":
        for name, envelope in engine_results.items():
            support_id = f"engine:{name}"
            contract["audit"]["support_index"][support_id] = envelope
            contract["warnings"].extend(list(envelope.get("warnings", [])))
            for item in _engine_claims(name, envelope, support_id):
                item["id"] = f"claim_{len(contract['claims']) + 1}"
                contract["claims"].append(item)

        if not engine_results or not contract["claims"]:
            contract["status"] = "error"
            contract["error"] = "no_publishable_engine_claims"

    support_index = contract["audit"].get("support_index", {})
    unresolved = sorted(
        {
            support_id
            for claim in contract.get("claims", [])
            for support_id in claim.get("supported_by", [])
            if support_id not in support_index
        }
    )
    contract["audit"]["unresolved_support"] = unresolved
    if contract["status"] == "success" and unresolved:
        contract["status"] = "error"
        contract["error"] = "unresolved_claim_support"
        contract["claims"] = []

    hash_input = {key: value for key, value in contract.items() if key not in {"run_id", "audit"}}
    contract["audit"]["result_hash"] = hashlib.sha256(
        json.dumps(hash_input, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()
    contract["rendered_markdown"] = render_extended_grounded_markdown(contract)
    return contract
