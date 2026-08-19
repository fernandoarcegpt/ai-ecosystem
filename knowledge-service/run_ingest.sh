#!/usr/bin/env bash
# Knowledge Broker Service - Ingestion Runner
# Ejecuta la pipeline de ingestión de PDFs en KuZu y prepara el almacenamiento

set -euo pipefail

# Configuración de ambiente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${AI_ECOSYSTEM_ROOT:-$(dirname "$SCRIPT_DIR")}"
VENV_PATH="${AI_ECOSYSTEM_VENV:-$PROJECT_ROOT/.venv}"
DATA_DIR="$PROJECT_ROOT/data/raw"
LOG_FILE="$PROJECT_ROOT/storage/kuzu/ingest_$(date +%Y%m%d_%H%M%S).log"

# Activar entorno virtual
if [[ ! -x "$VENV_PATH/bin/python" ]]; then
    echo "ERROR: no existe el entorno Python en $VENV_PATH" >&2
    echo "Crea .venv e instala requirements.txt antes de ingerir." >&2
    exit 2
fi

# Crear directorios necesarios si no existen
mkdir -p "$PROJECT_ROOT/storage/kuzu"
mkdir -p "$PROJECT_ROOT/storage/logs"
mkdir -p "$DATA_DIR"

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"

echo "=== Knowledge Broker Ingestion Started at $(date) ==="

# Ejecutar script de ingestión con logging
set +e
"$VENV_PATH/bin/python" "$PROJECT_ROOT/src/ingest.py" 2>&1 | tee -a "$LOG_FILE"
EXIT_CODE=${PIPESTATUS[0]}
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Ingestion completed successfully at $(date) ==="
    echo "=== Stats will show in query.py or via get_stats() ==="
else
    echo "=== ERROR: Ingestion failed with exit code $EXIT_CODE ==="
fi

exit $EXIT_CODE
