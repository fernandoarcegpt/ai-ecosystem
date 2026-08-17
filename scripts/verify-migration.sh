#!/bin/bash
# Script de verificación post-migración para estructura de archivos

set -e

echo "🔍 Verificando migración de estructura..."

# 1. Verificar que .gitignore está actualizado
if grep -q "ollama/" .gitignore; then
    echo "✓ .gitignore incluye ollama/"
else
    echo "✗ .gitignore NO incluye ollama/"
fi

# 2. Verificar que backups están excluidos
if grep -q ".backup-before" .gitignore; then
    echo "✓ Backups excluidos de .gitignore"
else
    echo "✗ Backups NO excluidos de .gitignore"
fi

# 3. Verificar que ruvector.db está excluido
if grep -q "ruvector.db" .gitignore; then
    echo "✓ ruvector.db excluido"
else
    echo "✗ ruvector.db NO excluido"
fi

# 4. Verificar estructura de directorios críticos
for dir in src tests docs scripts procedures; do
    if [ -d "$dir" ]; then
        echo "✓ Directorio $dir existe"
    else
        echo "⚠ Directorio $dir NO existe (puede requerir creación)"
    fi
done

# 5. Verificar skills disponibles
if [ -d ".hermes/skills/main/orchestrator-main" ]; then
    echo "✓ orchestrator-main skill disponible"
else
    echo "✗ orchestrator-main skill NO disponible"
fi

# 6. Verificar que logs no están en .gitignore
if git ls-files logs/ 2>/dev/null | grep -q .; then
    echo "⚠ logs/ tiene archivos seguros, revisar .gitignore"
else
    echo "✓ logs/ vacío o excluido como esperado"
fi

echo "✅ Verificación completada"