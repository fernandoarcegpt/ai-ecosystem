# Habilidades Configuradas en Hermes y Claude Code

## 📚 Orquestador Principal

### orchestrator-main
**Propósito:** Skill principal dinámico que orquesta todo el ecosistema.

**Ubicación:** `main/orchestrator-main/SKILL.md`

**Características Clave:**
- Auto-detección de skills disponibles
- Fallback inteligente entre herramientas
- Modulación por contexto (feature/bug/research/plan/download)
- Actualización automática de configuraciones

**Comandos:**
```bash
orchestrator-main "tarea" --full
orchestrator-main "tarea" --detect --health
orchestrator-main "tarea" --plan --research
```

---

## 🔍 Búsqueda e Investigación

### research-search-master
**Propósito:** Búsqueda integrada (arXiv, YouTube, StackOverflow, GitHub).

**Comandos:**
```bash
orchestrator-main "error X" --search [stackoverflow,youtube]
orchestrator-main "investigar tema" --research --full
```

### general-planning
**Propósito:** Genera planes según complejidad y tipo de problema.

**Comandos:**
```bash
general-planning "implementar API" --type feature --complexity medium
general-planning "corregir bug" --type bug --complexity low
```

---

## 📚 Documentación y Manuales

### zlibrary-notex-pipeline
**Propósito:** Pipeline integrado Z-Library → Notex para descarga y procesamiento.

**Ubicación:** `research/zlibrary-notex-pipeline/SKILL.md`

**Comandos:**
```bash
bash scripts/downloader.sh "Deep Learning" pdf
bash scripts/process-document.sh "Guía Técnica" pdf
```

### documentation-generator
**Propósito:** Genera guías, manuales y procedimientos documentados usando OKF, Notex y herramientas de procesamiento.

**Ubicación:** `productivity/documentation-generator/SKILL.md`

**Comandos:**
```bash
./scripts/process-document.sh "Título" formato [ruta_entrada]
python3 scripts/process-document.py "Título" formato
```

**Salida:** Archivos en `/home/fernando/Desktop/tor-browser/Browser/procedures/`

---

## 🔍 Verificación y Validación

### data-verifier
**Propósito:** Verifica información médica y científica usando fuentes confiables.

**Uso:** Validación de datos ESG y macroeconómicos.

**Comandos:**
```bash
# Usado internamente por orchestrator-main
# Para datos financieros:
orchestrator-main "analizar datos ESG" --verify
```

---

## 📊 Finanzas y Trading

### portfolio-optimization
**Propósito:** Optimización de carteras (Mean-Variance, Black-Litterman, HRP).

**Uso:** Usado por android-fin-gpt-trader.

**Comandos:**
```bash
# Integrado en android-fin-gpt-trader
# Ejemplo de uso:
python3 -c "from portfolio_optimization import optimize_portfolio; optimize_portfolio(risk_model='hrp')"
```

### android-fin-gpt-trader
**Propósito:** Automatización de trading para Android.

**Skill creada:** `android-fin-gpt-trader`

**Ubicación:** `android-fin-gpt-trader`

**Características:**
- Coordina portfolio-optimization, quant-analyst, data-verifier
- Usa FINGPT (Ollama) para análisis de acciones
- Funciona con orchestrator-main para workflows

---

## 🧠 Memoria y Aprendizaje

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

---

## 🛠 Herramientas Integradas

### pdf2md
**Propósito:** Convierte PDFs a texto plano o Markdown.

**Uso:** Procesamiento de documentos en workflow.

### ocr-and-documents
**Propósito:** Extrae texto de PDFs escaneados/imagenes.

**Uso:** Cuando markitdown o pdftotext fallan.

### nano-pdf
**Propósito:** Edita metadatos, corrige typos o títulos en PDFs.

**Uso:** Post-procesamiento de archivos descargados.

---

## 🧪 Pruebas y Verificación

### test-trivial.sh
**Propósito:** Verifica que Claude Code CLI está funcionando.

**Comandos:**
```bash
npm test  # Ejecuta: bash scripts/test-trivial.sh
```

---

## 📁 Estructura de Archivos

```
/home/fernando/ai-ecosystem/
├── scripts/
│   ├── downloader.sh          # Descarga Z-Library → Notex
│   ├── process-document.py  # Generador de documentos OKF
│   └── test-trivial.sh      # Tests básicos
├── .hermes/library/
│   └── downloads/             # Archivos procesados
├── notex/                   # Sistema de notas Notex
└── Desktop/tor-browser/Browser/procedures/  # Documentos finales
```

---

## 🚀 Flujo de Trabajo Recomendado

1. **Verificar skills:**
   ```bash
   orchestrator-main "estado" --detect --health
   ```

2. **Ejecutar tests:**
   ```bash
   npm test
   ```

3. **Crear documentación:**
   ```bash
   ./scripts/process-document.sh "Manual de Usuario" pdf
   ```

4. **Procesar libros:**
   ```bash
   bash scripts/downloader.sh "Deep Learning" pdf
   ```

5. **Consultar documentos:**
   - Abrir `http://localhost:8080` en Notex
   - Buscar en `/home/fernando/Desktop/tor-browser/Browser/procedures/`

---

## 📖 Referencias

- **Skill documentation:** `~/.hermes/skills/*/SKILL.md`
- **Project documentation:** `/home/fernando/ai-ecosystem/CLAUDE.md`
- **Notex documentation:** `/home/fernando/ai-ecosystem/notex/README.md`