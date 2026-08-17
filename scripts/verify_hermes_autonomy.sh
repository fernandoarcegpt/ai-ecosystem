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

prompt='/orchestrate Verificar el flujo real: crea hermes_autonomy_probe.txt con el contenido exacto HERMES_AUTONOMY_OK seguido de un salto de línea, léelo y no modifiques ningún otro archivo.'
if ! hermes chat -q "$prompt" >"$output_log" 2>&1; then
  echo "ERROR: Hermes no completó la solicitud autónoma" >&2
  sed -n '1,120p' "$output_log" >&2
  exit 1
fi

if ! grep -q 'AUTONOMY_COMPLETED=1 BLOCKED=0 FAILED=0' "$proof_log"; then
  echo "ERROR: el hook Hermes no registró una tarea autónoma completada" >&2
  sed -n '1,120p' "$proof_log" >&2
  exit 1
fi
if [[ ! -f "${probe_dir}/hermes_autonomy_probe.txt" ]]; then
  echo "ERROR: el agente no creó el archivo de prueba" >&2
  exit 1
fi
if [[ "$(<"${probe_dir}/hermes_autonomy_probe.txt")" != 'HERMES_AUTONOMY_OK' ]]; then
  echo "ERROR: el contenido creado por el agente no coincide" >&2
  exit 1
fi

echo "PASS: Hermes originó y supervisó una tarea real ejecutada por Claude Code"
