#!/usr/bin/env bash
set -euo pipefail

if ! command -v hermes >/dev/null 2>&1; then
  echo "ERROR: no se encontró 'hermes' en PATH" >&2
  exit 2
fi
if ! command -v claude >/dev/null 2>&1; then
  echo "ERROR: no se encontró 'claude' en PATH" >&2
  exit 2
fi

probe_dir="$(mktemp -d "${TMPDIR:-/tmp}/hermes-autonomy.XXXXXX")"
proof_log="${probe_dir}/proof.log"
output_log="${probe_dir}/hermes-output.log"
state_dir="${probe_dir}/state"
trap 'rm -rf -- "$probe_dir"' EXIT

git -C "$probe_dir" init -q
printf '# Repositorio temporal de autonomía Hermes\n' >"${probe_dir}/README.md"

export HERMES_AUTONOMY_ENABLED=1
export HERMES_AUTONOMY_REPOSITORY="$probe_dir"
export HERMES_AUTONOMY_STATE_DIR="$state_dir"
export HERMES_NEUROSYMBOLIC_PROOF_LOG="$proof_log"
export HERMES_AUTONOMY_VERIFY_FILE="hermes_autonomy_probe.txt"
export HERMES_AUTONOMY_VERIFY_CONTENT=$'HERMES_AUTONOMY_OK\n'

passed=0
for attempt in 1 2; do
  : >"$proof_log"
  : >"$output_log"
  prompt="/orchestrate Verificar el flujo real en el directorio absoluto ${probe_dir}: crea realmente hermes_autonomy_probe.txt con los bytes exactos HERMES_AUTONOMY_OK seguidos de un único salto de línea. Léelo después. No basta con describirlo ni declarar éxito. Intento ${attempt}."
  if hermes chat -q "$prompt" >"$output_log" 2>&1 \
    && grep -q 'AUTONOMY_COMPLETED=1 BLOCKED=0 FAILED=0' "$proof_log" \
    && python3 - "${probe_dir}/hermes_autonomy_probe.txt" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
raise SystemExit(0 if path.is_file() and path.read_bytes() == b"HERMES_AUTONOMY_OK\n" else 1)
PY
  then
    passed=1
    break
  fi
  echo "WARN: intento autónomo ${attempt} no produjo el archivo verificado" >&2
done

if [[ "$passed" -ne 1 ]]; then
  echo "ERROR: Hermes no completó la solicitud autónoma verificable" >&2
  sed -n '1,120p' "$proof_log" >&2
  sed -n '1,120p' "$output_log" >&2
  exit 1
fi

echo "PASS: Hermes originó y supervisó una tarea real ejecutada por Claude Code"
