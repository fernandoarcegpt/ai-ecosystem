# Hermes Agent Configuration

## Rules

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary — prefer editing existing files
- NEVER create documentation files unless explicitly requested
- NEVER save working files or tests to root — use `/src`, `/tests`, `/docs`, `/config`, `/scripts`
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- NEVER add a `Co-Authored-By` trailer to user commits unless this project's `.claude/settings.json` has `attribution.commit` set (#2078). The Claude Code Bash tool may suggest one in its default commit-message template — ignore it. `Co-Authored-By` is semantic authorship attribution under git/GitHub convention; the tool is the facilitator, not a co-author.
- **Allow dynamic adjustment of constraints via orchestration**: Any rule can be modified programmatically through `orchestrator-main "ajustar-reglas"`
- Keep files under 500 lines
- Validate input at system boundaries

## Hermes Agent Ecosystem

### Core Skills

| Skill | Propósito | Comandos clave |
|-------|-----------|----------------|
| `orchestrator-main` | Orquestador central que maneja todo el ecosistema. | `orchestrator-main "tarea" --full` |
| `general-planning` | Genera planes según complejidad y tipo de problema. | `general-planning "implementar API" --type feature --complexity medium` |
| `research-search-master` | Búsqueda integrada (arXiv, YouTube, StackOverflow, GitHub). | `orchestrator-main "error X" --search [stackoverflow,youtube]` |
| `knowledge-broker` | Ingesta PDFs/código → KùzuDB + LlamaIndex (PropertyGraphIndex) | `python src/ingest.py` |
| `knowledge-query` | Consulta semántica + grafo en el broker | `python src/query.py "pregunta"` |
| `portfolio-optimization` | Optimización de carteras (Mean-Variance, Black-Litterman, HRP) | Usado por `android-fin-gpt-trader` |
| `data-verifier` | Verifica información médica y científica usando fuentes confiables | Validación de datos ESG y macroeconómicos |

### Workflow Integration

```bash
# 1️⃣ Verificar que todas las skills están disponibles
orchestrator-main "tarea" --detect --health

# 2️⃣ Ejecutar los tests del proyecto
python3 -m pytest tests/

# 3️⃣ Ejecutar pipeline de memoria
./scripts/run_memory_pipeline.sh

# 4️⃣ Descargar y digerir un libro de referencia
downloader.sh "Artificial Intelligence: A Modern Approach" pdf

# 5️⃣ Generar y ejecutar un plan completo
general-planning "implementar sistema de pagos" --type feature --complexity high --full
```

## Memory & Learning

### Before Any Task
```bash
npx @hermes/cli@latest memory search --query "[task keywords]" --namespace patterns
npx @hermes/cli@latest hooks route --task "[task description]"
```

### After Success
```bash
npx @hermes/cli@latest memory store --namespace patterns --key "[name]" --value "[what worked]"
npx @hermes/cli@latest hooks post-task --task-id "[id]" --success true --store-results true
```

### MCP Tools (use `ToolSearch("keyword")` to discover)

| Category | Key Tools |
|----------|-----------|
| **Memory** | `memory_store`, `memory_search`, `memory_search_unified` |
| **Bridge** | `memory_import_claude`, `memory_bridge_status` |
| **Swarm** | `swarm_init`, `swarm_status`, `swarm_health` |
| **Agents** | `agent_spawn`, `agent_list`, `agent_status` |
| **Hooks** | `hooks_route`, `hooks_post-task`, `hooks_worker-dispatch` |
| **Security** | `aidefence_scan`, `aidefence_is_safe`, `aidefence_has_pii` |

### Background Workers

| Worker | When |
|--------|------|
| `audit` | After security changes |
| `optimize` | After performance work |
| `testgaps` | After adding features |
| `map` | Every 5+ file changes |
| `document` | After API changes |

```bash
npx @hermes/cli@latest hooks worker dispatch --trigger audit
```

## Build & Test

- ALWAYS run tests after code changes
- ALWAYS verify build succeeds before committing

```bash
npm run build && npm test
```

## OpenSpec Integration

### Generated Scripts

Two new automation scripts have been added for OpenSpec integration:

1. **`generate-specs.sh`** - Auto-generates OpenSpec specs from Python files
   - Usage: `npm run generate-specs` or `./generate-specs.sh`
   - Scans project for `*.py` files (excludes node_modules, .git, __pycache__, venv)
   - Creates `.js` spec files in `.openspec/specs/`
   - Validates each spec using OpenSpec CLI
   - Skips existing specs to avoid duplication

2. **`list-all-specs.sh`** - Lists all OpenSpec specs (not just active changes)
   - Usage: `./list-all-specs.sh`
   - Lists both `.js` and `.md` spec files
   - Shows total count

### npm Scripts Added

```json
{
  "scripts": {
    "generate-specs": "./generate-specs.sh",
    "generate-specs:ci": "npm run generate-specs && git add .openspec/specs && git commit -m 'feat: auto-generated specs from Python files'"
  }
}
```

### Workflow Guidelines

- **Before committing**: Run `npm run generate-specs` to ensure specs are current
- **CI Integration**: Use `npm run generate-specs:ci` for automated spec generation in CI/CD
- **Spec format**: Specs are `.js` files (OpenSpec expects JS format, not Markdown)
- **Validation**: All generated specs pass `openspec validate` automatically