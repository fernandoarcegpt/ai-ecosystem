# Patrones de Verificación Post-Migración

## Script de Verificación Estándar

Este patrón se usa después de cambios estructurales en el repositorio (migraciones, limpiezas, reorganizaciones).

### Ubicación
`/home/fernando/ai-ecosystem/scripts/verify-migration.sh`

### Plantilla Reutilizable

```bash
#!/bin/bash
# Script de verificación post-migración para estructura de archivos

set -e

echo "🔍 Verificando migración de estructura..."

# 1. Verificar .gitignore actualizado
if grep -q "ollama/" .gitignore; then
    echo "✓ .gitignore incluye ollama/"
else
    echo "✗ .gitignore NO incluye ollama/"
    exit 1
fi

# 2. Verificar exclusiones críticas
for pattern in ".backup-before" "ruvector.db" "downloads/" "logs/"; do
    if grep -q "$pattern" .gitignore; then
        echo "✓ $pattern excluido"
    else
        echo "✗ $pattern NO excluido"
        exit 1
    fi
done

# 3. Verificar directorios críticos
for dir in src tests docs scripts procedures; do
    if [ -d "$dir" ]; then
        echo "✓ Directorio $dir existe"
    else
        echo "⚠ Directorio $dir NO existe"
    fi
done

# 4. Verificar skills disponibles
if [ -d ".hermes/skills/main/orchestrator-main" ]; then
    echo "✓ orchestrator-main skill disponible"
else
    echo "✗ orchestrator-main skill NO disponible"
    exit 1
fi

# 5. Verificar logs no versionados
if git ls-files logs/ 2>/dev/null | grep -q .; then
    echo "⚠ logs/ tiene archivos versionados"
else
    echo "✓ logs/ excluido correctamente"
fi

echo "✅ Verificación completada exitosamente"
```

### Uso con Orquestador

```bash
orchestrator-main "verificar migración" --run-script verify-migration.sh
# O directamente:
bash scripts/verify-migration.sh
```

## Lecciones de Playwright-Browser + DuckDuckGo

### Limitaciones Encontradas
- DuckDuckGo Lite bloquea con CAPTCHA (detección de "duck")
- Búsqueda principal devuelve principalmente interfaz, no resultados específicos
- UNMSM admisión 2012-2022 → resultados genéricos sin datos concretos

### Workarounds Efectivos
1. Usar `web_search` con API key configurada (si disponible)
2. Consultar fuentes oficiales directamente:
   - https://admisiones.unmsm.edu.pe/
   - https://www.unmsm.edu.pe/
3. Guardar resultados en archivo para referencia futura

## pnpm como Runner Estándar

El proyecto usa `pnpm` (no `npm`) como package manager:
- `pnpm run test` → ejecuta `bash scripts/test-trivial.sh`
- `pnpm run generate-specs` → ejecuta `./generate-specs.sh`
- Lockfile validado con supply-chain policies

### Configuración package.json
```json
{
  "packageManager": "pnpm@11.18.0+sha512...",
  "scripts": {
    "test": "bash scripts/test-trivial.sh",
    "generate-specs": "./generate-specs.sh"
  }
}
```

## Patrones de .gitignore para Monorepos

### Exclusiones Críticas (SIEMPRE)
```
# Modelos pesados
ollama/

# Backups y respaldos temporales
agents_backup_*/
claude_backup_*/
.backup-before-*

# Datos temporales
downloads/
staging/
logs/

# Bases de datos regenerables
ruvector.db

# Entornos de desarrollo (dentro del proyecto)
playwright-venv/
node_modules/
```

### Verificación Automática
```bash
# Verificar que patrones están en .gitignore
grep -E "(ollama|backup-before|ruvector|downloads|logs)" .gitignore
```