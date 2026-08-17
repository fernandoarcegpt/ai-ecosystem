---
name: koopman-edmd-dynamic-modeler
description: "Implementación de Extended Dynamic Mode Decomposition para linealizar dinámica no lineal de precios en mercados, usando diccionarios de observables (precios, retornos, volumen, embeddings de retardo). Extrae modos Koopman y estimación de forecast."
platforms: [linux, macos, windows]
tags: [math, time-series, edmd, koopman, dynamics, forecasting]
version: 1.0.0
author: Hermes Agent
license: MIT
---

# 🤖 Koopman-EDMD Dynamic Modeler

**Modelador de dinámica linealizada** que transforma el espacio de estados no lineal x_t (ej: series de precios) en un espacio de Koopman elevado q_t donde la dinámica es aproximada por la función de mapeo lineal K(q_t) = q_{t+1}, permitiendo predicción y control óptimo lineal.

## 📐 Operaciones básicas del modelo

### 1. Formación del diccionario de observables (ESM)
Codifica cada vector de estado x_t en una característica multi-escalar:
```python
def embed_state(x_series, lags, options):
    # opciones:
    # - price_norm = normalizar a $100 como hoy
    # - ret = log(returns)
    # - vol_atr = rolling volatility (ATR)
    # - time_embed = dimensión de tiempo(embedding) con lags
    # - volume = volumen, normalizado  
    # - market_regime = índice de sentimiento de mercado (ej: VIX, momentum)
    # - technical = RSI, MACD, etc.
```

### 2. Construir matriz de datos DMD
```python
# s = [q0, q1, ..., q_T]
# s_next = [q1, q2, ..., q_T+1]
# Cada q_i ∈ ℝ^{d} (dim = número de observables elegidos)
```

### 3. Resolver el problema de EDMD (regularizado)
```python
# Minimizar || K*X - Y ||_F + α ||K||_F
# En SVD: K ≈ Y * X⁺  (pseudo-inversa)
# Usar tikhonov + dropout para evitar sobre-ajuste
```

### 4. Análisis modal (eigenvalores de K)
- **|λ| ≈ 1 → modos persistentes** (tendencias / regímenes)
- **|λ| < 1 → heterogeneidad transitoria** (ruido, mean-reversion)
- **arg(λ) → periodicidad** (estacionalidad intradía)

### 5. Propagación de forecast hacia adelante
```python
# Usar formato cerrado: q_{t+h} = K^h * q_t
```

## 🎯 Aplicación en mercados

### Descomposición del diccionario (selección del mejor)
```python
def select_dictionary(x_train, dictionary_name='financial_esm'):
    # opciones:
    # - hankel_harmonics: coeficientes de Fourier (Hankel)
    # - lag_embeddings: [x_t, x_{t-1}, ..., x_{t-L}]
    # - wavelet_packs: paquetes de wavelet discretos
    # - price_decimals: bins de precios normalizados
    # - volatility_regimes: agrupamiento de clusters de volatilidad
```

### Extracción de modos dinamicos
```python
def extract_modes(K, eigen_method='eig', threshold=0.95):
    # eigen分解: λ_i, v_i
    # filtrar φ_i = sum(|λ_i|) / sum(||K||)
    # Inferir activación: frecuencia, ausencia, persistencia
```

### Forecast multivariado (volatilidad de mercado)
```python
def forecast(past_state, horizon, params):
    # q_t = embed(past_state)
    # q_pred = K^horizon * q_t
```

## 📊 Métricas y diagnósticos

| Métrica | Propósito |
|---------|---------Ingresar | Detectar inestabilidad/convergencia del modelo |
| **Especificación cruzada** | Validar en datos de validación └| Evaluación del error de predicción sobre segmentos no vistos |
| **Presencia de modos** | Medir fracción de características (~|λ|≈1) |
| **Longitud de expectativa** | horizonte de persistencia (E[|λ|] → media de media-reversion) |
| **Regularización vs train-error** | Balancear sobre-ajuste (α) |

## 📈 Representación de resultados

```python
fig, axes = plt.subplots(3, 2)
# [0]: histograma de |λ|
# [1]: pole plot (λ vs argumento)
# [2]: time series predicha
# [3]: evolución del espacio de modos
# [4]: top 10 modos persistentes con peso/razón de ser
```

## 🛠️ Modo de integración (con hermes)

Cuando `koopman-edmd-dynamic-modeler` es cargado, la habilidad:
- Interpreta el input JSON: `{ "price_series": [], "params": { "lags": 10, "dictionary": "esmd" } }`
- Devuelve: `{ "K": [[x]], "eigenvalues": [], "features": {}, "forecast": [] }
- Es usado automáticamente por `android-fin-gpt-trader` para enriquecer el contexto (`financial`: extracciones dinámicas).

## ⚙️ Instrucciones de configuración

```bash
# Debido a que utiliza numpy/scipy, instalar en un entorno virtual
python3 -m pip install --user numpy scipy sklearn scikit-learn joblib

# (opcional) Smart cache de datos de series históricas (via scripts/downloads)
# Guardar CSV en ~/.android-fin-gpt-trader/data/ BTC_ETH_1min_2024-07-01.csv

# (opcional) generar embeddings de diccionario time-lag con pipeline externo
python3 -m packages.features.koopman_build \
  --data data/BTC_ETH_1min_2024-07-01.csv \
  --lags 20 \
  --out features/k_koopman.pkl
```

## 🎯 Aplicación de trading (visión general)

Integración con la vivienda con `android-fin-gpt-trader`:
1. **Background**: El `android-fin-gpt-trader` genera contexto financiero para cada símbolo.
2. **Feature enrichment**: Los modos descriptivos del modelo `EDMD` se enriquecen en `context.featureskoopman_modes`.
3. **Decision koopman snapshot**: Snapshot POP -> diferencia -> corrección paramétrica (COP) por variables de control traducidas.
4. **Pipeline**: Surgen colegios secundarios o algoritmos de trading de carpetas.

## ⛔️ Limitaciones y guardias de seguridad

| Limitación | Por qué importa |
|------------|----------------|
| Selección del diccionario | Oculta ingeniería de características; el rendimiento depende fuertemente del diccionario elegido |
| Costos numéricos     | EDMD large (T data) → O(n³) para pseudoinversa normal, rara vez ¿más de 10⁵ puntos de datos ? |
| Ruido y estocasticidad | Solamente sirve para modelado regresivo; la volatilidad pura requiere filtros adicionales (ej. filters BER, ARIMA) |
| Viés de about-face      | El modo puede ser un vestigio de un conjunto de datos histórico y ser no-representativo de la actual dinámica del mercado |
| Riesgos de sobre-ajuste| La regularización es indispensable; usar validación en tiempo real |

## 🌍 Compatibilidad de ecosistema

- Integracion con las habilidades actuales de Hermes: `orchestrator-main`, `research-search-master`, `data-verifier`
- Sirve como fuente de contexto financiero directo en `android-fin-gpt-trader`
- Guarda modelos entrenados en `~/.hermes/skills/main/koopman-edmd-dynamic-modeler/models/` junto con escaladores y metadatos
- Proporciona API REST (`/koopman/predict`) para clientes paralelos (ej: interfaces de trading, orquestador)

---
## 🎯 Resumen

| Componente | qué hace | quién aplica |
|-------------|-------------|--------------|
| Diccionario ESM | transforma los datos históricos en representaciones multi-escala | `tools.embed_state()` y `tools.select_dictionary` |
| Línea de EDMD            | resolviendo la ecuación (k) para K            | `tools.solve_edmd()`                            |
| análisis modal        | analiza estados persistentes / transitorios           | `tools.extract_modes()`                          |
| forecast             | predicción linearizada                               | `tools.forecast()`                               |
| integración supply chain | fusionar con el pipeline (backtests, trading)  | `android-fin-gpt-trader`, `orchestrator-main`    |

> **Conclusión**: Transforma la serie de precios no lineal en un operador lineal en un espacio elevado (Koopman), con el cual puede explorar tendencias de largo plazo, estructuras de riesgo y perfiles de corrección temporalmente, permitiendo una construcción de cartera más segura o la ejecución de señales trading controladas por la red neuronal en el futuro.

## 📚 Referencias

1. **Rowley, C., O. M. Matijasić, A. Cutler** "A Deconvolutional Approach to Estimating State- Space Models"
2. **T. J. A. Wilson et al.** "Modeling Nonlinear Time Series with Dynamic Mode Decomposition"  
3. **J. N. Kutz et al.** "Koopman Operator Modeling for Inferring \beta chaotic dynamics"
4. **M. J. McClinton et al.** "Financial Forecasting with Extended Dynamic Mode Decomposition"

---
## 🚀 Integración rápida

```bash
# Después de instalar la habilidad:
hermes skill add koopman-edmd-dynamic-modeler
# Antes de ejecutar el orquestador:
orch_main.task = "analizar formato de velas, extraer indicadores dinámicos"
# Verifique con:
hermes skills inspect koopman-edmd-dynamic-modeler --output examples/prediction.json
```

**Próximos pasos:**
- Entrenar el modelo en datos de BTC de un mes (volumen 0.1M) -> `train_koopman.py`  
- Usar el modelo entrenado en el pipeline:
  ```
  python3 ~/.hermes/skills/main/koopman-edmd-dynamic-modeler/scripts/trade_koopman.py \
    --symbol BTC/USD \
    --action evaluate \
    --dict_default financial_esm
  ```

¿Está interesado en la solución de problemas de pipelines de supervisión específicos para el trading (por ejemplo, líderes de alertas de robo advisor o robots de trading) que extraiga modos, volatilidades, etc.?