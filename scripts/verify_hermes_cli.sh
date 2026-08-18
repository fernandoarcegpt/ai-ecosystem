#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v hermes >/dev/null 2>&1; then
  echo "ERROR: no se encontró 'hermes' en PATH" >&2
  exit 2
fi

if ! plugin_list="$(hermes plugins list --plain --no-bundled 2>&1)"; then
  echo "ERROR: no se pudo consultar la lista de plugins de Hermes" >&2
  printf '%s\n' "$plugin_list" >&2
  exit 3
fi

if [[ "$plugin_list" != *"neurosymbolic-integration"* ]]; then
  echo "ERROR: Hermes no descubre el plugin neurosymbolic-integration" >&2
  echo "Instálalo en ~/.hermes/plugins/ y habilítalo con:" >&2
  echo "  hermes plugins enable neurosymbolic-integration" >&2
  exit 3
fi

plugin_path="agents/hermes/plugins/neurosymbolic-integration"
required_plugin_files=(
  "plugin.yaml"
  "__init__.py"
  "schemas.py"
  "tools.py"
  "runtime.py"
)
for required_file in "${required_plugin_files[@]}"; do
  if [[ ! -f "$plugin_path/$required_file" ]]; then
    echo "ERROR: falta $plugin_path/$required_file" >&2
    exit 4
  fi
done

for manifest_key in name version provides_tools provides_hooks; do
  if ! grep -Eq "^${manifest_key}:" "$plugin_path/plugin.yaml"; then
    echo "ERROR: plugin.yaml no declara '$manifest_key'" >&2
    exit 4
  fi
done

if ! python3 - "$plugin_path" <<'PY'
from pathlib import Path
import sys

plugin_path = Path(sys.argv[1])
for filename in ("__init__.py", "schemas.py", "tools.py", "runtime.py"):
    path = plugin_path / filename
    compile(path.read_bytes(), str(path), "exec")
PY
then
  echo "ERROR: el código Python del plugin no compila" >&2
  exit 4
fi

# `plugins doctor` no existe en Hermes Agent v0.20.0. Algunas versiones
# posteriores pueden incorporarlo; cuando esté disponible se ejecuta como
# comprobación adicional, sin romper la compatibilidad con la CLI instalada.
plugins_help="$(hermes plugins -h 2>&1 || true)"
if grep -Eq '(^|[,{[:space:]])doctor([,}[:space:]]|$)' <<<"$plugins_help"; then
  if ! doctor_output="$(hermes plugins doctor "$plugin_path" --ci 2>&1)"; then
    echo "ERROR: Hermes Plugin Doctor rechazó el contrato del plugin" >&2
    printf '%s\n' "$doctor_output" >&2
    exit 4
  fi
  echo "PASS: contrato validado por Hermes Plugin Doctor"
else
  echo "PASS: contrato estático válido (Hermes no ofrece 'plugins doctor')"
fi

proof_log="$(mktemp "${TMPDIR:-/tmp}/hermes-neuro-proof.XXXXXX")"
output_log="$(mktemp "${TMPDIR:-/tmp}/hermes-neuro-output.XXXXXX")"
trap 'rm -f "$proof_log" "$output_log"' EXIT
export HERMES_NEUROSYMBOLIC_PROOF_LOG="$proof_log"

verify_engine() {
  local engine="$1"
  local prompt="$2"
  : >"$proof_log"
  : >"$output_log"
  if ! hermes chat -q "$prompt" >"$output_log" 2>&1; then
    echo "ERROR: hermes chat falló al verificar $engine" >&2
    sed -n '1,120p' "$output_log" >&2
    return 1
  fi
  if ! grep -q '"event": "tool_completed"' "$proof_log"; then
    echo "ERROR: Hermes no completó la herramienta oficial para $engine" >&2
    sed -n '1,120p' "$proof_log" >&2
    return 1
  fi
  if ! grep -q "\"engine\": \"$engine\"" "$proof_log"; then
    echo "ERROR: la herramienta no registró el motor $engine" >&2
    return 1
  fi
  if ! grep -Eq '[1-9][0-9]* tool calls?' "$output_log"; then
    echo "ERROR: la sesión no contabilizó una llamada de herramienta" >&2
    sed -n '1,160p' "$output_log" >&2
    return 1
  fi
  echo "PASS: $engine ejecutado mediante tool call oficial"
}

verify_engine "networkx" "Detecta el ciclo del grafo A -> B -> C -> A"
verify_engine "z3" "Resuelve las restricciones x > 10 y x < 5"
verify_engine "pydatalog" "Ana es madre de Luis y Luis es padre de Marta. ¿Es Ana ancestro de Marta?"

: >"$proof_log"
: >"$output_log"
hermes chat -q "Hola, ¿cómo estás?" >"$output_log" 2>&1
if grep -q '"event": "tool_started"' "$proof_log"; then
  echo "ERROR: un mensaje ordinario activó la herramienta neurosimbólica" >&2
  exit 1
fi
if ! grep -Eq '0 tool calls?' "$output_log"; then
  echo "ERROR: no se pudo comprobar cero tool calls para texto ordinario" >&2
  sed -n '1,160p' "$output_log" >&2
  exit 1
fi

echo "PASS: integración Hermes CLI extremo a extremo (3 motores + control negativo)"
