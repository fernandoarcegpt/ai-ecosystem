# Architecture Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Core Components](#core-components)
4. [Skill Ecosystem](#skill-ecosystem)
5. [Configuration & Environment](#configuration--environment)
6. [Dependency Management](#dependency-management)
7. [Build, Test & Deployment](#build-test--deployment)
8. [Orchestration & Workflow](#orchestration--workflow)
9. [Memory & Learning System](#memory--learning-system)
10. [OpenSpec Integration](#openspec-integration)
11. [Maintenance & Extensibility](#maintenance--extensibility)
12. [Troubleshooting](#troubleshooting)
13. [Glossary & References](#glossary--references)

---

### Project Overview
The repository `ai-ecosystem` is a **Hermes Agent** workspace that combines:
- **Automation** of AI skill execution (trading, quant analysis, data verification)
- **Memory & learning** mechanisms for persistent knowledge
- **Orchestration** via `orchestrator-main` to coordinate multi‑step tasks
- **OpenSpec** spec generation for automated API contract validation
- **CLI tooling** (Claude Code, npm scripts) for developer interaction

The system is written primarily in Python and JavaScript/TypeScript, managed with `pnpm`, and configured through a collection of YAML/JSON files, CLI flags, and persistent memory stores.

### Directory Structure
```
.
├── .hermes/                     # Hermes runtime data
│   ├── profiles/
│   │   └── default/             # Current profile
│   │       ├── skills/          # Installed skills (e.g., android-fin-gpt-trader)
│   │       ├── plugins/
│   │       ├── memories/
│   │       └── cron/
├── src/                         # Application source code
│   ├── ingest.py                # PDF/Document ingestion to KùzuDB
│   ├── query.py                 # Semantic query against the knowledge graph
│   ├── orchestrator_main.py     # Entry point for orchestrator tasks
│   ├── generate_specs.py        # OpenSpec spec generator
│   └── ...                      # Additional modules
├── scripts/
│   ├── run_memory_pipeline.sh   # Executes memory pipeline
│   └── downloader.sh            # Downloads reference documents
├── tests/                       # Unit / integration tests
├── .openspec/
│   └── specs/                   # Auto‑generated spec files (JavaScript)
├── .github/                     # GitHub workflow definitions (if any)
├── .gitignore
├── CLAUDE.md                    # Hermes Agent configuration guide
├── package.json                 # pnpm package definition
├── pnpm-lock.yaml
├── requirements.txt             # Python dependencies
├── README.md                    # Basic project README
└── ARCHITECTURE.md              # This documentation
```

### Core Components
| Component | Purpose | Entry Point / API |
|-----------|---------|-------------------|
| **Hermes Agent** | Runtime that loads skills, manages memories, schedules cron jobs | `~/.hermes/profiles/default` |
| **Orchestrator (`orchestrator-main`)** | Central planner & executor for multi‑step tasks | `orchestrator-main "task-name" --full` |
| **General Planner (`general-planning`)** | Generates structured plans for features / bugs | `general-planning "implement API" --type feature --complexity medium` |
| **Research Engine (`research-search-master`)** | Cross‑source search (arXiv, YouTube, StackOverflow) | `orchestrator-main "error X" --search [stackoverflow,youtube]` |
| **Memory Broker** | Ingests documents → KùzuDB graph; provides semantic queries | `python src/ingest.py` ; `python src/query.py "question"` |
| **OpenSpec Generator** | Scans Python files, emits `.js` spec files, validates them | `npm run generate-specs` |
| **CLI Integration** | Wrapper around Claude Code for interactive coding | `claude-code ...` |

### Skill Ecosystem
- **Installed Skills:**  
  - `android-fin-gpt-trader` – Android‑oriented automated trading.  
  - `portfolio-optimization` – Mean‑Variance, Black‑Litterman, HRP algorithms.  
  - `ah-quant-analyst` – Quantitative analysis utilities.  
  - `data-verifier` – Validates scientific/medical data against trusted sources.  
  - `hermes-agent` – Low‑level agent configuration & management.  
- **Skill Management Commands:**  
  ```bash
  # List skills
  skill_view
  # Load a skill for use
  skill_view(name='android-fin-gpt-trader')
  # Edit / patch a skill
  skill_manage(action='patch', name='android-fin-gpt-trader', old_string='...', new_string='...')
  ```

All skills live under `~/.hermes/skills/` (or profile‑specific subfolders) and follow a **SKILL.md** convention (YAML front‑matter + usage guide). Skills can be created, updated, or deleted via `skill_manage`.

### Configuration & Environment
| Variable | Description |
|----------|-------------|
| `ANTHROPIC_BASE_URL` | `https://openrouter.ai/api` – Base endpoint for OpenRouter API. |
| `ANTHROPIC_AUTH_TOKEN` | API token for authentication. |
| `ANTHROPIC_MODEL` | Default model (`openrouter/free`). |
| `HERMES_PROFILE` | Name of the active Hermes profile (`default`). |
| `HERMES_MEMORIES_DIR` | Directory where persistent memories are stored (`~/.hermes/memories`). |

Configuration files:
- **`.env`** (not version‑controlled) holds secrets.  
- **`CLI` options** override environment defaults.  
- **`package.json`** scripts define frequently used commands (`npm run test`, `npm run build`).  

### Dependency Management
- **Python:** `requirements.txt` (pinned versions). Installed via `pnpm install` or `python -m pip install -r requirements.txt`.  
- **Node.js:** `package.json` + `pnpm-lock.yaml`. Scripts:  
  ```json
  {
    "scripts": {
      "test": "python3 -m pytest tests/",
      "build": "echo \"No build step required\"",
      "generate-specs": "./generate-specs.sh",
      "generate-specs:ci": "npm run generate-specs && git add .openspec/specs && git commit -m \"feat: auto-generated specs from Python files\""
    }
  }
  ```
- **System Packages:** Occasionally required tools (`curl`, `jq`, `git`) are installed via `apt-get` or `pnpm add -g` as needed.

### Build, Test & Deployment
```bash
# Activate virtualenv (if any) and install deps
pnpm install

# Run tests
pnpm run test

# Execute the memory pipeline
./scripts/run_memory_pipeline.sh

# Regenerate OpenSpec specs
npm run generate-specs:ci
```

All commands are **self‑contained**; they respect the current working directory (`/home/fernando/ai-ecosystem`). The CI pipeline can be hooked to GitHub Actions via the `generate-specs:ci` script.

### Orchestration & Workflow
A typical end‑to‑end workflow might look like:

1. **Health Check**
   ```bash
   orchestrator-main "tarea" --detect --health
   ```
2. **Plan Generation** (example)
   ```bash
   general-planning "implement payment system" --type feature --complexity high --full
   ```
3. **Skill Execution** (example using trading skill)
   ```bash
   orchestrator-main "run-trade" --skill android-fin-gpt-trader --mode live
   ```
4. **Memory Update**
   ```bash
   ./scripts/run_memory_pipeline.sh
   ```
5. **OpenSpec Validation**
   ```bash
   npm run generate-specs:ci
   ```

The orchestrator can chain these steps automatically, using `context_from` to inject outputs of previous jobs into the next prompt.

### Memory & Learning System
- **Storing a Fact**
  ```bash
  memory add --target=user --content "User prefers concise responses in Spanish"
  ```
- **Searching Memories**
  ```bash
  memory search --query "android-fin-gpt-trader" --namespace patterns
  ```
- **hooks** can be scheduled (cron) to run post‑task evaluations and store results.

Memory entries are **additive**; stale entries can be removed or replaced in batches to stay within the char limit.

### OpenSpec Integration
- **Spec Generation Script** (`generate-specs.sh`)  
  - Scans `src/**/*.py` (excluding `node_modules`, `venv`, `__pycache__`).  
  - Emits JavaScript spec files into `.openspec/specs/`.  
  - Runs `openspec validate` automatically.  
- **CI Script** (`generate-specs:ci`) adds and commits generated specs.  

Usage:
```bash
npm run generate-specs          # Local development
npm run generate-specs:ci       # CI – stages & commits automatically
```

### Maintenance & Extensibility
| Action | Command | Notes |
|--------|---------|-------|
| **Add a new skill** | `skill_manage(action='create', name='new-skill', category='mlops', content='...')` | Must include YAML front‑matter and usage guide. |
| **Patch an existing skill** | `skill_manage(action='patch', name='android-fin-gpt-trader', old_string='...', new_string='...')` | Update after discovering missing steps or OS‑specific issues. |
| **Schedule a cron job** | `cronjob action='create' schedule='0 2 * * *' prompt='Run memory pipeline nightly' skills=[]` | Use `cronjob action='list'` to review existing jobs. |
| **Run a background watchdog** | `terminal background=true notify_on_complete=true command='python watchdog.py'` | Ensure script emits output on success/failure. |
| **Update documentation** | `write_file path='ARCHITECTURE.md' content='...'` | Keep this file synchronized with structural changes. |

### Troubleshooting
- **Missing dependencies:** Run `pnpm install` again; check `requirements.txt` for Python packages.  
- **Skill fails to load:** `skill_view(name='<skill>')` to inspect its `SKILL.md`; verify front‑matter is valid YAML.  
- **Orchestrator cannot find a skill:** Ensure the skill directory resides under the active profile’s `skills/` folder; run `orchestrator-main "tarea" --detect --health`.  
- **Cron job does not fire:** `cronjob action='list'` → verify `schedule` field; use `cronjob action='run' job_id=XYZ` to force execution.  

### Glossary & References
- **Hermes Agent:** Open‑source orchestration framework (https://hermes-agent.nousresearch.com).  
- **OpenSpec:** Contract‑first API validation tool (https://openspec.org).  
- **KùzuDB:** Property graph database used for semantic memory (https://kuzudb.org).  
- **Claude Code:** Anthropic CLI for interactive coding (https://claude.ai/code).  
- **pnpm:** Fast, space‑efficient package manager (https://pnpm.io).  

--- End of Document ---