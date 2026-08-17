#!/bin/bash
# Script wrapper para process-document.py
# Uso: ./scripts/process-document.sh "Título Guía" [pdf|txt|image] [ruta_archivo]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Procesador de Documentos para Notex y OKF ===${NC}"
echo "Ejecutando: python3 $SCRIPT_DIR/process-document.py $*"

python3 "$SCRIPT_DIR/process-document.py" "$@"