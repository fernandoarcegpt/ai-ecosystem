---
name: system-directives
description: "System directives for when to execute reasoning, Claude Code (via delegation), information lookup, and orchestration. All decisions are based on work type, context, and health of the ecosystem."
platforms: [linux, macos, windows]
tags: [directives, system, governance, change-management]
version: 1.1.0
author: Hermes Agent
license: MIT
---

# System Directives – Orchestration Timing & Action Rules

> **Estado: reemplazado.** Las reglas vigentes están en `CLAUDE.md` y
> `agents/hermes/SOUL.md`. Consulte `docs/DOCUMENTATION_INDEX.md` antes de usar
> los comandos históricos descritos aquí.

## 📌 Propósito

Estas directrices establecen **micro‑TIEMPO** para cada decisión de ejecución dentro del ecosistema de Hermes:

- **¿Cuándo yo (el agente principal) actúo?** – investigación de alto nivel, planificación, resolución de fallos, coordinación entre habilidades.
- **¿Cuándo delego a Claude Code (a través de `delegate_task`)?** – implementación de código, redacción de tests, corrección de errores, entrega de integraciones.
- **¿Cuándo consulto externalmente?** – búsqueda web, extraction, OCR, análisis de imágenes, cálculos de CLI, verificación del sistema de archivos.
- **¿Cuándo invoco `orchestrator-main`?** – detección de cambios, reparación del ecosistema, modificación persistente de habilidades, ejecución de auditorías completas.

## 🎯 Criterios clave de decisión

### 1. Responder / Actuar personalmente
**Criterios:**  
- Modificación conceptual, diseño o refactor de habilidades (including `SKILL.md` front‑matter).  
- Planificación por complejidad / tipo (habilidad `general-planning`); cualquier plan nuevo pasa primero por mi ciclo de procesamiento intelectual antes de ser delegado.  
- Resolución de problemas en el flujo general (including detección de fallbacks, coordinación entre habilidades, actualización de dependencias del ecosistema).  
- Decide si una habilidad necesita un emergency patch (includes ``skill_manage(action='patch')``) sin tooling separado.  

**Acciones:**  
- Utiliza `self-audit --audit` para validar el escenario.  
- Utiliza `skill_view`/`read_file`/`search_files` para investigación de contexto.  
- Persiste cambios con `skill_manage`, `write_file`, `patch`, `memory`, y `cronjob` si es necesario.  

### 2. Delegar a Claude Code (delegate_task)
**Criterios:**  
- Cualquier cosa que sea explícitamente mencionada en el prompt del usuario o en el ``goal`` del plan, con ``subagent_type`` estrictamente como ``coder`` o ``tester`` (ej. reparación de código, tests, comentarios de revisión de código).  
- Cuando ``delegate_task`` se menciona explícitamente en el prompt del usuario (ej., ``delega a Claude Code``).  
- Cuando ``task_type`` definido es ``coded`` o ``test`` en el micro‑plan (la matriz de complejidad se hace específica sobre tipos de recursos).  

**Micro‑plan ejemplo (para bug de baja complejidad):**  
``` 
1️⃣ Yo: crear plan con pasos detallados
2️⃣ Delegar: reparación de código (agente ``coder``)
3️⃣ Yo: probar reparación con ``orchestrator-main --health``
``` 

### 3. Consultar / Extraer externalmente
**Criterios:**  
- **Datos** vs **ideas** – para aportar nueva información de fuera del ecosistema (content webs, archivos, resultados de CLI, a través de ``web_search``, ``web_extract``, ``read_file``, ``search_files``, ``terminal``, ``computer_use``, ``vision_analyze``, ``video_analyze``, ``image_generate``).  
- **Verificación de hechos** – necesita respuestas actuales (ej. porqué falló un script, versión exacta de una lib, comando de CI exacto).  
- **Referencias externas** – cualquier dato que no esté en el repositorio actual, base de conocimientos interna o competencias propias de la habilidad del agente (`research-search-master`, `google-workspace`, etc.).  

**Cuando usar cada herramienta:**  
- ``web_search`` – preguntas generales del mundo, diagnóstico de problemas de dependencias, patrones.  
- ``web_extract`` – contenido específico de páginas, PDFs, arXiv papers.  
    - continúa con ``execute_code`` para análisis.  
- ``read_file`` / ``search_files`` – vista interna del sistema operativo; siempre primero para archivos locales.  
- ``terminal`` – ejecución en bash (ej. construcción, tests, scripts).  
- ``computer_use`` – inspección visual de interfaces, UI, openers de diálogo.  
- ``vision_analyze`` – imágenes en disco, capturas de pantalla, referencias visuales.  

### 4. Activar / Coordinar `orchestrator-main`
**Criterios:**  
- **Detección de cambios** (ej. ``git diff --name-only`` detecta que ``.md``, ``.sh``, ``.json`` han cambiado).  
- **Verificación de salud del ecosistema** – ``orchestrator-main \"verificar\" --health`` se ejecuta después de cualquier modificación del ecosistema.  
- **Reaparición / Fallbacks** – reparar cualquier habilidad rota o rotura de pipeline, ``orchestrator-main`` gerencia fallbacks automáticamente.  
- **Reparación de habilidades persistentes** – cuando una habilidad se ha vuelto obsoleta, rota, o necesita ser actualizada con nuevos pasos / fluff.  

## 🔄 Flujo de trabajo

### A. Flujo de trabajo **Planificador** (problema -> plan)

``` 
Problema (ej. "fuga de memoria") → 
🟢 - Yo: ejecutar ``orchestrator-main\"Planificar\" --type bug --complexity high --full`` (entra en modo de planificación)
🟡 - Delegar: agente ``coder`` (si el plan solicita reparación de código)
🟠 - Yo: después de que el coder termine, ejecutar ``orchestrator-main --health``, ``self-audit --audit``
✅ - Terminó solo si ambas fases lo aprobaron
``` 

### B. Flujo de trabajo **Search‑Dynamic** (búsqueda de información)

``` 
Petición (ej. "porqué el tests fallan") → 
🟢 - Yo: intentar ``terminal`` → ``execute_code`` para probar lo que puedo resolver localmente
🟡 - Detectar fallos → ``web_search`` / ``web_extract`` (si fuera del repo)
🟠 - Usar CLI de Hermes para cualquier verification de entorno (ej. ``hermes skills`` etc.)
✅ - Integrar hallazgos en plan si es necesario
``` 

### C. Flujo de trabajo **Download‑and‑Digester**

``` 
``downloader.sh`` ejecutado → 
🟢 - Yo: tracking de tarea con ``self-audit --detect`` and ``orchestrator-main --health``
🟡 - Fallback: si falla la descarga, usar ``web_search`` / ``web_extract`` o repositorios alternativos
🟠 - Persisitir contenido a ``memorwise`` si es exitoso, despues `orchestrator-main\"actualizar\"`
✅ - Revertir si el processing falla seguido de ``self-audit --audit``.
``` 

## 📍 Técnicas específicas

### Modulo 1: Habilidades y auditoría de cambios

```bash
# Modificación (ej. patching un skill)
... <directamente> ...

# Verificación obligatoria
orchestrator-main \"verificar\" --health && self-audit --audit

# Solo si ambas validaciones APRUEBAN el cambio, persistir en la cadena de Git / continuar.
``` 

### Modulo 2: Macros de delegate_task

``` 
# Cada macro incluye un plan básico antes de delegar.
# Comandos compuestos usados por mi directamente (sin agente) o a través de `delegate_task`.

# Ejemplo: Al corregir errores de linter (tipo de recurso --simple)
delegate_task(
    goal=\"Ejecutar linter en $HOME/.hermes/skills/software-development/general-planning/SKILL.md y corregir lint errors, tests y esquemas de código.\"
)
``` 

### Modulo 3: Web Search / Extract

```bash
# Siempre primero... intenta ver si se puede resolver localmente con read_file.
read_file $HOME/ai-ecosystem/README.md

# Si aun asi es insuficiente, buscar externo
web_search \"remitir un error luego de ejecucion git\"
``` 

### Modulo 4: CLI + Computer Use

```bash
# Empezar con: intento directo de CLI si se necesita un command para prueba.
terminal \"python -c 'import some_module; print(some_module.__version__)'\"

# Verificadores visuales (si se necesita) para dialogs, errores.
computer_use action='capture' app='Firefox'
``` 

## 📊 Resumen rápido (para usuario)

| Situación | Acción recomendada | Comando principal |
|-----------|-------------------|-------------------|
| **Plan de tarea nuevo** | Yo (planificación) | ``orchestrator-main \"planificar\" …`` |
| **Implementar / arreglar código** | Delegar a Claude Code | ``delegate_task`` con ``coder`` / ``tester`` |
| **Investigar / obtener hechos externos** | Consultar externalmente | ``web_search`` / ``web_extract`` / ``read_file`` / ``terminal`` |
| **Ejecutar reparación a nivel de habilidad / reparar ecosistema** | Activar orquestador maestro | ``orchestrator-main \"verificar\" --health`` + ``self-audit --audit`` |
| **Verificar consistencia de cambios** | Auditoría | ``self-audit --audit`` |

---

## 📌 Preferencias del usuario

- **Idioma**: Español obligatorio en todas las respuestas.  
- **Tono**: Directo, práctico, sin verbosidad innecesaria.  
- **Extensión**: Respuestas concisas, al grano. No explicaciones extemporáneas.  
- **Formato**: Listas breves cuando añaden claridad, pero sin verbosidad extra.  

---

## 📍 Técnicas específicas

*(El resto del contenido original permanece sin cambios; se mantiene para referencia completa.)*

--- 

## 📊 Resumen rápido (para usuario)

| Situacion | Acción recomendada | Comando principal |
|-----------|-------------------|-------------------|
| **Plan de tarea nuevo** | Yo (planificación) | ``orchestrator-main \"planificar\" …`` |
| **Implementar / arreglar código** | Delegar a Claude Code | ``delegate_task`` con ``coder`` / ``tester`` |
| **Investigar / obtener hechos externos** | Consultar externalmente | ``web_search`` / ``web_extract`` / ``read_file`` / ``terminal`` |
| **Ejecutar reparación a nivel de habilidad / reparar ecosistema** | Activar orquestador maestro | ``orchestrator-main \"verificar\" --health`` + ``self-audit --audit`` |
| **Verificar consistencia de cambios** | Auditoría | ``self-audit --audit`` |

--- 

## 📍 Técnicas específicas

*(El resto del contenido original permanece sin cambios; se mantiene para referencia completa.)*
