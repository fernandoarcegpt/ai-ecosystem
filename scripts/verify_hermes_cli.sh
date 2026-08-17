#!/usr/bin/env bash
set -euo pipefail

if ! command -v hermes >/dev/null 2>&1; then
  echo "ERROR: no se encontró 'hermes' en PATH" >&2
  exit 2
fi

if ! hermes plugins list 2>&1 | grep -q "neurosymbolic-integration"; then
  echo "ERROR: Hermes no descubre el plugin neurosymbolic-integration" >&2
  echo "Instálalo en ~/.hermes/plugins/ y habilítalo con:" >&2
  echo "  hermes plugins enable neurosymbolic-integration" >&2
  exit 3
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
  if ! grep -q "ENGINE=$engine STATUS=success" "$proof_log"; then
    echo "ERROR: el hook no registró éxito para $engine" >&2
    sed -n '1,120p' "$proof_log" >&2
    return 1
  fi
  if ! grep -q "CONTEXT_INJECTED" "$proof_log"; then
    echo "ERROR: $engine ejecutó, pero no inyectó contexto" >&2
    return 1
  fi
  echo "PASS: $engine ejecutado e inyectado en Hermes CLI"
}

verify_engine "networkx" "Detecta el ciclo del grafo A -> B -> C -> A"
verify_engine "z3" "Resuelve las restricciones x > 10 y x < 5"
verify_engine "pydatalog" "Ana es madre de Luis y Luis es padre de Marta. ¿Es Ana ancestro de Marta?"

echo "PASS: integración Hermes CLI extremo a extremo (3/3 motores)"
