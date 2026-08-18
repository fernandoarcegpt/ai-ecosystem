# �� 📖 Tutorial de Instalación: Integración de Razonamiento Simbólico para Hermes Agent

> **Estado: histórico y reemplazado.** Use `README.md` y
> `npm run test:hermes-cli` para la instalación y verificación actuales.

## �� 🎯 Objetivo
Esta guía te enseñará a instalar y configurar la integración de razonamiento simbólico en Hermes Agent, permitiendo que tu asistente AI entienda y resuelva automáticamente consultas sobre reglas, restricciones, dependencias y situaciones de revisión humana.

## �� 📋 Requisitos Previos
Antes de comenzar, asegúrate de tener:
- � ✅ Sistema operativo: Linux, macOS o Windows (con WSL o PowerShell)
- � ✅ Python 3.8 o superior instalado
- � ✅ Acceso a terminal/Línea de comandos
- � ✅ Conexión a internet para descargar paquetes
- � ✅ Token de API de OpenRouter (obtenlo gratis en [openrouter.ai](https://openrouter.ai))

### Verificar Python y pip
Abre tu terminal y ejecuta:
```bash
python3 --version
pip3 --version
```
Deberías ver algo como:
```
Python 3.10.6
pip 23.0.1
```

## �� 🔧 Paso 1: Instalar Dependencias Necesarias

La integración requiere tres paquetes especializados de Python:
- `networkx`: Para análisis de grafos y dependencias
- `z3-solver`: Para resolución de restricciones lógicas y matemáticas
- `pydatalog`: Para razonamiento basado en reglas y lógica

### En Linux/macOS:
Abre una terminal y ejecuta:
```bash
pip3 install networkx z3-solver pydatalog
```

### En Windows (PowerShell):
Ejecuta como administrador:
```powershell
pip install networkx z3-solver pydatalog
```

**Nota:** Si ves errores de permisos, usa `pip3 install --user ...` en Linux/macOS o ejecuta PowerShell como administrador en Windows.

## �� 📁 Paso 2: Crear Estructura de Directorios para Hermes

Hermes almacena sus habilidades (skills) en `~/.hermes/skills/`. Necesitamos crear la carpeta para nuestra skill de razonamiento simbólico.

### En Linux/macOS:
```bash
mkdir -p ~/.hermes/skills/reasoning/
```

### En Windows (PowerShell):
```powershell
New-Item -ItemType Directory -Path "$env:USERPROFILE\.hermes\skills\reasoning" -Force
```

## �� 📄 Paso 3: Descargar e Instalar el Archivo SKILL.md

El archivo `SKILL.md` contiene toda la configuración necesaria para que Hermes reconozca y use nuestra integración.

### Opción A: Copiar desde el repositorio (recomendado)
Si tienes acceso al proyecto donde se encuentra el archivo original:
```bash
# Desde la carpeta del proyecto
cp $HOME/ai-ecosystem/skills/reasoning/hermes-symbolic-integration/SKILL.md ~/.hermes/skills/reasoning/
```

### Opción B: Crear manualmente
Si no tienes acceso al archivo original, crea el archivo manualmente:

1. Abre tu editor de texto favorito (Notepad, TextEdit, VS Code, etc.)
2. Copia y pega el siguiente contenido exactamente como aparece:
```
---
name: hermes-symbolic-integration
description: Integration of neuro-symbolic reasoning router with Hermes chat pipeline
version: 1.0.0
author: System
category: reasoning
tags:
  - reasoning
  - integration
  - semantic-router
  - z3
  - networkx
  - pydatalog
  - constraints
  - human_review
dependencies:
  - networkx
  - z3-solver
  - pydatalog
triggers:
  - semantic_routing
  - symbolic_reasoning
  - constraint_solving
  - graph_analysis
  - rule_validation
  - human_review
---

# Hermes Symbolic Integration

This skill provides automatic neuro-symbolic reasoning integration with the Hermes chat pipeline. It intercepts user queries and routes them to appropriate symbolic engines (Z3, NetworkX, PyDatalog) based on semantic analysis.

## Architecture

```
�┌─────────────────────────────────────────────────────────────�┐
│                    Hermes Chat Pipeline                     │
�└─────────────────────────────────────────────────────────────�┘
                              │
                              � ▼
�┌─────────────────────────────────────────────────────────────�┐
│              semantic_router.classify_task_structure        │
│                                                             │
│  Analyzes query strings → mode + engine + confidence        │
�└─────────────────────────────────────────────────────────────�┘
                              │
           � ┌──────────────────�┼──────────────────�┐
           � ▼                  � ▼                  � ▼
    � ┌──────────�┐      � ┌──────────�┐      � ┌──────────�┐
    │   LLM    │      │  Z3/SMT  │      │NetworkX  │
    │(llm_only)│      │(constraints│      │  (graph) │
    │          │      │ / rules) │      │          │
    └──────────�┘      └──────────�┘      └──────────�┘
           │                  │                  │
           └──────────────────�┼──────────────────�┘
                              � ▼
�┌─────────────────────────────────────────────────────────────�┐
│              Result Integration + Final Response          │
�└─────────────────────────────────────────────────────────────�┘
```

## Modes

| Mode | Engine | Description |
|------|--------|-------------|
| `llm_only` | none | Simple queries, no symbolic reasoning |
| `rules` | z3 | Logical rule validation, permission checks |
| `constraints` | z3 | Assignment, budget, resource allocation |
| `graph` | networkx | Dependency cycles, path analysis |
| `human_review` | none | Missing critical information |

## Installation

```bash
# Install dependencies
pip install networkx z3-solver pydatalog

# Copy skill to Hermes profile
cp ~/.hermes/skills/hermes-symbolic-integration $HOME/.hermes/skills/reasoning/
```

## Usage from CLI

```bash
# Simple query (LLM only)
hermes chat -q "What is Hermes Agent?"

# Rule-based query
hermes chat -q "Rule: editors can only read files. Ana is an editor. Can she modify config.yaml?"

# Constraint-based query
hermes chat -q "Assign tasks A,B,C among Ana,Luis,Marta with constraints..."

# Graph-based query
hermes chat -q "A depends on B, B depends on C, C depends on A. Valid order?"

# Human review query
hermes chat -q "Distribute 10 users among 5 teams but no budget info"
```

## Integration Points

The skill integrates via two main entry points:

1. `hermes_auto_detect_and_reason()` - Auto-triggering for contextual analysis
2. `hermes_explicit_symbolic_reasoning()` - Explicit symbolic reasoning requests

Both functions are exposed through `hermes_integration.py` and called automatically during chat processing.

## Output Format

When symbolic reasoning activates, output includes trace markers:

```
[reasoning-router]
mode=<mode_name>
engine=<engine_name|none>
executed=<true|false>
result=<result_token>
evidence=<brief_explanation>
```

## Testing

Run the built-in tests:

```bash
python test_symbolic_integration.py
```

All 5 tests should pass with expected modes and engines.
```

3. Guarda el archivo como: `SKILL.md`  
   **Ubicación importante:**  
   - Linux/macOS: `~/.hermes/skills/reasoning/SKILL.md`  
   - Windows: `%USERPROFILE%\.hermes\skills\reasoning\SKILL.md`

## �� ⚙��️ Paso 4: Configurar Hermes Agent

Necesitamos indicarle a Hermes que use nuestra nueva skill.

### Abrir archivo de configuración
- Linux/macOS: `nano ~/.hermes/config.yaml`
- Windows: Abre `%USERPROFILE%\.hermes\config.yaml` con Bloc de notas

### Asegúrate de que tenga estas líneas (o agréguelas si no existen):
```yaml
profile: default
model: openrouter/free
language: es
features:
  symbolic_reasoning: true
```

### Guardar y cerrar el archivo
- En nano: `Ctrl+O`, `Enter`, `Ctrl+X`
- En Bloc de notas: `Archivo > Guardar`

## �� 🧪 Paso 5: Verificar la Instalación

¡Ahora es momento de probar si todo funciona correctamente!

### Comando de prueba 1: Consulta de revisión humana
Ejecuta en tu terminal:
```bash
hermes chat -q "Distribuye diez usuarios entre cinco equipos sin superar un presupuesto total, pero no conocemos los costos de asignación."
```

**Deberías ver una respuesta similar a esta:**
```
[reasoning-router]
mode=human_review
engine=none
confidence: 0.8
matched_patterns: ['no conocemos']
Lo siento, pero no tengo suficiente información para resolver este problema de asignación. Necesitaría conocer los costos de asignar cada usuario a cada equipo para poder determinar una distribución óptima que no supere el presupuesto total.
```

### Comando de prueba 2: Consulta lógica (reglas)
```bash
hermes chat -q "Regla: los editores solo pueden leer archivos. Ana es editora. ¿Puede Ana modificar config.yaml?"
```

**Respuesta esperada:**
```
[reasoning-router]
mode=rules
engine=z3
confidence: 0.9
No, Ana no puede modificar config.yaml porque según la regla, los editores solo tienen permiso para leer archivos, no para modificarlos.
```

### Comando de prueba 3: Consulta de dependencias (grafo)
```bash
hermes chat -q "La tarea A depende de B, la tarea B depende de C y la tarea C depende de A. ¿Existe un orden válido de ejecución?"
```

**Respuesta esperada:**
```
[reasoning-router]
mode=graph
engine=networkx
confidence: 0.85
No existe un orden válido de ejecución porque hay un ciclo circular: A → B → C → A. Para resolver esto, sería necesario eliminar al menos una dependencia.
```

### Comando de prueba 4: Consulta simple (solo LLM)
```bash
hermes chat -q "¿Qué es Hermes Agent en una oración?"
```

**Respuesta esperada:**
```
Hermes Agent es un asistente de IA modular y extensible que combina modelos de lenguaje grandes con capacidades de razonamiento simbólico especializado.
```
*(Esta respuesta NO mostrará trazas [reasoning-router] porque es una consulta simple que no requiere razonamiento simbólico)*

## �� 📊 Paso 6: Qué Esperar en las Respuestas

Cuando Hermes use el razonamiento simbólico, verás este formato en sus respuestas:

```
[reasoning-router]
mode=<nombre_del_modo>
engine=<nombre_del_motor>
confidence: <valor_entre_0_y_1>
matched_patterns: [<patrones_detectados>]
<respuesta_del_asistente>
```

### Los modos posibles son:
- `llm_only`: Consulta simple (no muestra motor)
- `rules`: Para validar reglas y permisos (usa Z3)
- `constraints`: Para asignación y limitaciones (usa Z3)
- `graph`: Para dependencias y ciclos (usa NetworkX)
- `human_review`: Cuando falta información crítica (no ejecuta motor)

## �� 🛠��️ Solución de Problemas Comunes

| Problema | Posible Causa | Solución |
|----------|---------------|----------|
| `ModuleNotFoundError: No module named 'networkx'` | Dependencias no instaladas | Ejecuta `pip3 install networkx z3-solver pydatalog` |
| `Command not found: hermes` | Hermes Agent no instalado | Sigue la instalación en [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs) |
| No aparecen trazas `[reasoning-router]` | Skill no cargada correctamente | Verifica que `SKILL.md` esté en `~/.hermes/skills/reasoning/` |
| Respuesta en inglés invece de español | Configuración de idioma incorrecta | Asegúrate de que `language: es` esté en `config.yaml` |
| Error de autenticación con OpenRouter | Token API faltante o incorrecto | Configura `ANTHROPIC_AUTH_TOKEN` en tu entorno o en `.hermes/.env` |

### Verificar instalación de dependencias
Ejecuta:
```bash
python3 -c "import networkx, z3, pydatalog; print('Todas las dependencias están instaladas')"
```
Si no ves errores, las dependencias están correctamente instaladas.

## �� 🎉 ¡Felicidades!
Has instalado con éxito la integración de razonamiento simbólico en Hermes Agent. Ahora tu asistente podrá:
- �� 🔍 Detectar automáticamente cuándo necesita usar razonamiento lógico especializado
- �� ⚖��️ Resolver problemas de restricciones usando solvers matemáticos
- �� 🔄 Analizar dependencias y detectar ciclos en grafos
- �� 🚨 Alertarte cuando falta información crítica para tomar una decisión
- �� 💬 Proporcionar respuestas más precisas y fundamentadas

## �� 📚 Próximos Pasos Sugeridos

1. **Experimenta con tus propias consultas:** Prueba preguntas como:
   - "Si todos los hombres son mortales y Sócrates es hombre, ¿Sócrates es mortal?"
   - "Necesito asignar 5 proyectos a 3 desarrolladores sin que ninguno tenga más de 2 proyectos"
   - "El proceso A debe terminar antes de B, y B antes de C. ¿Puedo empezar con C?"

2. **Explora la skill técnica:** Revisa el contenido completo en `~/.hermes/skills/reasoning/SKILL.md`

3. **Únete a la comunidad:** Visita los foros de Hermes Agent para compartir tus experiencias y aprender de otros usuarios

---
*¿Necesitas ayuda adicional? No dudes en consultar la documentación oficial de Hermes Agent en [https://hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs) o preguntar en los canales de soporte comunitario.*
