---
name: advanced-quant-analysis
description: "Advanced quantitative analysis skill that integrates Koopman/EDMD, Grassmannian tracking, TDA, and Transformer-based modeling for financial markets."
platforms: [linux, macos, windows]
tags: [finance, koopman, grassmannian, tda, transformer, analysis]
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Advanced Quantitative Analysis

## Overview
This skill combines several advanced mathematical techniques to analyze financial markets:

1. **Koopman/EDMD**: Linearizes non-linear price dynamics to extract Koopman modes and eigenvalues.
2. **Grassmannian tracking**: Monitors sub‑spaces of covariance and detects regime shifts using Grassmannian geometry.
3. **Topological Data Analysis (TDA)**: Uses persistent homology to capture multi‑scale structure and detect early warning signs before regime changes.
4. **Transformer‑based modeling**: Treats sequences and cross‑sectional data as tokens, applying self‑attention for long‑range dependencies and multi‑head specialization.

The skill provides a unified pipeline:

1. **Data ingestion** – raw price, volume, order‑book, and macro‑economic series.
2. **Pre‑processing** – cleaning, missing‑value handling, scaling.
3. **Feature extraction** – Koopman modes, Grassmannian coordinates, persistence landscapes, and Transformer embeddings.
4. **Modeling** – optional supervised learning (regression/classification) on top of extracted features.
5. **Output** – structured JSON with:
   - `modes`: list of Koopman eigenvalues and eigenvectors,
   - `grassmann_coords`: coordinates in the Grassmann manifold,
   - `persistence_diagram`: barcode representation of H1/H2,
   - `transformer_embeddings`: tokenized sequences for downstream ML,
   - `trading_signal`: derived recommendation (BUY/SELL/HOLD).

## 🛠️ Core Functions

| Function | Description |
|----------|-------------|
| `load_data(path, format)` | Load CSV, Parquet, or JSON market data. |
| `embed_state(series, lags, options)` | Build observable dictionary (price, returns, volume, delay embeddings, etc.). |
| `run_edmd(series, dictionary, **kwargs)` | Run Extended DMD, return eigenvalues, eigenvectors, and Koopman modes. |
| `track_grassmann(subspace, window)` | Track Grassmannian coordinates over a sliding window. |
| `compute_persistence(series, epsilon_range)` | Compute persistent homology (H0, H1, H2) and return landscape. |
| `transformer_encode(seq, model_name='gpt2-medium')` | Tokenize and embed sequence for Transformer inference. |
| `run_full_pipeline(data, params)` | End‑to‑end pipeline returning a dict with all features. |

## 📚 How to use

```python
from hermes_skills import advanced_quant_analysis as aq

# Load data (example CSV)
df = aq.load_data('data/SP500_daily.csv')

# Define dictionary and lags
dict_name = 'financial_esm'
lags = 5

# Run EDMD
modes = aq.run_edmd(df, dict_name, lags=lags)

# Run Grassmann tracking
coords = aq.track_grassmann(df, window=30)

# Run TDA
persistence = aq.compute_persistence(df, epsilon_range=(0.01, 0.5))

# Run Transformer (optional)
embeddings = aq.transformer_encode(df['close'].tolist(), model='gpt2-medium')

# Full pipeline
result = aq.run_full_pipeline(df, dict_name='financial_esm', lags=10, 
                              grassmann_window=30, tda_eps=0.05, transformer_model='gpt2-medium')
print(result['trading_signal'])
```

## 📈 Example usage in a workflow

```bash
# 1️⃣ Load data
hermes run python -c "import pandas as pd; df = pd.read_csv('data/SP500_daily.csv'); print(df.head())"

# 2️⃣ Run the skill (example CLI)
hermes run advanced-quant-analysis --goal 'forecast SP500 next 30 days' \
    --params '{"lags": 10, "dictionary": "financial_esm", "tda_eps": 0.02, "transformer_model": "gpt2-medium"}'
```

---

## 📌 Usage notes

- The skill expects the data to be in a CSV or Parquet file with at least columns: `timestamp`, `close`, `volume`, `open`, `high`, `low`.
- If you need to feed in external data (e.g., from a database), use the `read_file` command to load the file into the skill's working directory.
- The skill automatically saves intermediate results (Koopman modes, Grassmann coordinates, persistence diagrams) under `~/.hermes/skills/main/android-fin-gpt-trader/auxiliary/` for debugging.
- **Important:** The skill expects the underlying `koopman-edmd-dynamic-modeler` and `project-categorizer` skills to be present in the environment; otherwise it will raise a clear error.

---

## 📚 Example usage from command line

```bash
# Load data and run the full pipeline
hermes run advanced-quant-analysis \
    --goal 'forecast next 30 days for SP500' \
    --params '{"lags": 10, "dictionary": "financial_esm", "tda_eps": 0.02, "transformer_model": "gpt2-medium"}'
```

Output example:

```json
{
  "modes": [
    {"eigenvalue": 0.98, "eigenvector": [...], "type": "trend"},
    {"eigenvalue": 0.92, "eigenvector": [...], "type": "seasonal"},
    {"eigenvalue": 0.45, "eigenvector": [...], "type": "noise"}
  ],
  "grassmann_coords": [[0.12, 0.34, 0.66], [0.11, 0.33, 0.68]],
  "persistence_diagram": {
    "H0": 12,
    "H1": 27,
    "H2": 3
  },
  "transformer_embeddings": [...],
  "trading_signal": "BUY",
  "confidence": "HIGH",
  "notes": "Strong upward trend indicated by λ≈0.98 mode; ESG score high; no political risk detected."
}
```

---

### 📦 How to install the skill

```bash
hermes skills create android-fin-gpt-trader --category main --content "$(cat ~/.hermes/skills/main/android-fin-gpt-trader/SKILL.md)"  # existing skill
hermes skills create advanced-quant-analysis --category main --content "$(cat /home/fernando/.hermes/skills/main/advanced-quant-analysis/SKILL.md)"
```

(Replace the path with the actual location of the skill definition file.)

---

## 📌 Nota importante

- **Habilitar `koopman-edmd-dynamic-modeler`**: antes de usar `advanced-quant-analysis`, asegúrate de que la skill `koopman-edmd-dynamic-modeler` esté **activada** (en la lista de skills habilitadas).  
- **Dependencias**: la skill depende de `numpy`, `scipy`, `scikit-learn`, `pytorch`, y `tensorflow` (para el transformer). Instálalas con:

```bash
pip install --user numpy scipy scikit-learn joblib torch torchvision
```

---

## ✅ Verificación rápida

```bash
# Listar skills instaladas
hermes skills list | grep -E "advanced|quant|koopman|grassmann|tda|transformer"

# Verificar que la skill está disponible
hermes skill_view name:advanced-quant-analysis
```

Si todo está correcto, la skill aparecerá en la lista y podrás usarla en cualquier flujo de trabajo que requiera análisis financiero avanzado.

--- 

## 📌 Próximos pasos sugeridos

1. **Instalar dependencias** (si no lo has hecho aún):
   ```bash
   pip install --user numpy scipy scikit-learn torch torchvision
   ```
2. **Crear un proyecto de prueba** en `wiki_memoria/proyectos/finanzas/acciones/` con datos de precios de una empresa Android (ej.: `GOOGL` o `MSFT`).
3. **Ejecutar la skill** con un conjunto de parámetros:
   ```bash
   hermes run advanced-quant-analysis \
       --goal "forecast 30‑day price trajectory for GOOGL" \
       --params '{"lags": 12, "dictionary": "financial_esm", "tda_eps": 0.02, "transformer_model": "gpt2-medium"}'
   ```
4. **Validar** el resultado con `self-audit --detect` y `self-audit --audit`.

Con este conjunto de skills, tendrás una **pipeline completa** que:

- **Lineariza** la dinámica de precios (Koopman/EDMD).  
- **Rastreará** la evolución del subespacio de covarianzas (Grassmannian).  
- **Detectará** cambios estructurales mediante persistencia topológica (TDA).  
- **Transformará** todo en tokens para un Transformer que generará predicciones y señales de trading.

If you need help installing dependencies, adjusting parameters, or creating a training script, let me know.