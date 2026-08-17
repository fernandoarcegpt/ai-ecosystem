# Notas Técnicas - knowledge_broker_db_path

## Problemas Identificados y Soluciones

### Problema 1: Ruta sin extensión .kuzu
**Causa**: La instrucción de inicialización apuntaba a `"knowledge_base"` en lugar de `"knowledge_base.kuzu"`, lo que impedía que KùzuDB creara el archivo correctamente.

### Solución:
- Aplicar parche para incluir la extensión `.kuzu` en la ruta.
- Verificar que el directorio `storage/kuzu/` exista antes de crear el archivo.

### Problema 2: Limpieza de archivos previos
**Causa**: El código intentaba eliminar archivos previos en `db_dir` sin asegurar que el directorio existiera primero.

### Solución:
- Añadir `os.makedirs(os.path.dirname(db_path), exist_ok=True)` antes de intentar limpiar.
- Validar que la ruta del padre exista antes de operaciones de limpieza.

### Problema 3: Patrones de exclusión
**Causa**: Los patrones de exclusión en `exclude_patterns` no coincidían exactamente con archivos de base de datos.

### Solución:
- Añadir `"*.kuzu"` y `"*.db"` a `exclude_patterns` para evitar incluir accidentalmente nuevos archivos de base de datos durante rescaneos.

## Configuración Verificada

```python
# Ruta final confirmada (línea 31)
db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"

# Patrones de exclusión completos (líneas 57-66)
exclude_patterns = [
    "venv/*", ".venv/*", "storage/*", "data/*",
    "__pycache__/*", ".git/*", "*.kuzu", "*.db"
]
```

## Estado Final Verificado
- ✅ Base de datos KùzuDB creada correctamente
- ✅ Pipeline de ingestión ejecutándose sin errores críticos
- ✅ PropertyGraphIndex almacenando metadatos correctamente
- ✅ Acceso acumulativo a embeddings funcional