# Integración Completa del Semantic Router en Hermes Agent

Este documento detalla cómo integrar el router semántico en el flujo de trabajo real de Hermes, más allá de la clasificación estática.

## Flujo de Integración Completa

```python
from skilled.reasoning.semantic_router import classify_task_structure

def integrated_workflow(request: str):
    """
    Flujo completo que integra clasificación y ejecución real.
    
    Este es el patrón recomendado para integración en Hermes Agent.
    """
    
    # 1. Clasificar la solicitud
    classification = classify_task_structure(request)
    
    # 2. Registrar trazabilidad para depuración
    log_routing_decision(classification)
    
    # 3. Rutar a la habilidad correspondiente
    if classification["mode"] == "human_review":
        return handle_human_review_case(classification, request)
        
    elif classification["mode"] == "llm_only":
        return process_with_llm(request)
        
    else:
        return execute_symbolic_engine(classification, request)

def handle_human_review_case(classification, request):
    """Maneja casos que requieren revisión humana"""
    missing_info = extract_missing_info(request, classification)
    
    return {
        "status": "human_review_needed",
        "mode": classification["mode"],
        "engine": "none",
        "executed": False,
        "reason": f"Falta información crítica: {', '.join(missing_info)}",
        "missing_info": missing_info,
        "next_action": "Solicitar información faltante al usuario",
        "classification_confidence": classification["confidence"]
    }

def execute_symbolic_engine(classification, request):
    """Ejecuta el motor simbólico correspondiente"""
    
    engines = {
        "rules": execute_rules_engine,
        "constraints": execute_constraints_engine,
        "graph": execute_graph_engine,
        "hybrid": execute_hybrid_engine
    }
    
    executor = engines.get(classification["mode"])
    if not executor:
        raise ValueError(f"Modo no soportado: {classification['mode']}")
    
    try:
        result = executor(request, classification)
        return {
            "status": "symbolic_engine_executed",
            "mode": classification["mode"],
            "engine": classification["recommended_engine"],
            "executed": True,
            "result": result,
            "classification_confidence": classification["confidence"]
        }
    except Exception as e:
        # Degradar a human_review en caso de error de ejecución
        return {
            "status": "execution_failed",
            "mode": "human_review",
            "engine": "none",
            "executed": False,
            "reason": f"Error en ejecución simbólica: {str(e)}",
            "fallback_reason": "Degradado a revisión humana por fallo de ejecución"
        }
```

## Semántica Definitiva de `confidence`

**`confidence` representa la confianza del router en la clasificación elegida, NO la confianza en la capacidad de resolver la tarea automáticamente.**

| Valor | Significado |
|-------|-------------|
| 0.9   | Muy seguro de que la clasificación es correcta |
| 0.8   | Seguro (usado en `human_review` cuando hay indicadores claros) |
| 0.45  | Incertidumbre en la clasificación (ej. modo `hybrid` con scores cercanos) |
| 0.0   | Sin confianza (fallback a `llm_only`) |

**Ejemplo crítico**: `human_review` con `confidence=0.8` = "El router está 80% seguro de que esta solicitud REQUIERE revisión humana"

## Orden de Precedencia Entre Modos

1. **MÁXIMA PRIORIDAD** → `human_review` (datos críticos faltantes)
2. **ALTA PRIORIDAD** → `rules`, `constraints`, `graph` (dominios bien definidos)
3. **MEDIA PRIORIDAD** → `hybrid` (múltiples dominios)
4. **BAJA PRIORIDAD** → `llm_only` (default para tareas lingüísticas)

**Regla de oro**: `human_review` SIEMPRE prevalece cuando hay información faltante crítica, independientemente de otros scores.

## Prevención de Falsos Positivos

| Caso | Clasificación | Razón |
|------|---------------|-------|
| "No hay datos de costos" | `human_review` | Información faltante crítica |
| "Información insuficiente" | `human_review` | Incertidumbre explícita |
| "Costos desconocidos" | `human_review` | Datos requeridos ausentes |
| "No hay restricciones de presupuesto" | `rules` / `llm_only` | Negación que ELIMINA restricción, no falta info |
| "No hay datos faltantes" | `llm_only` | Afirmación de completitud |
| "Costos desconocidos pero no intervienen" | `llm_only` | Info desconocida no necesaria para la tarea |

## Trazabilidad Observable

Para depuración y monitoreo, cada clasificación genera logs estructurados:

```json
// Caso human_review
{
  "timestamp": "2026-08-07T10:30:00Z",
  "request_hash": "abc123...",
  "classification": {
    "mode": "human_review",
    "engine": "none",
    "confidence": 0.8,
    "matched_patterns": ["sin información", "no hay datos"],
    "missing_info": ["costos por equipo"]
  },
  "executed": false,
  "routing_reason": "critical_missing_data"
}

// Caso constraints ejecutado
{
  "timestamp": "2026-08-07T10:30:05Z",
  "request_hash": "def456...",
  "classification": {
    "mode": "constraints",
    "engine": "z3",
    "confidence": 0.92
  },
  "executed": true,
  "execution_result": {
    "solver": "z3",
    "status": "sat",
    "solution": {"equipo_1": ["Ana", "Luis"], "equipo_2": ["Marta"]},
    "execution_time_ms": 145
  },
  "routing_reason": "constraint_satisfaction"
}
```

## Pruebas de Integración End-to-End

```python
def test_end_to_end_integration():
    """Pruebas que validan el flujo completo en Hermes"""
    
    test_cases = [
        {
            "input": "Resume las funciones principales de este proyecto.",
            "expected_mode": "llm_only",
            "expected_engine": "none",
            "executed": False
        },
        {
            "input": "Si admin puede editar y editor solo puede leer, ¿puede un editor modificar config.yaml?",
            "expected_mode": "rules",
            "expected_engine": "z3",
            "executed": True
        },
        {
            "input": "Tengo Ana, Luis y Marta. Reparte seis tareas sin que nadie tenga más de dos y las tareas A y B no pueden recaer en la misma persona.",
            "expected_mode": "constraints",
            "expected_engine": "z3",
            "executed": True
        },
        {
            "input": "A depende de B, B depende de C y C depende de A. ¿En qué orden debo ejecutar las tareas?",
            "expected_mode": "graph",
            "expected_engine": "networkx",
            "executed": True
        },
        {
            "input": "Distribuye diez usuarios en cinco equipos bajo presupuesto limitado, pero no tenemos los costos.",
            "expected_mode": "human_review",
            "expected_engine": "none",
            "executed": False
        }
    ]
    
    for case in test_cases:
        result = integrated_workflow(case["input"])
        assert result["mode"] == case["expected_mode"], f"Modo incorrecto para: {case['input']}"
        assert result["engine"] == case["expected_engine"], f"Motor incorrecto para: {case['input']}"
        assert result["executed"] == case["executed"], f"Estado ejecución incorrecto para: {case['input']}"
        print(f"✅ {case['input'][:50]}... → {result['mode']} ({result['engine']})")
```

## Configuración de Umbrales

```python
# Configuración avanzada para dominios específicos
SEMANTIC_ROUTER_CONFIG = {
    # Umbral para activar human_review (más bajo = más estricto)
    "uncertainty_threshold": 0.3,
    
    # Penalización para modo hybrid cuando hay incertidumbre
    "hybrid_uncertainty_penalty": 0.2,
    
    # Confianza mínima para activar rules (evita falsos positivos)
    "min_confidence_rules": 0.7,
    
    # Boost para constraints cuando hay palabras clave fuertes
    "constraints_keyword_boost": 1.5,
    
    # Modo debug para ver decisiones de routing
    "debug_mode": False
}
```

## Integración con Skills de Hermes

Para usar como skill en Hermes:

```bash
# Instalar skill
hermes skills install /ruta/a/semantic-router

# Verificar instalación
hermes skills list | grep semantic-router

# Usar en conversación
hermes chat -q "¿Puede un editor modificar config.yaml según las reglas?"
```

El skill se activa automáticamente cuando se detectan patrones de razonamiento simbólico.