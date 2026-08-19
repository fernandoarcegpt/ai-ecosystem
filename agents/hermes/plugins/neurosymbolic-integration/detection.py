"""Detección conservadora y auditable de intención neurosimbólica.

La detección decide únicamente si Hermes debe solicitar la herramienta y qué
capacidades debe intentar formalizar. No construye specs ni autoriza a inventar
datos que no estén en el mensaje del usuario.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Tuple


def _normalize(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(text).lower())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


# Cada regla aporta puntos solo cuando se reconoce una estructura bastante
# específica. El umbral evita activar motores por palabras aisladas como
# "plan", "causa" o "probabilidad" en conversación ordinaria.
_RULES: Dict[str, Tuple[Tuple[str, int, str], ...]] = {
    "graph": (
        (r"\b[A-Za-z_]\w*\s*(?:->|→)\s*[A-Za-z_]\w*", 5, "graph_explicit_edge"),
        (r"\b(?:grafo|nodo|arista|orden\s+topologico)\b", 2, "graph_terms"),
        (r"\b\w+\s+depende\s+de\s+\w+\b", 3, "graph_dependency"),
        (r"\b(?:ciclo|camino|alcanzabilidad)\b", 2, "graph_query"),
    ),
    "logic": (
        (r"\bsi\b.{1,160}\bentonces\b", 5, "logic_if_then"),
        (r"\breglas?\s*[:=]", 3, "logic_rules_block"),
        (r"\bhechos?\s*[:=]", 2, "logic_facts_block"),
        (r"\b(?:deducir|deduce|inferir|infiere)\b", 2, "logic_inference_request"),
    ),
    "constraints": (
        (r"\b[A-Za-z_]\w*\s*(?:>=|<=|>|<|=)\s*-?\d+", 5, "constraint_comparison"),
        (r"\b(?:maximo|maxima|a\s+lo\s+sumo)\s+\d+\b", 3, "constraint_maximum"),
        (r"\bno\s+pueden\b.{0,80}\bmisma\b", 3, "constraint_incompatibility"),
        (r"\b(?:reparte|asigna|distribuye)\b.{0,120}\bentre\b", 2, "constraint_assignment"),
    ),
    "planning": (
        (r"\bplanificacion\s+clasica\b", 5, "planning_classical"),
        (r"\bprecondicion(?:es)?\b", 3, "planning_preconditions"),
        (r"\bestado\s+inicial\b", 2, "planning_initial_state"),
        (r"\b(?:efecto|efectos)\s+de\s+(?:la|las|una|unas)?\s*acciones?\b", 2, "planning_effects"),
        (r"\bacciones?\b.{0,80}\bobjetivo(?:s)?\b", 2, "planning_actions_goals"),
        (r"\bsecuencia\s+de\s+acciones\b", 4, "planning_action_sequence"),
        (r"\bque\s+acciones\b.{0,100}\b(?:alcanzar|lograr|llegar)\b", 3, "planning_reach_goal"),
    ),
    "temporal": (
        (r"\brestricciones?\s+temporales?\b", 5, "temporal_explicit"),
        (r"\b(?:dura|duracion|tarda)\s+(?:de\s+)?\d+(?:[.,]\d+)?", 2, "temporal_duration"),
        (r"\b(?:antes\s+de|despues\s+de|terminar\s+antes|empezar\s+despues)\b", 2, "temporal_precedence"),
        (r"\b(?:cuando|hasta\s+que)\s+termine\b", 2, "temporal_finish_dependency"),
        (r"\b(?:no\s+se\s+solapen|sin\s+solaparse|no\s+solapar)\b", 3, "temporal_non_overlap"),
        (r"\b(?:deadline|fecha\s+limite)\b", 3, "temporal_deadline"),
    ),
    "spatial": (
        (r"\bdistancia\s+geodesica\b", 5, "spatial_geodesic"),
        (r"\b(?:interseccion|relacion)\s+espacial\b", 5, "spatial_explicit"),
        (r"\b(?:poligono|geometria|coordenadas?|punto)\b", 2, "spatial_geometry_terms"),
        (r"\b(?:esta|queda)\s+dentro\s+de\b|\bintersecta\b|\btoca\b", 2, "spatial_relation"),
        (r"\(\s*-?\d+(?:[.,]\d+)?\s*,\s*-?\d+(?:[.,]\d+)?\s*\)", 2, "spatial_coordinate_pair"),
    ),
    "probabilistic": (
        (r"\bbayes(?:iano|iana)?\b", 5, "probabilistic_bayes"),
        (r"\bprobabilidad\s+(?:posterior|condicional)\b", 5, "probabilistic_conditional"),
        (r"\bprobabilidad\s+de\b.{0,80}\b(?:dado|dada)\b", 5, "probabilistic_given"),
        (r"\bp\s*\([^)]*\|[^)]*\)", 5, "probabilistic_notation"),
        (r"\bactualiz(?:a|ar)\s+(?:la\s+)?probabilidad\b", 3, "probabilistic_update"),
        (r"\b(?:prevalencia|sensibilidad|especificidad)\b", 2, "probabilistic_test_parameter"),
        (r"\bprueba\b.{0,50}\bpositiv[ao]\b", 2, "probabilistic_positive_test"),
        (r"\bevidencia\b", 1, "probabilistic_evidence"),
    ),
    "causal": (
        (r"\befecto\s+causal\b", 5, "causal_effect"),
        (r"\bgrafo\s+causal\b", 5, "causal_graph"),
        (r"\bconfusor(?:es)?\b", 4, "causal_confounder"),
        (r"\bvariable\s+de\s+tratamiento\b", 3, "causal_treatment"),
        (r"\bintervencion(?:es)?\b", 2, "causal_intervention"),
        (r"\btratamiento\b", 2, "causal_treatment_term"),
        (r"\b(?:resultado|outcome)\b", 1, "causal_outcome"),
    ),
    "counterfactual": (
        (r"\bcontrafactual(?:es)?\b", 5, "counterfactual_explicit"),
        (r"\b(?:que|qué)\s+habria\s+pasado\s+si\b", 5, "counterfactual_habria"),
        (r"\b(?:que|qué)\s+hubiera\s+pasado\s+si\b", 5, "counterfactual_hubiera"),
    ),
    "abductive": (
        (r"\babduccion\b|\babductiv", 5, "abductive_explicit"),
        (r"\bexplicaciones?\s+minimas?\b", 5, "abductive_minimal"),
        (r"\bhipotesis\s+permitidas?\b", 4, "abductive_assumables"),
        (r"\b(?:posibles?\s+causas?|hipotesis)\b.{0,80}\b(?:explican?|explicar)\b", 4, "abductive_explanation"),
        (r"\b(?:que\s+pudo\s+causar|que\s+podria\s+explicar)\b", 4, "abductive_natural_question"),
        (r"\bobservacion\b", 1, "abductive_observation"),
    ),
    "statistical_induction": (
        (r"\barbol\s+de\s+decision\b", 4, "induction_tree"),
        (r"\bentrena(?:r)?\b.{0,80}\b(?:ejemplos?|datos)\b", 4, "induction_train_examples"),
        (r"\bclasific(?:a|ar|acion)\b.{0,80}\b(?:datos|ejemplos)\b", 4, "induction_classification"),
        (r"\bregresion\b.{0,80}\b(?:datos|ejemplos)\b", 4, "induction_regression"),
        (r"\bpredic(?:e|ir|cion)\b.{0,80}\b(?:datos|ejemplos|modelo)\b", 3, "induction_prediction"),
        (r"\bcon\s+estos\s+ejemplos\b", 2, "induction_examples"),
        (r"\bcon\s+estos\s+ejemplos\b.{0,80}\bpredic", 4, "induction_examples_then_predict"),
    ),
}

_THRESHOLD = 4


def detect_extended_reasoning(text: str) -> Dict[str, Any]:
    """Devuelve capacidades, puntuaciones y evidencia de detección."""
    normalized = _normalize(text)
    scores: Dict[str, int] = {}
    evidence: Dict[str, List[str]] = {}

    for capability, rules in _RULES.items():
        score = 0
        matched: List[str] = []
        for pattern, weight, label in rules:
            if re.search(pattern, normalized, flags=re.IGNORECASE | re.DOTALL):
                score += weight
                matched.append(label)
        if score >= _THRESHOLD:
            scores[capability] = score
            evidence[capability] = matched

    capabilities = list(scores)
    # Un contrafactual necesita un modelo causal; declarar ambos evita que el
    # router trate el contrafactual como una capacidad aislada.
    if "counterfactual" in capabilities and "causal" not in capabilities:
        capabilities.insert(capabilities.index("counterfactual"), "causal")
        scores["causal"] = max(scores.get("causal", 0), _THRESHOLD)
        evidence["causal"] = ["required_by_counterfactual"]

    return {
        "requires_tool": bool(capabilities),
        "capabilities": capabilities,
        "scores": scores,
        "evidence": evidence,
    }
