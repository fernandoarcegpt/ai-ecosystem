# Herramientas de Uso

## Utilidades para configurar y probar el razonamiento neurosimbólico

### generate-test-env.sh
```bash
#!/bin/bash
# Crea un entorno virtual limpio, instala dependencias, ejecuta tests básicos

set -e

PROJECT_ROOT="/home/fernando/ai-ecosystem"
VENV_PATH="$PROJECT_ROOT/.venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creando entorno virtual..."
python3 -m venv "$VENV_PATH"

source "$VENV_PATH/bin/activate"

echo "Instalando dependencias..."
pip install --upgrade pip
pip install networkx z3-solver pyDatalog

echo "Habilitando Python packages..."
export PYTHONPATH="$PROJECT_ROOT/skilled:$PYTHONPATH"

echo "Ejecutando tests básicos..."
python3 "$SCRIPT_DIR/test_neurosymbolic.py"

echo "✓ Setup y tests completados!"
deactivate
```