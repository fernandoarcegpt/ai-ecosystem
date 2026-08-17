#!/bin/bash
# Script wrapper para búsqueda automática de información de UNMSM
# Usa el skill playwright-browser para realizar búsquedas

# Activar entorno Playwright
source /home/fernando/ai-ecosystem/playwright-venv/bin/activate

# Verificar que se proporcionó una consulta
if [ $# -eq 0 ]; then
    echo "Uso: $0 \"tu consulta de búsqueda\""
    echo "Ejemplo: $0 \"primer puesto UNMSM medicina 2015\""
    echo "Ejemplo: $0 \"ingreso UNMSM 2012 primer puesto\""
    exit 1
fi

# Ejecutar script de búsqueda
python3 /home/fernando/ai-ecosystem/scripts/unmsm_search.py "$@"