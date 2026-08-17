#!/bin/bash
# Knowledge Broker Service - Ingestion Runner
# Ejecuta la pipeline de ingestión de PDFs en KuZu y prepara el almacenamiento

set -e

# Configuración de ambiente
VENV_PATH="/home/fernando/ai-ecosystem/venv"
PROJECT_ROOT="/home/fernando/ai-ecosystem"
DATA_DIR="$PROJECT_ROOT/data/raw"
LOG_FILE="$PROJECT_ROOT/storage/kuzu/ingest_$(date +%Y%m%d_%H%M%S).log"

# Activar entorno virtual
source "$VENV_PATH/bin/activate"

# Crear directorios necesarios si no existen
mkdir -p "$PROJECT_ROOT/storage/kuzu"
mkdir -p "$PROJECT_ROOT/storage/logs"
mkdir -p "$DATA_DIR"

# Cambiar al directorio del proyecto
cd "$PROJECT_ROOT"

echo "=== Knowledge Broker Ingestion Started at $(date) ==="

# Ejecutar script de ingestión con logging
python "$PROJECT_ROOT/src/ingest.py" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "=== Ingestion completed successfully at $(date) ==="
    echo "=== Stats will show in query.py or via get_stats() ==="
else
    echo "=== ERROR: Ingestion failed with exit code $EXIT_CODE ==="
fi

exit $EXIT_CODE