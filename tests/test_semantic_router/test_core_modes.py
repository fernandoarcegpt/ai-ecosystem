# tests/test_semantic_router/test_core_modes.py
"""
Conjunto de pruebas unitarias que validan que el *Semantic Router* del proyecto
detecta correctamente el modo de razonamiento necesario para cada tipo de
petición, **sin necesidad de usar tags manuales** (#RAZONAMIENTO, #DEPENDENCY,
#CONSTRAINT, etc.).

Las pruebas cubren los cinco modos operacionales obligatorios del enunciado:

1. `rules`��� ��� ��� →	identifica restricciones / políticas.
2. `graph`��� ��� ��� →	identifica dependencias, ciclos o topologías.
3. `hybrid`��� ��� ��� →	 combina varios patrones (p.ej. restricciones + dependencias).
4. `llm_only`��� →	 solicita una acción puramente lingüística (resumen,
   traducción, redacción, etc.).
5. `human_review` →	detecta incertidumbre o falta de información suficiente.

El objetivo es garantizar que, partir únicamente del texto de la solicitud,
el router elija el modo y el motor simbólico adecuados.
"""

import os
import sys
import pytest

# Add the skilled directory to the Python path so we can import from skilled.reasoning
# This ensures the module can be found even when running from different working directories
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../skilled')))

# Import from the correct module path
from skilled.reasoning.semantic_router import classify_task_structure


def test_rules_mode_selection():
    """
    Verifica que una solicitud que menciona explícitamente “reglas” sea
    clasificada como modo **rules** y que recomiende el motor Z3.
    """
    txt = "¿El operador puede eliminar un archivo protegido según estas reglas?"
    out = classify_task_structure(txt)
    assert out["mode"] == "rules"
    assert out["recommended_engine"] == "z3"


def test_graph_mode_selection():
    """
    Verifica que una solicitud que menciona “dependencias”, “ciclos” o “grafo”
    sea clasificada como modo **graph** y que recomiende el motor NetworkX.
    """
    txt = "Organiza estas tareas respetando sus dependencias y detecta ciclos."
    out = classify_task_structure(txt)
    assert out["mode"] == "graph"
    assert out["recommended_engine"] == "networkx"


def test_hybrid_mode_selection():
    """
    Verifica que cuando aparecen varios patrones (p.ej. restricciones + dependencias)
    el router seleccione el modo **hybrid** y recomiende el motor combinado.
    """
    txt = "Planifica el cambio y comprueba tanto políticas como dependencias."
    out = classify_task_structure(txt)
    # “hybrid” se elige cuando se detectan al menos dos de los patrones
    assert out["mode"] == "hybrid"
    assert out["recommended_engine"] == "combined"


def test_llm_only_detection():
    """
    Verifica que una solicitud puramente lingüística sea clasificada como
    **llm_only** (no necesita razonamiento simbólico).
    """
    txt = "Resume este documento."
    out = classify_task_structure(txt)
    assert out["mode"] == "llm_only"


def test_human_review_when_uncertain():
    """
    Verifica que, cuando la solicitud contiene información ambigua o falta
    datos críticos, el router devuelva el modo **human_review**.
    """
    txt = (
        "Asigna diez usuarios a cinco equipos bajo presupuesto limitado, "
        "pero sin información de costos."
    )
    out = classify_task_structure(txt)
    # En la práctica el router asignaría human_review cuando la incertidumbre sea alta.
    assert out["mode"] == "human_review"