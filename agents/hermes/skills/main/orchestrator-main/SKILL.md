---
name: orchestrator-main
description: "Skill principal dinámico que orquesta todo el ecosistema: Hermes, Claude Code, Ruflo, búsqueda, planificación y descarga de libros"
platforms: [linux, macos, windows]
tags: [orchestrator, main, integration, dynamic, master]
version: 3.0.0
author: Hermes Agent
license: MIT
---

# Orchestrator Main - Skill Principal Dinámico

## Propósito

Este skill actúa como **capa maestra** que orquesta todo el ecosistema integrado:
- **Hermes** → Orquestador y coordinador principal
- **Claude Code** → Ejecutor de tareas principal con el ecosistema de skills de Hermes
- **Ruflo** → Componente de soporte y contenedor de herramientas
- **Búsqueda** → research-search-master (integrado), youtube-content (integrado), web_search (integrado), blogwatcher (integrado)
- **Planificación** → general-planning (integrado), plan (integrado), test-driven-development (integrado)
- **Descarga libros** → zlibrary-mcp (integrado), memorwise (integrado)

## Características Dinámicas Clave

✅ **Auto-detección**: Detecta qué skills están disponibles y los usa  
✅ **Fallback inteligente**: Si un skill falla, usa el siguiente más adecuado del mismo tipo (ej: si research-search-master falla, usa web_search)  
✅ **Modulación por contexto**: Ajusta el flujo de trabajo según el tipo de tarea (feature/bug/research/plan/download)  
✅ **Módulo por componente**: Cada área tiene su handler independiente con contexto propio  
✅ **Actualización automática**: Detecta cambios en habilidades, renombra habilidades, repara configuraciones dañadas  

## Arquitectura Modular Dinámica

### 1. Búsqueda de Información (`search_handler`)
Orquesta:
- `research-search-master` (si está activo)
- `web_search` (fallback)
- `youtube-content` (para contenido audiovisual)
- `blogwatcher` (para blogs y RSS)

### 2. Planificación (`plan_handler`)
Orquesta:
- `general-planning` para proyectos complejos
- `plan` para tareas simples
- `test-driven-development` para planes TDD

### 3. Ejecución (`execute_handler`)
Orquesta:
- `delegation-handler` (delegador de tareas especializadas)
- Claude Code (ejecutor principal cuando está autenticado)
- Ruflo (ejecutor secundario)
- Herramientas de terminal integradas (último recurso)
- **Policy Gate** → Validación de políticas antes de ejecución (cuando se usa --gate-policy)

### 4. Descarga y Memoria (`download_handler`)
Orquesta:
- zlibrary-mcp → descarga libros desde `.claude-flow`
- notex → procesa e indexa contenido mediante ingest mode (`-ingest`)
- almacenamiento en `.hermes/library/downloads/` con metadatos
- **Nota**: memorwise fue migrado a notex - ver referencias/notex-migration.md

## Comandos Dinámicos

### 1. Detección y Diagnóstico Avanzado
```bash
orchestrator-main "tarea" --detect
# Salida:
# - Skills detectados: research-search-master ✅, general-planning ✅
# - Skills inactivos: web_search ⚠️ (requiere configuración)
# - Skills con errores: youtube-content ❌ (clave faltante)
# - Recomendaciones: usar web_search como fallback
```

### 2. Planificación Inteligente con Desvío
```bash
orchestrator-main "implementar API de autenticación" --plan --research --full
# Flujo dinámico:
# 1. research-search-master → investigar
# 2. general-planning → crear plan
# 3. execute_handler → Claude Code implementa
# 5. requesting-code-review → revisión de código
# 5. download_handler → descarga libro de referencia
```

### 3. Descarga con Fallback Automático
```bash
orchestrator-main "libro Deep Learning" --download --zlib --zlib-fallback --indexar
# Flujo:
# 1. zlibrary-mcp → descarga libro
# 2. Si falla, web_search → descarga alternativa
# 4. memorwise → indexa y digiere
```

### 4. Planificación Adaptativa por Contexto
```bash
orchestrator-main "corregir error de frontend" --plan

# Selección dinámica:
# 1. error visible → research-search-master para soluciones similares
# 2. error documentado → plan para TDD
# 3. error de dependencia → web_search + download_handler
```

## Estructura de Ejecución Dinámica con Contexto

```
orchestrator-main "tarea X"
    │
    ├── VERIFICAR entorno → check_environment()
    │   ├── Skills disponibles
    │   ├─ Dependencias
    │   └── Configuración
    │
    ├── ANALIZAR tarea → parse_task()
    │   ├─ Tipo: feature/bug/research/plan
    │   ├─ Prioridades
    │   └─ Skills requeridos
    │
    ├── ORQUESTAR → workflow()
    │   ├── search_handler → buscar información
    │   ├─ plan_handler → crear plan si es necesario
    │   ├─ execute_handler → ejecutar con Claude Code/Ruflo
    │   └─ download_handler → descargar libros si aplica
    │
    └── ACTUALIZAR memoria → update_memory()
        ├─ Guardar resultados
        ├─ Actualizar patrones
        └── Indexar en memorwise
```

## Manejo de Errores Dinámico

### 1. Si falta un skill:
```bash
# Auto-detección
Skill 'xyz' no encontrado
Alternativa: usando 'web_search' como fallback
```

### 2. Si Claude Code no está autenticado:
```bash
# Fallback directo a herramientas locales
Claude Code no disponible → usando herramientas de terminal
```

### 3. Si zlib MCP falla:
```bash
# Alternativa
Descarga fallida → intentando búsqueda web o manual
```

## Ejemplos de Uso Real

### Caso 1: Investigación + Solución
```bash
orchestrator-main "resolver problema de memoria en Python"
# 1. Busca en StackOverflow, GitHub, YouTube
# 2. Crea plan con general-planning
# 3. Ejecuta con Claude Code
# 4. Indexa en memorwise
```

### Caso 2: Descarga + Digerión
```bash
orchestrator-main "libro Machine Learning" --download --zlib --memorize
# 1. Busca en zlibrary-mcp
# 2. Descarga libro
# 3. Indexa en memorwise
# 4. Resume y extrae conceptos clave
```

### Caso 3: Feature Completo
```bash
orchestrator-main "sistema de recomendaciones" --full
# 1. Investigación (research-search-master)
# 2. Planificación (general-planning)
# 3. Diseño de arquitectura
# 4. Implementación TDD
# 5. Pruebas de integración
# 6. Documentación
# 7. Indexado en memorwise
```

## Archivos Generados

```
.hermes/
├── plans/                    # Planes generados
├── logs/                     # Logs de ejecución
├── library/                  # Libros descargados
│   └── zlib_downloads/
├── memory/                   # Memoria actualizada
└── artifacts/                # Resultados de búsquedas
```

## Registro de Memoria Automático

Al completar tareas, actualiza automáticamente:
- Patrones de búsqueda exitosos
- Tiempos de ejecución por tipo de tarea
- Skills más efectivos por contexto
- Errores comunes y soluciones

## Actualización Automática

Este skill se autoactualiza:
- Cada 24h verifica updates de skills
- Detecta nuevas habilidades disponibles
- Ajusta workflow según capabilities del sistema
- Mantiene compatibilidad hacia atrás

## Notas Clave

- � ✅ **Dinámico**: No se rompe con cambios
- � ✅ **Auto-detección**: Usa lo que hay disponible
- � ✅ **Fallbacks**: Múltiples rutas de ejecución
- � ✅ **Memoria persistente**: Aprende de cada ejecución
- � ✅ **Documentación automática**: Genera docs al completar
- � ✅ **Patch tracking**: Registra automáticamente cambios (ej: modification en src/ingest.py:31)
- � ✅ **CBM Integration**: Soporta codebase-memory-mcp para análisis estructural de código

## Próximas Mejoras

- [ ] Integración con MCPs adicionales
- [ ] Cache inteligente de resultados
- [ ] Optimización de workflow por tipo de tarea
- [ ] Dashboard de estado del orquestador
- [ ] Integración de razonamiento neurosimbólico (NetworkX, PyDatalog, Z3)
- [ ] Integración de Policy Gate (--gate-policy flag) para validación de políticas antes de ejecución
- [ ] **Patch Management**: Integrar modo de creación/edición de parches (ej: usar comando `patch` de Hermes para modify code)
- [ ] **CBM Workflow Enhancement**: Mejorar integración con codebase-memory-mcp para búsquedas estructurales

### Reference Material
- [references/cbm-install.md] (command-line patterns)
- [references/cbm-tests.md] (verification workflow)
- [references/cbm-integration.md] (integration patterns and best practices)

### Compatibility Layer
- ` orchestrator-main` now handles CBM initialization sequence
- `knowledge-broker` handles CBM data disambiguation rules

### New Support Files Added
- `references/cbm-install.md` - Comprehensive installation guide for codebase-memory-mcp
- `references/cbm-tests.md` - Verification workflow and troubleshooting patterns
- `references/cbm-integration.md` - Integration patterns and ecosystem best practices

## Integración de Patch Management

### Nueva funcionalidad: Modo de creación/edición de parches

El orquestador ahora soporta modificación directa de código mediante el patrón Hermes `patch`, documentando cambios para conocimiento futuro.

#### Uso:
```bash
# Crear parche para archivo específico
orchestrator-main "patch src/ingest.py" --path="/home/fernando/ai-ecosystem/src/ingest.py"

# Aplicar parche basado en historia de chat
orchestrator-main "patch src/ingest.py:31" --from-session="b8380c00-1a06-4f9e-b215-d04f7c21a4bb"

# Lista parches en sesión
orchestrator-main "listar patches" --session-filter="2026-08-04"
```

#### Capacidad de Patch Store:
- **Gestión**: Guardar/patch/eliminar cambios de código
- **Meta**: Referencias a sesiones específicas (message_id, session_id)
- **Documentación**: Almacenar en `references/patches/` con formato markdown
- **Auditoría**: Llevar historial completo de modificaciones

#### Componentes integrados:
- `patch.skill.PatchManager` - Manejador de parches
- `memory.skill.Memory` - Almacenar referencias de parches
- Herramientas `hermes_tools.patch` - Aplicar cambios

#### Ejemplo de Documento de Patch:
```markdown
---
File: src/ingest.py
Session: b8380c00-1a06-4f9e-b215-d04f7c21a4bb
Message ID: patch_n0045pzac76a

## Patch: KùzuDB Path

### Contexto
Cambiar ruta de base de datos KùzuDB durante migración de memorwise a knowledge-broker.

### Motivo
Migración de memoria vectorial a conocimiento agente.

### Diff
```diff
- db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base"
+ db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
```

### Autor
orchestrator-main (edición automática)
---
```

## Integración de Policy Gate

### Nueva funcionalidad: `--gate-policy` flag

El orquestador ahora soporta validación de políticas antes de ejecutar tareas mediante el flag `--gate-policy`.

#### Uso:
```bash
# Ejecutar tarea con validación de políticas
orchestrator-main "modify admin settings" --gate-policy

# Con planificación completa y validación
orchestrator-main "implementar sistema de pagos" --plan --gate-policy --full
```

#### Flujo de integración:
1. **POLICY_CHECK** - Antes de ejecutar, evalúa la tarea con Policy Gate
2. **Decisión**:
   - `ALLOW` → Ejecutar directamente
   - `DENY` → Bloquear y reportar razón
   - `REQUIRE_HUMAN` → Enviar a Human Gate para aprobación
   - `UNKNOWN` → Requerir revisión humana

#### Componentes integrados:
- `policy_gate.skill.PolicyGate` - Evaluador de políticas
- `human_gate.skill.HumanGate` - Gestor de revisiones humanas
- Integración con `src/reasoning/policy_engine.py` (motor determinista)
- Contratos en `src/reasoning/contracts.py`

#### Prueba de integración:
```bash
# Test completo
cd /home/fernando/ai-ecosystem
PYTHONPATH=/home/fernando/.hermes/skills python3 test_integration.py
```

#### Salida esperada:
```
🎉 INTEGRATION TEST PASSED
==============================================================
✅ Policy Gate: Successfully evaluates tasks against policies
✅ Human Gate: Successfully manages human review workflow
✅ Integration: Successfully combines both systems
==============================================================
The Policy Gate and Human Gate skills are fully functional
and ready for production use in the Hermes Agent ecosystem.
```

## Lecciones Aprendidas: Integración de Razonamiento Neurosimbólico

### PyDatalog: Error Común con `load()` vs `defrule()`

**Problema**: El método `pydatalog.load()` falla con reglas dinámicas definidas como strings, produciendo `SyntaxError: invalid syntax`.

**Causa**: `load()` espera código Datalog en formato archivo, no strings con reglas construidas dinámicamente.

**Solución**: Usar `pydatalog.db.defrule()` directamente:

```python
# INCORRECTO - Falla con SyntaxError
pydatalog.load("ancestor(X, Y) <= parent(X, Y).")

# CORRECTO - Usa defrule
from pydatalog.db import defrule

defrule("ancestor", "ancestor(X, Y)", "parent(X, Y)")
```

**Pitfall crítico**: Cuando escribir strings de documentación que contienen fragmentos de código, verificar que el sistema de archivos no introduzca caracteres de escape invisibles (`\n` al final de líneas). Si ocurre, usar un editor que preserve caracteres literales o crear el archivo con `write_file` completo en lugar de `patch`.

### HumanReviewRequest Metadata Filtering

**Problema**: When passing arbitrary metadata to `HumanReviewRequest` constructor, unexpected keyword argument errors occur (e.g., `integration_test=True`).

**Causa**: The dataclass only accepts defined fields; metadata contains extra keys.

**Solución**: Filter metadata to only include valid fields before passing to constructor:

```python
import dataclasses

valid_fields = {f.name for f in dataclasses.fields(HumanReviewRequest)}
filtered_metadata = {k: v for k, v in metadata.items() if k in valid_fields and v is not None}
```

**Pitfall crítico**: Python 3.8+ no soporta `{**dict} or {}` syntax correctamente en todos los contextos. Usar `{**metadata} if metadata else {}` en lugar de esto último.

### Convenciones de Import PyDatalog
**Import correcto**:
```python
from pyDatalog import pyDatalog as pydatalog  # Nombre del paquete es pyDatalog
from pydatalog.db import defrule  # Módulo interno
```

**Nota**: El paquete se instala como `pip install pyDatalog` pero se importa como `pydatalog` (minúsculas).

### Integración de Motores Simbólicos (NetworkX, PyDatalog, Z3)

**Patrón de integración exitoso**:
1. Crear wrappers independientes en `skilled/reasoning/`
2. Usar `__init__.py` para exportar clases principales
3. Configuración centralizada en `config.yaml`
4. Skill de orquestación `neuro-symbolic` para activación

**Activación**: Automática basada en detección de patrones (dependencias, restricciones, ciclos) o manual con `#RAZONAMIENTO` / `#SOLVER`.

### Preferencia de Comunicación del Usuario

**El usuario prefiere respuestas directas y concisas**:
- NO explicar por qué algo no funciona sin mostrar la solución
- NO crear documentación innecesaria a menos que se solicite
- SÍ reportar bloqueos honestamente y proseguir con alternativas
- SÍ mostrar resultados de ejecución real, no outputs fabricados

---

## 📦 Migración de Memoria: Lecciones Aprendidas

### Riesgo Crítico: Referencias Hardcodeadas

**Situación**: El directorio `wiki_memoria` estaba referenciado en 15 archivos diferentes (tests, scripts, README). Su eliminación sin migración previa causó fallos silenciosos en flujos de descarga.

**Lección**: **NUNCA eliminar un directorio de memoria sin**:
1. Buscar todas las referencias con `grep -r "wiki_memoria" .`
2. Actualizar rutas con `sed -i "s/wiki_memoria/sharememory/g"`
3. Verificar con tests de integración
4. Solo entonces eliminar el directorio antiguo

### Ruta Nueva Recomendada

```bash
# Estructura actualizada
sharememory/
├── hermes_memory/     # Estado del agente Hermes
├── claude_memory/     # Estado de Claude Code
└── wiki/              # Archivos migrados (nuevo destino)
```

### Comando de Verificación Post-Migración

```bash
orchestrator-main "verificar migración memoria" --migrate-check
# Verifica:
# - Rutas actualizadas
# - Tests pasan
# - Ningún archivo referencia directorio eliminado
```

---

**Este skill es el punto de entrada principal para todo el ecosistema integrado.**