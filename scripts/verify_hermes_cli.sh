#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! hermes_bin="$(command -v hermes)"; then
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
  "detection.py"
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
for filename in ("__init__.py", "detection.py", "schemas.py", "tools.py", "runtime.py"):
    path = plugin_path / filename
    compile(path.read_bytes(), str(path), "exec")
PY
then
  echo "ERROR: el código Python del plugin no compila" >&2
  exit 4
fi

# Resolver el Python que usa Hermes. Un override explícito gana; después se
# intenta el shebang real del ejecutable y finalmente el venv estándar.
hermes_python="${HERMES_PYTHON:-}"
if [[ -z "$hermes_python" ]]; then
  first_line="$(head -n 1 "$hermes_bin" 2>/dev/null || true)"
  if [[ "$first_line" =~ ^#!(/[^[:space:]]*/python[0-9.]*)$ ]]; then
    hermes_python="${BASH_REMATCH[1]}"
  fi
fi
if [[ -z "$hermes_python" && -x "$HOME/.hermes/hermes-agent/venv/bin/python" ]]; then
  hermes_python="$HOME/.hermes/hermes-agent/venv/bin/python"
fi
if [[ -z "$hermes_python" ]]; then
  hermes_python="$(command -v python3)"
  echo "WARN: no se pudo resolver el venv de Hermes; se usará $hermes_python" >&2
fi
if [[ ! -x "$hermes_python" ]]; then
  echo "ERROR: Python de Hermes no ejecutable: $hermes_python" >&2
  exit 4
fi

echo "INFO: Hermes=$hermes_bin"
echo "INFO: Python runtime=$hermes_python"

# Esta prueba ejecuta operaciones mínimas REALES en todos los motores desde el
# mismo intérprete que se espera que use Hermes. Detecta el clásico mismatch de
# dependencias instaladas en otro venv.
if ! runtime_report="$(PYTHONPATH=.:./skilled "$hermes_python" scripts/verify_neurosymbolic_runtime.py 2>&1)"; then
  echo "ERROR: uno o más motores no levantan en el runtime de Hermes" >&2
  printf '%s\n' "$runtime_report" >&2
  exit 4
fi
if ! grep -q '"overall": "pass"' <<<"$runtime_report"; then
  echo "ERROR: el smoke test no confirmó todos los motores" >&2
  printf '%s\n' "$runtime_report" >&2
  exit 4
fi
echo "PASS: todos los motores extendidos ejecutan en el Python de Hermes"

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
    sed -n '1,160p' "$output_log" >&2
    return 1
  fi

  for required_event in detector_decision tool_required tool_started runtime_engine_inventory engine_result_observed tool_completed output_replaced; do
    if ! grep -q "\"event\": \"$required_event\"" "$proof_log"; then
      echo "ERROR: falta evento $required_event al verificar $engine" >&2
      sed -n '1,200p' "$proof_log" >&2
      return 1
    fi
  done

  if ! grep -q "\"engine\": \"$engine\"" "$proof_log"; then
    echo "ERROR: la herramienta no registró el motor $engine" >&2
    sed -n '1,200p' "$proof_log" >&2
    return 1
  fi
  if ! grep -q "\"status\": \"success\"" "$proof_log"; then
    echo "ERROR: no se registró éxito del motor $engine" >&2
    sed -n '1,200p' "$proof_log" >&2
    return 1
  fi
  if ! grep -Eq '[1-9][0-9]* tool calls?' "$output_log"; then
    echo "ERROR: la sesión no contabilizó una llamada de herramienta" >&2
    sed -n '1,200p' "$output_log" >&2
    return 1
  fi
  echo "PASS: $engine detectado y ejecutado mediante tool call oficial"
}

verify_engine "networkx" "Detecta el ciclo del grafo A -> B -> C -> A"
verify_engine "z3" "Resuelve las restricciones x > 10 y x < 5"
verify_engine "pydatalog" "Ana es madre de Luis y Luis es padre de Marta. ¿Es Ana ancestro de Marta?"
verify_engine "z3_temporal" "Resuelve estas restricciones temporales: la tarea A dura 2 horas y la tarea B dura 3 horas; A debe terminar antes de B."

: >"$proof_log"
: >"$output_log"
hermes chat -q "Hola, ¿cómo estás?" >"$output_log" 2>&1
if grep -q '"event": "tool_started"' "$proof_log"; then
  echo "ERROR: un mensaje ordinario activó la herramienta neurosimbólica" >&2
  exit 1
fi
if ! grep -Eq '0 tool calls?' "$output_log"; then
  echo "ERROR: no se pudo comprobar cero tool calls para texto ordinario" >&2
  sed -n '1,200p' "$output_log" >&2
  exit 1
fi

echo "PASS: integración Hermes CLI extremo a extremo (runtime completo + 4 motores E2E + control negativo)"
