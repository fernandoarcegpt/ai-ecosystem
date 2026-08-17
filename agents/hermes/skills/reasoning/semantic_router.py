"""
Semantic Router para Hermes Agent

Este módulo proporciona la clasificación estructural de tareas para determinar
automáticamente qué modo de razonamiento simbólico se necesita, sin requerir
etiquetas manuales (#RAZONAMIENTO, #DEPENDENCY, etc.).

Modos disponibles:
- llm_only: tareas puramente lingüísticas (resumen, traducción, redacción)
- rules: políticas, permisos, restricciones, cumplimiento
- constraints: restricciones simultáneas, planificación, asignación, horarios
- graph: dependencias, ciclos, caminos, relaciones, orden de ejecución
- hybrid: combinación de varios de los anteriores
- human_review: cuando hay incertidumbre alta o faltan datos críticos
"""

import re
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ReasoningMode(Enum):
    """Modos de razonamiento disponibles"""
    LLM_ONLY = "llm_only"
    RULES = "rules"
    CONSTRAINTS = "constraints"
    GRAPH = "graph"
    HYBRID = "hybrid"
    HUMAN_REVIEW = "human_review"


class RecommendedEngine(Enum):
    """Motores simbólicos recomendados"""
    NONE = "none"
    NETWORKX = "networkx"
    Z3 = "z3"
    PYDATALOG = "pydatalog"
    COMBINED = "combined"


@dataclass
class ClassificationResult:
    """Resultado de la clasificación estructural"""
    mode: str
    recommended_engine: str
    confidence: float
    matched_patterns: List[str]
    structural_indicators: Dict[str, Any]


def classify_task_structure(request: str) -> Dict[str, Any]:
    """
    Analiza la estructura semántica de una solicitud para determinar el modo
    de razonamiento apropiado.
    
    Args:
        request: Texto de la solicitud del usuario
        
    Returns:
        Dict con:
        - mode: uno de ["llm_only", "rules", "constraints", "graph", "hybrid", "human_review"]
        - recommended_engine: motor simbólico recomendado
        - confidence: nivel de confianza (0-1)
        - matched_patterns: patrones detectados
        - structural_indicators: detalles de indicadores estructurales
    """
    request_lower = request.lower()
    
    # Patrones estructurales que indican cada modo
    patterns = {
        "rules": {
            "keywords": [
                "regla", "reglas", "política", "políticas", "permiso", "permisos",
                "autorización", "cumplimiento", "compliance", "prohibido", "permitido",
                "según estas reglas", "bajo estas reglas", "conforme a", "normativa",
                "normativo", "legal", "ilegal", "autorizado", "no autorizado"
            ],
            "structural": [
                r'\bpuede\b.*\beliminar\b',
                r'\bpermite\b.*\bhacer\b',
                r'\bprohíbe\b',
                r'\bes\b.*\bpermitido\b',
                r'\baccording to\b.*\brules?\b'
            ],
            "engine": RecommendedEngine.Z3.value
        },
        "constraints": {
            "keywords": [
                "restricción", "restricciones", "límite", "límites", "bound", "bounds",
                "presupuesto", "budget", "capacidad", "capacity", "máximo", "mínimo",
                "asigna", "asignar", "asignación", "schedule", "horario", "horarios",
                "tiempo", "recurso", "recursos", "simultáneo", "simultánea",
                "sin cruzar", "sin superar", "no exceder", "máximo de"
            ],
            "structural": [
                r'\basigna\b.*\ba\b.*\bpersonas?\b',
                r'\bpresupuesto\b.*\blimitado\b',
                r'\bhorarios?\b.*\bsin\b.*\bcruzar\b',
                r'\bsin\b.*\bsuperar\b.*\bpresupuesto\b'
            ],
            "engine": RecommendedEngine.Z3.value
        },
        "graph": {
            "keywords": [
                "dependencia", "dependencias", "dependency", "dependencies",
                "ciclo", "ciclos", "cycle", "cycles", "grafo", "graph",
                "topología", "topology", "orden", "ordenar", "sequence", "secuencia",
                "camino", "caminos", "path", "paths", "ruta", "rutas",
                "relación", "relaciones", "relation", "relations",
                "detecta ciclos", "respetando", "depende de", "bloquea",
                "predecesor", "sucesor", "anterior", "posterior"
            ],
            "structural": [
                r'\bdepende\b.*\bde\b',
                r'\brespetando\b.*\bdependencias?\b',
                r'\bdetecta\b.*\bciclos?\b',
                r'\border\b.*\bde\b.*\bejecución\b',
                r'\btopolog\w+\b'
            ],
            "engine": RecommendedEngine.NETWORKX.value
        },
        "hybrid": {
            "keywords": [
                "planifica", "planificar", "planificación", "plan", "comprueba",
                "verifica", "validar", "validación", "tanto", "como", "y también",
                "políticas y", "dependencias y", "reglas y", "restricciones y"
            ],
            "structural": [
                r'\bplanifica\b.*\bcomprueba\b',
                r'\bpolíticas?\b.*\bdependencias?\b',
                r'\breglas?\b.*\bdependencias?\b',
                r'\brestricciones?\b.*\bdependencias?\b'
            ],
            "engine": RecommendedEngine.COMBINED.value
        },
        "human_review": {
            "keywords": [
                "sin información", "no hay datos", "falta información", "incierto",
                "ambiguo", "ambigüedad", "desconocido", "no sé", "no se sabe",
                "decisión humana", "revisión humana", "aprobación", "autorización"
            ],
            "structural": [
                r'\bsin\b.*\binformación\b',
                r'\bno\b.*\bdatos?\b',
                r'\bfalta\b.*\binformación\b',
                r'\bdesconocido\b'
            ],
            "engine": RecommendedEngine.NONE.value
        }
    }
    
    # Calcular puntuaciones para cada modo
    scores = {}
    matched_patterns = {}
    structural_indicators = {}
    
    for mode_name, config in patterns.items():
        score = 0
        matches = []
        indicators = {}
        
        # Puntuación por palabras clave
        for keyword in config["keywords"]:
            count = request_lower.count(keyword.lower())
            if count > 0:
                score += count * 2
                matches.append(keyword)
        
        # Puntuación por patrones estructurales (más peso)
        for pattern in config["structural"]:
            if re.search(pattern, request_lower):
                score += 5
                matches.append(f"pattern:{pattern}")
        
        if score > 0:
            scores[mode_name] = score
            matched_patterns[mode_name] = matches
            structural_indicators[mode_name] = {"keyword_count": len([m for m in matches if not m.startswith("pattern:")]),
                                                 "pattern_count": len([m for m in matches if m.startswith("pattern:")])}
    
    # Determinar el modo ganador
    if not scores:
        return {
            "mode": ReasoningMode.LLM_ONLY.value,
            "recommended_engine": RecommendedEngine.NONE.value,
            "confidence": 0.9,
            "matched_patterns": [],
            "structural_indicators": {}
        }
    
    # Verificar si hay indicadores de incertidumbre ANTES de decidir hybrid
    # Si hay "sin información", "no hay datos", "falta información" -> priorizar human_review
    uncertainty_indicators = [
        "sin información" in request_lower,
        "no hay datos" in request_lower,
        "falta información" in request_lower,
        "desconocido" in request_lower
    ]
    if any(uncertainty_indicators) and "human_review" in scores:
        # human_review tiene prioridad cuando hay incertidumbre explícita
        return {
            "mode": ReasoningMode.HUMAN_REVIEW.value,
            "recommended_engine": RecommendedEngine.NONE.value,
            "confidence": 0.8,
            "matched_patterns": matched_patterns.get("human_review", []),
            "structural_indicators": structural_indicators.get("human_review", {})
        }
    
    # Verificar si hay múltiples modos con puntuaciones altas (hybrid)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_score = sorted_scores[0][1]
    top_mode = sorted_scores[0][0]
    
    # Si el modo top es hybrid, o si hay múltiples modos con scores cercanos
    if top_mode == "hybrid" or (len(sorted_scores) > 1 and sorted_scores[1][1] >= top_score * 0.7):
        # Verificar si realmente hay múltiples dominios
        modes_above_threshold = [m for m, s in scores.items() if s >= top_score * 0.5]
        # Excluir human_review del hybrid si hay incertidumbre (ya se manejó arriba)
        if len(modes_above_threshold) >= 2:
            return {
                "mode": ReasoningMode.HYBRID.value,
                "recommended_engine": RecommendedEngine.COMBINED.value,
                "confidence": min(top_score / 20.0, 1.0),
                "matched_patterns": [p for m in modes_above_threshold for p in matched_patterns.get(m, [])],
                "structural_indicators": {m: structural_indicators.get(m, {}) for m in modes_above_threshold}
            }
    
    # Modo único ganador
    engine = patterns[top_mode]["engine"]
    
    # Verificar si human_review tiene prioridad cuando hay incertidumbre (para otros casos)
    if top_mode == "human_review" or (top_mode in ["constraints", "graph"] and top_score < 8):
        # Baja confianza en modos que requieren datos precisos
        if "sin información" in request_lower or "no hay datos" in request_lower or "falta información" in request_lower:
            return {
                "mode": ReasoningMode.HUMAN_REVIEW.value,
                "recommended_engine": RecommendedEngine.NONE.value,
                "confidence": 0.8,
                "matched_patterns": matched_patterns.get("human_review", []),
                "structural_indicators": structural_indicators.get("human_review", {})
            }
    
    confidence = min(top_score / 15.0, 1.0)
    
    return {
        "mode": top_mode,
        "recommended_engine": engine,
        "confidence": confidence,
        "matched_patterns": matched_patterns.get(top_mode, []),
        "structural_indicators": structural_indicators.get(top_mode, {})
    }


def get_coordinator():
    """Placeholder para compatibilidad con tests existentes"""
    return None


# Función de conveniencia para testing
if __name__ == "__main__":
    test_cases = [
        "¿El operador puede eliminar un archivo protegido según estas reglas?",
        "Organiza estas tareas respetando sus dependencias y detecta ciclos.",
        "Planifica el cambio y comprueba tanto políticas como dependencias.",
        "Resume este documento.",
        "Asigna diez usuarios a cinco equipos bajo presupuesto limitado, pero sin información de costos."
    ]
    
    for case in test_cases:
        result = classify_task_structure(case)
        print(f"Input: {case}")
        print(f"  Mode: {result['mode']}")
        print(f"  Engine: {result['recommended_engine']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Patterns: {result['matched_patterns'][:5]}")
        print()