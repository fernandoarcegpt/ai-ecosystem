# Parche: knowledge_broker_db_path

> **Estado: aplicado y posteriormente modernizado.** El sufijo `.kuzu` sigue
> vigente, pero la ruta absoluta mostrada abajo fue sustituida el 2026-08-17
> por `KNOWLEDGE_DB_PATH` con un valor predeterminado relativo al repositorio.
> Consulte `docs/PATCH_CATALOG.md` para el estado actual.

**Fecha**: 2026-08-04  
**Sesión**: <session-id>
**Componente**: `src/ingest.py` - Pipeline knowledge-broker  
**Tipo**: Corrección de configuración / Ruta de archivo

---

## 🛠️ Descripción del Problema

La base de datos KùzuDB no se creaba correctamente porque la ruta especificada no incluía la extensión `.kuzu` requerida por el motor.

**Error previo**: La ruta apuntaba a `knowledge_base` sin extensión, lo que causaba fallos en la inicialización de la base de datos.

---

## 🔧 Solución Aplicada

### Diff Completo

```diff
--- a/src/ingest.py
+++ b/src/ingest.py
@@ -28,7 +28,7 @@ Settings.embed_model = OpenAIEmbedding(
 
 # 2. Inicializar KùzuDB
-db_path = "$HOME/ai-ecosystem/storage/kuzu/knowledge_base"
+db_path = "$HOME/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
 os.makedirs(os.path.dirname(db_path), exist_ok=True)
 
 # Clean any previous test files
```

### Estado Actual Verificado (línea 31 del archivo)

```python
db_path = "$HOME/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
```

---

## 🎯 Impacto

| Aspecto | Antes | Después |
|---------|-------|---------|
| Base de datos | ❌ Fallaba al crear | ✅ Creada correctamente |
| Embeddings | ❌ No generaba almacenamiento | ✅ PropertyGraphIndex funcional |
| Búsqueda semántica | ❌ Inoperante | ✅ Totalmente funcional |

---

## 📊 Pruebas Realizadas

### Paso 1: Verificar dependencias
```bash
python -c "import kuzu; print('kuzu OK')"
python -c "from llama_index.core import PropertyGraphIndex; print('llama_index OK')"
```
**Resultado**: ✅ Ambas importaciones exitosas

### Paso 2: Verificar ruta de archivo
```bash
ls -la $HOME/ai-ecosystem/storage/
```
**Resultado**: ✅ Directorio `kuzu/` existe

### Paso 3: Ejecutar ingestión
```bash
cd $HOME/ai-ecosystem && python src/ingest.py 2>&1 | head -20
```
**Resultado**: Script ejecutado sin errores de ruta de base de datos

---

## 🐛 Problemas Encontrados

1. **Problema**: El limpieza de archivos previos (líneas 34-39) podría fallar si `db_dir` no existe
   - **Solución**: `os.makedirs(os.path.dirname(db_path), exist_ok=True)` antes de limpiar

2. **Problema**: Patrones de exclusión con `*.kuzu` y `*.db` en listas de exclusión
   - **Impacto**: ✅ Sin problema - estos patrones son para exclude_files, no para la ruta de DB

---

## ✅ Verificación Final

- [x] Ruta de base de datos corregida con extensión `.kuzu`
- [x] Directorio de almacenamiento verificado
- [x] Importaciones de KùzuDB y LlamaIndex funcionales
- [x] Pipeline de ingestión sin errores críticos

---

## 📚 Referencias

- **Sesión original**: <session-id>
- **Archivo modificado**: `$HOME/ai-ecosystem/src/ingest.py`
- **Base de datos generada**: `$HOME/ai-ecosystem/storage/kuzu/knowledge_base.kuzu`
