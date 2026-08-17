# Federated Vault Architecture Plan

## 1. Vision
Transform the current monolithic OKF Wiki Memory vault into a **federated ecosystem of agent-specific domains** with a shared cross-reference layer. This enables:

- **Sovereign operation** of each agent's knowledge domain  
- **Controlled sharing** via a `Sinapsis` bridge layer  
- **Isolation** to prevent accidental contamination of domain-specific data  
- **Clear attribution** of decisions to specific domains  

The new layout mirrors the described “Vault Federado” structure:

```
/Mi_Vault_Obsidian/
│
├── /00_Orquestador_Humano/           <-- Human orchestration, prompts, decisions
│
├── /10_Cerebro_Claude/               <-- Claude’s independent reasoning, code generation
│
├── /20_Cerebro_Hermes/               <-- Hermes’ independent investigation, research, browsing
│
├── /30_Sinapsis/                     <-- Cross‑domain “sinapsis” for linking and conflict resolution
│
└── /99_Sistema/                      <-- Templates, configs, CI/CD, documentation
```

## 2. Current State Review
| Component | Location | Role | Constraints |
|-----------|----------|------|-------------|
| `wiki_memoria/` (vault root) | `/home/fernando/ai-ecosystem/wiki_memoria` | Flat storage of `.md` notes | All agents read/write to same namespace |
| `process_wiki.py` | – | Simple flat‑file pipeline (list/write/validate) | No isolation logic |
| `knowledge_broker.py` | – | Writes to Obsidian vault via REST API | No read‑only enforcement |
| `staging/` | `/home/fernando/ai-ecosystem/staging` | Temporary notes before validation | One global queue |
| `.index.json` / `.changelog.log` | vault root | Global metadata tracking | No domain granularity |

## 3. Target Architecture

### 3.1 Directory Structure
```
wiki_memoria/
├── 00_Orquestador_Humano/
│   └── prompts/          # Human‑written prompts, decision logs
│
├── 10_Cerebro_Claude/
│   ├── reasoning/        # Step‑by‑step reasoning traces
│   ├── code/             # Generated source files (read‑only for Hermes)
│   └── metadata/         # Index & changelog specific to Claude
│
├── 20_Cerebro_Hermes/
│   ├── investigation/    # Research notes, web scrape results
│   ├── citations/        # Source URLs & references
│   └── metadata/         # Index & changelog specific to Hermes
│
├── 30_Sinapsis/
│   ├── mapas_cruzados/   # Index files that explicitly link [[Cerebro_Claude]] ↔ [[Cerebro_Hermes]]
│   └── conflictos/       # Issue trackers for contested cross‑domain decisions
│
└── 99_Sistema/
    ├── configs/          # YAML/JSON config files (permissions, env vars)
    └── scripts/          # Migration and validation utilities
```

### 3.2 Per‑Domain Access Controls
| Domain | Permission Model |
|--------|------------------|
| **Cerebro_Claude** | Writes only to its own sub‑tree; **read‑only** access to `20_Cerebro_Hermes` (via Knowledge Broker). |
| **Cerebro_Hermes** | Writes only to its own sub‑tree; **read‑only** access to `10_Cerebro_Claude` (via Knowledge Broker). |
| **Sinapsis** | Shared read/write namespace; but writes are **annotated** with a `source_domain` tag and must reference a *link* in `30_Sinapsis/mapas_cruzados`. |

### 3.3 Metadata Changes
- Split `.index.json` into per‑domain variants (`index_claude.json`, `index_hermes.json`, `index_sinapsis.json`).  
- Introduce `domain` field for each entry to enable targeted searches.  
- Changelog entries must include `domain` prefix (`CLAUDE_WRITE`, `HERMES_INVESTIGATE`, `SINAPSIS_LINK`).  

### 3.4 Script Adjustments
1. **`process_wiki.py` → `domain_writer.py`**  
   - Add CLI flag `--domain` (values: `claude`, `hermes`).  
   - Enforce that file paths stay within the caller’s domain root.  
   - Auto‑populate domain‑specific `update_index` calls.  

2. **`knowledge_broker.py` → `domain_broker.py`**  
   - Add `DOMAIN_ROOT` constant per domain.  
   - Validate that incoming `filename` starts with the caller’s root path.  
   - Return **403** if a domain tries to write outside its root.  

3. **Cross‑link Enforcement (`30_Sinapsis`)**  
   - Create helper `link_sinapse(source_path, target_path, target_domain)`.  
   - The helper writes a markdown note to `30_Sinapsis/mapas_cruzados/` that contains a standard header with:  
     ```markdown
     ## Sinapsis: [[{source_domain}]] ↔ [[{target_domain}]]
     **Source Note:** `[[{source_path}]]({source_path})`
     **Target Note:** `[[{target_path}]]({target_path})`
     **Status:** pending / resolved / conflict
     ```  
   - The note is automatically appended to both domain changelogs (`append_changelog` with `SINAPSIS_LINK`).  

## 4. Migration Procedure
1. **Backup**: `tar -czf backup_$(date +%F).tar.gz /home/fernando/ai-ecosystem/wiki_memoria`.  
2. **Create new directory tree** as in Section 3.1.  
3. **Copy existing notes** into appropriate sub‑folders based on historical domain tags (use comments in note front‑matter or heuristics).  
4. **Run `scripts/migrate_index.py`** – generates per‑domain `index_*.json` and rewrites `.changelog.log` entries with domain prefixes.  
5. **Update `.env`** for `OBSIDIAN_URL` and `OBSIDIAN_API_KEY` (unchanged) but add `CLAUDE_ROOT` / `HERMES_ROOT` env vars used by scripts.  
6. **Execute smoke test**: run `process_wiki.py --dry-run` for each domain to verify permission enforcement.  

## 5. Verification & Testing
- **Unit tests**: add `tests/test_domain_isolation.py` to assert that an attempt by `Cerebro_Claude` to write in `20_Cerebro_Hermes/` raises `PermissionError`.  
- **Integration test**: simulate a full pipeline run for each domain, confirming that:  
  - Valid notes are written to the correct domain folder.  
  - Invalid notes are rejected and logged.  
  - A link note appears in `30_Sinapsis/mapas_cruzados/` when a cross‑domain reference is added.  
- **Security scan**: ensure `write_to_vault` can’t be abused via directory traversal.  

## 6. Roll‑back Strategy
- Keep the original flat `wiki_memoria` directory as `backup_flat/`.  
- Re‑activate the flat pipeline by setting an env var `FLAT_MODE=true` in `.env` (currently default false).  
- All new migrations are reversible via the backup archive.  

## 7. Documentation & On‑boarding
- Update `README.md` with a **“Vault Architecture”** section summarizing the new layout.  
- Provide a **“Domain Quick‑Start”** guide showing how to spawn a new agent folder and how to create a sinapsis link.  
- Add a **FAQ** covering:  
  - “Why are some notes read‑only?”  
  - “How do I resolve a conflict in `30_Sinapsis/conflictos/`?”  
  - “Can I see a visual graph of the cross‑links?”  

## 8. Timeline Estimate
| Phase | Effort | Duration |
|-------|--------|----------|
| Backup & Baseline | 1 h | Immediate |
| New Directory Setup | 2 h | ~30 min |
| Script Refactor | 4 h | 1 day |
| Migration Scripts | 3 h | 1 day |
| Testing & Verification | 5 h | 1–2 days |
| Documentation | 2 h | ½ day |
| **Total** | **≈17 h** | **~1 week** (including buffer) |

---  

*Prepared by the planning loop. Ready for review and approval to proceed with implementation.*