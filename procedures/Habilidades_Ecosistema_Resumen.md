# Habilidades del Ecosistema Hermes y Claude Code

## 📚 Skills Principales por Categoría

### 🎛️ **Orquestador Principal**
- **orchestrator-main** - Coordina todo el ecosistema (v3.0.0)

### 🔍 **Búsqueda e Investigación**
- **research-search-master** - Búsqueda académica (arXiv, YouTube, StackOverflow, GitHub)
- **general-planning** - Genera planes según complejidad
- **data-verifier** - Verifica información médica y científica

### 📚 **Documentación y Biblioteca**
- **zlibrary-notex-pipeline** - Pipeline Z-Library → Notex
- **documentation-generator** - Genera guías/manuales con OKF

### 💼 **Finanzas y Trading**
- **portfolio-optimization** - Optimización de carteras (Mean-Variance, Black-Litterman, HRP)
- **android-fin-gpt-trader** - Automatización de trading Android

### 🧠 **Memoria y Aprendizaje**
|- **knowledge-broker** - Ingesta PDFs/código → KùzuDB + LlamaIndex
|- **knowledge-query** - Consulta semántica + grafo en el broker
|- **compartir-conocimiento** - Sistema OKF de intercambio

### 🛠 **Técnicas**
- **pdf2md** - Convierte PDF a Markdown
- **ocr-and-documents** - Extrae texto de imágenes/PDFs escaneados
- **nano-pdf** - Edita metadatos PDF
- **huggingface-hub** - Modelos y datasets
- **segment-anything-model** - Segmentación de imágenes

### 🧪 **Pruebas**
- **test-trivial.sh** - Verifica Claude Code CLI

---

## 🚀 Flujos de Trabajo Clave

### 1. Procesar Documento con OKF
```bash
./scripts/process-document.sh "Título" formato
python3 scripts/process-document.py "Título" formato
```

### 2. Pipeline Z-Library → Notex
```bash
bash scripts/downloader.sh "Libro Técnico" pdf
```

### 3. Verificar Estado del Sistema
```bash
orchestrator-main "estado" --detect --health
npm test
```

### 4. Crear Plan de Trabajo
```bash
general-planning "objetivo" --type feature --complexity medium
```

---

## 📁 Archivos Generados

| Tipo | Ubicación |
|------|-----------|
| Documentos OKF | `Desktop/tor-browser/Browser/procedures/` |
| Libros procesados | `.hermes/library/downloads/` |
| Metadatos | `.hermes/library/downloads/*.meta.json` |
| Skills documentadas | `~/.hermes/skills/*/SKILL.md` |
| Catálogo completo | `sharememory/hermes_memory/hermes_skills_catalog.md` |

---

## 📊 Estado Actual

- ✅ Claude Code CLI 2.1.216 operativo
- ✅ OpenRouter API autenticada
- ✅ Notex disponible para procesamiento
- ✅ Skills OKF funcionales
- ✅ Pipeline Z-Library → Notex actualizado

*Generado: 2026-07-24*