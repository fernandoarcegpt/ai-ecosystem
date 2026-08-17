#!/bin/bash
# Script de integración codebase-memory-mcp para ecosistema Hermes

# Variables de configuración
HERMES_PROJECT="/home/fernando/ai-ecosystem"
CBM_PATH="/tmp/test_cbm"  # Proyecto de prueba temporal
CACHE_DIR="$HOME/.cache/codebase-memory-mcp"

# 1. Limpieza inicial
function cleanup {
    echo "🧹 Limpieza..."
    rm -rf "$CBM_PATH" "$CACHE_DIR"
    echo "✓ Limpieza completada"
}

# 2. Instalación global
function install_cbm {
    echo "🔄 Instalando codebase-memory-mcp global..."
    npm install -g codebase-memory-mcp@0.8.1 || { echo "❌ Instalación fallida"; cleanup; exit 1; }
    echo "✓ Instalación completada"
}

# 3. Configuración de .mcp.json
function config_mcp {
    echo "🛠️ Actualizando configuración de .mcp.json..."
    cat <<EOF > "$HERMES_PROJECT/.mcp.json"
{
  "mcpServers": {
    "codebase-memory-mcp": {
      "command": "codebase-memory-mcp",
      "args": [],
      "optional": true
    }
  }
}
EOF
    echo "✓ Configuración actualizada"
}

# 4. Configuraciónfter instala
function init_environment {
    echo "🌐 Actualizando PATH para binarios globales..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    source "$HOME/.bashrc"
    echo "✓ PATH actualizado"
}

# 5. Pruebas funcionalitas
function run_tests {
    echo "🚀 Ejecutando pruebas de funcionalidad..."
    
    # Prueba 1: Verificación de ayuda
    echo "\n🔍 Prueba 1: Ayuda CLI"
    codebase-memory-mcp --help || { echo "❌ Prueba 1 fallida"; cleanup; exit 1; }
    
    # Prueba 2: Indexeo del proyecto de prueba
    echo "\n🔍 Prueba 2: Indexeo con repo_path"
    mkdir -p "$CBM_PATH"
    echo "# Test Project" > "$CBM_PATH/README.md"
    echo "import os" > "$CBM_PATH/test_file.py"
    
    codebase-memory-mcp cli index_repository '{"repo_path": "'"$CBM_PATH"'"}' --progress || { echo "❌ Prueba 2 fallida"; cleanup; exit 1; }
    
    # Prueba 3: Búsqueda básica
    echo "\n🔍 Prueba 3: Search code"
    codebase-memory-mcp cli search_code '{"pattern": "import", "limit": 5}' || { echo "❌ Prueba 3 fallida"; cleanup; exit 1; }

    # Prueba 4: Búsqueda gráfica
    echo "\n🔍 Prueba 4: Search graph"
    codebase-memory-mcp cli search_graph '{"name_pattern": "test_file", "limit": 5}' || { echo "❌ Prueba 4 fallida"; cleanup; exit 1; }

    echo "✓ Todas las pruebas exitosas"
}

# 6. Ejecución principal
echo "🚀 Iniciando integración codebase-memory-mcp..."
install_cbm
config_mcp
init_environment
run_tests
cleanup
echo "✅ Integración completada con éxito"