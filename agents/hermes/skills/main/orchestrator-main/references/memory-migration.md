# Guía de Migración de Memoria Compartida

> Referencia histórica. Antes de migrar memoria, consulte el estado y las
> fuentes vigentes en `docs/DOCUMENTATION_INDEX.md`.

## Proceso de Verificación Obligatorio

### Paso 1: Escaneo de Referencias
```bash
grep -r "wiki_memoria" $HOME/ai-ecosystem \
  --include="*.py" --include="*.sh" --include="*.md" --include="*.json"
```

### Paso 2: Actualización Masiva de Rutas
```bash
# Reemplazar todas las ocurrencias
sed -i 's|wiki_memoria|sharememory|g' $(grep -rl "wiki_memoria" $HOME/ai-ecosystem)
```

### Paso 3: Verificación de Integridad
```bash
npm run test  # Verificar que no se rompe nada
git diff --stat  # Ver cambios
```

### Paso 4: Eliminación Segura
```bash
rm -rf $HOME/ai-ecosystem/wiki_memoria
```

### Paso 5: Registro en Changelog
```bash
echo "$(date): Migración wiki_memoria → sharememory" >> CHANGELOG.md
```

## Ejemplo de Fallo Detectado

**Error**: El script `test_wiki.py` refería a `wiki_memoria` en 3 lugares diferentes.  
**Consecuencia**: Tests fallaron silenciosamente.  
**Solución**: Patrón de búsqueda + reemplazo masivo.

## Plantilla de Comando de Verificación
```bash
orchestrator-main "verificar migración memoria" --migrate-check
```

## Nota de Servicio
Siempre usar `orchestrator-main --detect` antes de eliminar cualquier directorio de memoria para identificar dependencias.
