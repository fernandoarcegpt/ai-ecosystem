# Integración de codebase-memory-mcp

## Rol actual

`codebase-memory-mcp` funciona como memoria estructural del código. No reemplaza al núcleo neurosimbólico ni a Kùzu; lo complementa.

```text
Código del repo
  ↓
CBM index
  ↓
búsqueda / grafo estructural
  ↓
Hermes / Claude Code
  ↓
contexto para análisis, edición o razonamiento
```

## Estado

| Capacidad | Estado |
|---|---|
| Instalación vía `pnpm run cbm:install` | Configurada |
| Indexación vía `pnpm run cbm:index` | Configurada |
| Búsqueda de código | Configurada |
| Búsqueda de grafo | Configurada |
| Integración como memoria de código | Parcial/operativa según índice local |
| Sustituto de base lógica | No |

## Scripts actuales

Definidos en `package.json`:

```json
{
  "cbm:install": "npm install -g codebase-memory-mcp@0.8.1",
  "cbm:index": "codebase-memory-mcp cli index_repository '{\"repo_path\": \".\"}' --progress",
  "cbm:search": "codebase-memory-mcp cli search_code '{\"pattern\": \"$QUERY\", \"limit\": 5}'",
  "cbm:graph": "codebase-memory-mcp cli search_graph '{\"name_pattern\": \"$QUERY\", \"limit\": 5}'"
}
```

## Uso básico

```bash
# Instalar una vez
pnpm run cbm:install

# Indexar repo actual
pnpm run cbm:index

# Buscar código
QUERY="ProblemExtractor" pnpm run cbm:search

# Buscar grafo relacionado
QUERY="reasoning" pnpm run cbm:graph
```

## Buen uso dentro del proyecto

CBM debe usarse para:

- localizar funciones, clases y archivos;
- entender dependencias de código;
- responder preguntas estructurales sobre el repo;
- dar contexto a Claude Code antes de editar;
- evitar duplicar componentes existentes.

No debe confundirse con:

- memoria lógica persistente;
- motor de inferencia;
- base de hechos y reglas;
- truth maintenance;
- razonamiento simbólico determinista.

## Relación con el núcleo neurosimbólico

| Capa | Función |
|---|---|
| CBM | memoria estructural del código |
| ProblemExtractor | formalización de problemas simbólicos |
| NetworkX | grafos/dependencias |
| Z3 | restricciones |
| PyDatalog | reglas/hechos |
| Hermes hook | inyección de evidencia antes del LLM |

## Flujo recomendado antes de modificar código

```bash
QUERY="nombre_del_componente" pnpm run cbm:search
QUERY="nombre_del_componente" pnpm run cbm:graph
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
```

## Limitaciones actuales

- El índice depende del estado local/cache.
- Si no se reindexa, puede estar desactualizado.
- No reemplaza pruebas.
- No garantiza consistencia lógica.
- No resuelve identidad de entidades.
- No detecta contradicciones entre hechos documentales.

## Próximo paso recomendado

Conectar CBM a una futura base lógica canónica:

```text
CBM result
→ entidad/código detectado
→ FactStore
→ relación con fuente/archivo
→ ReasoningTraceStore
```

Así CBM dejaría de ser solo memoria de código y pasaría a alimentar una memoria lógica verificable.
