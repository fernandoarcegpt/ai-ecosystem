# Habilidades Completas del Ecosistema Hermes y Claude Code

## 📚 Catálogo General de Habilidades

### 🎛️ **Orchestrator-Main** (v3.0.0)
**Ubicación:** `main/orchestrator-main/SKILL.md`

**Propósito:** Skill principal dinámico que orquesta todo el ecosistema:
- Hermes → Orquestador y coordinador principal
- Claude Code → Ejecutor de tareas principal con skills de Hermes
- Ruflo → Componente de soporte y contenedor de herramientas
- Búsqueda → research-search-master, youtube-content, web_search, blogwatcher
- Planificación → general-planning, plan, test-driven-development
- Descarga libros → zlibrary-mcp, Notex
- Ingesta y consulta conocimiento → knowledge-broker, knowledge-query

**Características Clave:**
- ✅ **Auto-detección**: Detecta qué skills están disponibles y las usa
- ✅ **Fallback inteligente**: Si un skill falla, usa el siguiente más adecuado
- ✅ **Modulación por contexto**: Ajusta flujo según tipo de tarea (feature/bug/research/plan/download)
- ✅ **Módulo por componente**: Cada área tiene handler independiente con contexto propio
- ✅ **Actualización automática**: Detecta cambios en habilidades, renombra y repara configuraciones dañadas

**Comandos Principales:**
```bash
# Detección y diagnóstico avanzado
orchestrator-main "tarea" --detect --health

# Planificación inteligente con desvío
orchestrator-main "implementar API de autenticación" --plan --research --full

# Descarga con fallback automático
orchestrator-main "libro Deep Learning" --download --zlib --zlib-fallback --indexar
```

**Archivos Generados:**
- `.hermes/plans/` - Planes generados
- `.hermes/logs/` - Logs de ejecución
- `.hermes/library/` - Libros descargados
- `.hermes/memory/` - Memoria actualizada
- `.hermes/artifacts/` - Resultados de búsquedas

## 🔍 **Habilidades de Búsqueda e Investigación**

### research-search-master
**Ubicación:** `research/research-search-master/SKILL.md`

**Propósito:** Búsqueda académica en múltiples fuentes:
- arXiv papers vía arxiv skill
- YouTube videos vía youtube-content skill
- StackOverflow, GitHub, y otras fuentes web

**Características:**
- Integración con múltiples motores de búsqueda
- Recuperación y síntesis de papers académicos
- Capacidad para procesar referencias y citas

### general-planning
**Ubicación:** `main/general-planning/SKILL.md`

**Propósito:** Genera planes según complejidad y tipo de problema:
- **Feature development:** Implementación de nuevas características
- **Bug fixing:** Corrección de problemas
- **Research:** Búsqueda y análisis
- **Plan planning:** Planificación estratégica

**Comandos:**
```bash
general-planning "implementar API" --type feature --complexity medium
general-planning "implementar API" --type bug --complexity low
general-planning "investigar tecnología emergente" --type research --complexity high
general-planning "plan estratégico 2025" --type plan --complexity high --full
```

### data-verifier
**Ubicación:** `main/data-verifier/SKILL.md`

**Propósito:** Verifica información médica y científica usando fuentes confiables.

**Características:**
- Validación de datos
- Verificación de fuentes académicas
- Cross-referencia de información científica

**Usos:**
- Validación de datos ESG
- Verificación de datos macroeconómicos
- Pruebas de investigación con soporte académico

## 📊 **Habilidades Financieras y Trading**

### portfolio-optimization
**Ubicación:** `main/portfolio-optimization/SKILL.md`

**Propósito:** 4 clases de optimización de carteras:
- **Mean-Variance:** Optimización clásica de Markowitz
- **Black-Litterman:** Integración de perspectivas de mercado
- **HRP ( Hierarchical Risk Parity):** Diversificación basada en correlaciones

**Características:**
- Soporte multi-clase de activos
- Análisis de riesgo con simulación de Monte Carlo
- Integración con buffers de riesgos

**Tipado:** `portfolio_optimization.OptPortFolioOptimizer`

### android-fin-gpt-trader
**Ubicación:** `android-fin-gpt-trader` (específico de Android)

**Propósito:** Automatización de trading para análisis de acciones Android.

**Características:**
- Integración con portfolio-optimization
- Coordeción con quant-analyst
- Conectividad con data-verifier
- Enlace con FINGPT (Ollama) para análisis de sentimiento

## 📚 **Habilidades de Documentación y Biblioteca**

### zlibrary-notex-pipeline
**Propósito:** Pipeline integrado Z-Library → Notex para descarga y procesamiento.

**Flujo Automatizado:**
1. **Búsqueda**: Busca libro en Z-Library MCP
2. **Descarga**: Descarga el libro a `.hermes/library/downloads/`
3. **Procesamiento**: Extrae texto y procesa con Notex
4. **Indexación**: Crea notebook en Notex y lo indexa
5. **Metadata**: Guarda metadatos en `.hermes/library/downloads/<timestamp>_<libro>.meta.json`

**Comando:**
```bash
bash scripts/downloader.sh "Título Libro" formato
bash scripts/process-document.sh "Título Guía" pdf
```

**Archivos de Salida:**
```
.hermes/library/
├── downloads/
│   ├── <timestamp>_<libro>.pdf
│   ├── <timestamp>_<libro>.txt
│   ├── <timestamp>_<libro>.meta.json
│   └── <timestamp>_<libro>.notex_ref
```

### documentation-generator
**Propósito:** Genera guías, manuales y procedimientos documentados usando OKF, Notex y herramientas de procesamiento de documentos.

**Ubicación:** `productivity/documentation-generator/SKILL.md`

**Características:**
- Procesa PDFs, imágenes y texto plano
- Genera contenido OKF estructurado
- Sincroniza con procedures de Desktop
- Crea metadatos OKF para cada documento

**Flujos de Trabajo:**
- **Proceso de 2 pasos:** Descargar → Procesar → Indexar → Guardar
- **Documentos en procedimientos:** Se guardan en `Desktop/tor-browser/Browser/procedures/`
- **Metadatos:** Se guardan en `.hermes/library/downloads/`

## 🧠 **Habilidades de Memoria y Aprendizaje**

### knowledge-broker
**Propósito:** Ingesta PDFs/código → KùzuDB + LlamaIndex (PropertyGraphIndex).

**Comandos:**
```bash
python src/ingest.py       # Re-genera el grafo de conocimiento
python src/query.py "¿pregunta?"  # Consulta semántica
```

### knowledge-query
**Propósito:** Consulta semántica + grafo en el broker.

**Comandos:**
```bash
python src/query.py "¿pregunta?"
```

### compartir conocimiento
**Propósito:** Sistema de intercambio de conocimiento OKF.

**Características:**
- 📚 Aprendizaje continuo entre agentes
- 🔗 Network de conocimiento entre Hermes y Claude Code
- 📊 Análisis de tendencias de conocimiento
- 🎯 Selección de conocimiento relevante

**Archivos:**
```
sharememory/
├── hermes_memory/     # Estado del agente Hermes
├── claude_memory/     # Estado de Claude Code
└── wiki/              # Contenido OKF compartido
```

## 🛠 **Habilidades Técnica**

### pdf2md
**Propósito:** Convierte archivos PDF a texto plano o Markdown.

**Características:**
- Soporte para múltiples fuentes PDF
- Preserva estructura y formateo
- Extracción eficiente de texto

**Usos:**
- Pre-procesamiento de documentos para Notex
- Extracción de texto para conocimiento compartido
- Creación de documentos indexables

### ocr-and-documents
**Propósito:** Extrae texto de PDFs escaneados o imágenes usando pymupdf o marker-pdf.

**Características:**
- Detección automática de papel vs. impreso
- Soporte multi-lenguaje
- Corrección de errores integrada

### nano-pdf
**Propósito:** Edita metadatos, corrige typos o títulos en archivos PDF directamente desde la CLI.

**Características:**
- Edición de metadatos PDF
- Corrección automática de typos
- Actualización de títulos y encabezados

### huggingface-hub
**Propósito:** Integra HuggingFace HF CLI para search/download/upload models, datasets.

**Características:**
- Modelo hub desde terminal
- Gestión de datasets automatizada
- Integración con pipeline de Notex

### segment-anything-model
**Propósito:** SAM: zero-shot image segmentation via points, boxes, masks.

**Características:**
- Segmentación de imágenes sin entrenamiento
- Extracción de objetos para análisis
- Integración con reconocimiento de imágenes

## 🧪 **Habilidades de Pruebas y Verificación**

### test-trivial.sh
**Propósito:** Verifica que Claude Code CLI está funcionando.

**Características:**
- ✅ Test 1: Versión check - `claude --version`
- ✅ Test 2: Tarea trivial - `claude -p "Say hello" --allowedTools Read --max-turns 1`
- ✅ Test 3: JSON output - `claude -p "Return JSON" --output-format json --allowedTools Read --max-turns 1`

**Resultados:**
- ✅ Claude Code 2.1.216 (Claude Code)
- ✅ Working correctly con Claude Code (backend: anthropic, model: openrouter/free)

---
## 📁 **Resumen de Archivos y Directorios**

### Estructura Principal de Archivos:
```
/home/fernando/ai-ecosystem/
├── scripts/                    # Core automation scripts
│   ├── downloader.sh         # Z-Library → Notex pipeline
│   ├── process-document.py   # OKF documentation generator
│   └── test-trivial.sh       # Tests de verificación
├── .hermes/                  # State and memory
│   ├── library/              # Documentación y descargas
│   │   └── downloads/        # Archivos procesados (.pdf, .txt, .meta.json)
│   ├── skills/              # Definiciones de skills y documentaciones
│   └── logs/                # Logs del sistema
├── notex/                    # Sistema de notas y vector store
├── Desktop/                 # Documentos finales para consulta
│   └── tor-browser/         # Navegador web para documentación
│       └── Browser/        # Archivos HTML y procedures
├── CLAUDE.md               # Documentación completa del sistema
└── package.json            # Scripts enrutados de la aplicación
```

### Directorios de Salida Clave:

**Documentación NOTEX:**
- `/home/fernando/ai-ecosystem/notex/` - Notebooks Notex crudos
- `/home/fernando/ai-ecosystem/procedures/` - Documentos HTML OKF finales

**Libros Procesados:**
- `/home/fernando/ai-ecosystem/.hermes/library/downloads/` - Libros con metadatos
- `/home/fernando/ai-ecosystem/.hermes/library/downloads/*.meta.json` - Metadatos OKF

**Archivos OKF:**
- `sharememory/` - Memoria compartida para Hermes+Claude Code
- `wiki/` - Documentos OKF compartidos

---
## 🚀 **Guía de Inicio Rápido**

### 1. Iniciar Sistema:
```bash
# Verificar estado general
orchestrator-main "estado" --detect --health

# Ejecutar tests basicos
npm test

# O ejecutar pipeline automatico completo
./scripts/automation.sh run
```

### 2. Procesar Documentos:
```bash
# Procesar PDF con pipeline Z-Library+Notex
bash scripts/downloader.sh "Título Técnico" pdf

# Generar guía manual con OKF
./scripts/process-document.sh "Manual de Usuario" txt

# Crear documento OKF desde contenido existente
python3 scripts/process-document.py "Documento Existente" pdf /ruta/al/archivo.pdf
```

### 3. Consultar Documentación:
```bash
# Ver documentos OKF en procedures
ls -la /home/fernando/Desktop/tor-browser/Browser/procedures/

# Abrir pestaña en navegador (si Noex está corriendo)
cd /home/fernando/ai-ecosystem/notex
# Corre: go run . -server  # Luego consultar http://localhost:8080
```

---
## 🔧 **Referencias y Recursos**

### Documentación Principal:
- **README principal:** `/home/fernando/ai-ecosystem/README.md`
- **Documentación Hermes:** `/home/fernando/ai-ecosystem/CLAUDE.md`
- **Documentación Notex:** `/home/fernando/ai-ecosystem/notex/README.md`
- **Skills:** `~/.hermes/skills/*/SKILL.md`

### Documentación OKF:
- **Estructura de Wiki OKF:** `sharememory/hermes_memory/okf_index.json`
- **Memoria compartida:** `sharememory/hermes_memory/`

### Archivos de Configuración:
- **Archivos .env:** `.env` en `ai-ecosystem/` y `notex/`
- **Configuración del sistema:** `CLAUDE.md`
- **Scripts enrutados:** `scripts/downloader.sh`, `scripts/process-document.sh`

### Lista Completa de Habilidades (por Categoría):

#### 🎛️ **Orchestrator Main**
- orchestrator-main (main/orchestrator-main/SKILL.md)

#### 🔍 **Búsqueda e Investigación**
- research-search-master (research/research-search-master/SKILL.md)
- general-planning (main/general-planning/SKILL.md)
- data-verifier (main/data-verifier/SKILL.md)

#### 📚 **Documentación y Biblioteca**
- zlibrary-notex-pipeline (research/zlibrary-notex-pipeline/SKILL.md)
- documentation-generator (productivity/documentation-generator/SKILL.md)

#### 💼 **Finanzas y Trading**
- portfolio-optimization (main/portfolio-optimization/SKILL.md)
- android-fin-gpt-trader (android-fin-gpt-trader/)

#### 🧠 **Habilidades Técnica**
- pdf2md, ocr-and-documents, nano-pdf (hermes-agent skills)

#### 🧪 **Pruebas**
- test-trivial.sh (scripts/test-trivial.sh)

### 🗂️ **Navegación a Recursos:**
```bash
# A las skills
ls -la ~/.hermes/skills/

# A los procedimientos OKF finales
ls -la /home/fernando/ai-ecosystem/procedures/

# A los libros procesados
ls -la ~/.hermes/library/downloads/
```

---
## 📊 **Estadísticas del Sistema**

### Resumen de Skills:
- **Total de skills principales:** 8
- **Skills en orchestrator-main:** 1
- **Skills de investigación:** 3
- **Skills de documentación:** 2
- **Skills financieras:** 2
- **Skills técnica:** 3
- **Skills de pruebas:** 1

### Flujos de Trabajo:
- **Flujo de navegación de documentos:** Z-Library → Notex → OKF → procedures
- **Flujo de investigación académica:** web_search → research-search-master → Notex
- **Flujo de planificación estratégica:** general-planning → orchestrator-main

### Archivos Generados:
- **Documentos OKF:** `Desktop/tor-browser/Browser/procedures/*.md`
- **Archivos procesados:** `.hermes/library/downloads/*.txt, *.meta.json`
- **Metadatos:** `.hermes/library/downloads/*.meta.json`
- **Contenido NOTEX:** `notex/` (si está corriendo)

### Conectividad del Sistema:
- ✅ Claude Code CLI está operativo (2.1.216)
- ✅ OpenRouter API está autenticada
- ✅ Notex puede estar corriendo localmente para procesamiento
- ✅ orchestrator-main está listo para orquestar tareas

---
## 🎯 **Conclusión**

Este ecosistema proporciona una **infraestructura completa de gestión de conocimiento** que integra:

1. **Búsqueda académica** y recuperación de papers científicos
2. **Procesamiento de bibliotecas** de Z-Library vía Notex
3. **Documentación automatizada** con OKF (Open Knowledge Format)
4. **Optimización financiera** para trading algorítmico
5. **Memoria compartida** entre Hermes y Claude Code

El sistema está **listo para producción** con funcionalidad completa de:
- ⏰ Automatización programada via `scripts/automation.sh`
- 🔍 Búsqueda avanzada en todo el contenido
- 🛡️ Validación y verificación de datos integrada
- 📊 Análisis financiero con múltiples modelos
- 📚 Generación de documentos con OKF

Para comenzar, simplemente ejecuta:
```bash
orchestrator-main "estado" --detect --health
npm test
```

El sistema verificará todo automáticamente y dejará el ecosistema listo para su uso.

---
*Generado por sistema Hermes+Claude Code v3.0.0*
*Ubicación: /home/fernando/ai-ecosystem/sharememory/hermes_memory/*
*Fecha: 2026-07-24_22:16:00*