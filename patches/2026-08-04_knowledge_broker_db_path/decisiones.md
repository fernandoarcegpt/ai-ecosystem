# Decisiones Técnicas - knowledge_broker_db_path

> Registro histórico. La decisión sobre `.kuzu` continúa vigente; la ruta fija
> fue reemplazada por configuración portable. Estado actual:
> `docs/PATCH_CATALOG.md`.

## Decisiones Tomadas Durante la Implementación

### 1. Elección de extensión .kuzu para archivo de base de datos
**Contexto**: KùzuDB requiere archivos con extensión `.kuzu` para el motor de base de datos embebido.
**Decisión**: Usar la convención estándar `.kuzu` en lugar de nombre sin extensión.
**Justificación**: Garantiza compatibilidad con el motor KùzuDB y evita errores de inicialización.
**Alternativas consideradas**: 
- Usar `.db` (rechazado - no específico de KùzuDB)
- Sin extensión (rechazado - causa errores de inicialización)

### 2. Limpieza proactiva de archivos previos
**Contexto**: Desarrollo iterativo genera múltiples archivos de prueba en el directorio de almacenamiento.
**Decisión**: Limpiar archivos `knowledge_base*` antes de crear nuevo.
**Justificación**: Evita conflictos con versiones anteriores y asegura estado limpio.
**Riesgo**: Podría eliminar bases de datos de producción si no se usa directorio dedicado.

### 3. Patrones de exclusión para archivos de base de datos
**Contexto**: `SimpleDirectoryReader` escanea recursivamente el repositorio.
**Decisión**: Excluir `*.kuzu` y `*.db` de la indexación.
**Justificación**: Previene indexación recursiva de los propios archivos de base de datos.
**Impacto**: Reduce ruido en embeddings y evita bucle de auto-indexación.

### 4. Configuración de modelo de embedding
**Contexto**: OpenRouter API proporciona acceso a modelos de OpenAI.
**Decisión**: Usar `text-embedding-3-small` (1536 dimensiones) por defecto.
**Justificación**: Balance costo/rendimiento para búsqueda semántica general.
**Alternativa**: `text-embedding-3-large` (3072 dims) para mayor precisión.

## Decisiones Pendientes

- [ ] Evaluar migración a modelo de embedding local (sentence-transformers)
- [ ] Considerar partición de embeddings por dominio/categoría
- [ ] Implementar versionado de esquema de PropertyGraph

---

## Análisis de Impacto

| Área | Impacto | Acción Requerida |
|------|---------|------------------|
| Pipeline de ingestión | Alto - resuelve bloqueo crítico | ✅ Completado |
| Búsqueda semántica | Alto - habilita funcionalidad completa | ✅ Completado |
| Memoria vectorial | Alto - base para memory system | ✅ Completado |
| Configuración OpenRouter | Medio - parámetros de modelo | ✅ Configurado |

---

## Lecciones Aprendidas

1. **Verificar convenciones de archivo** específicas de cada motor de base de datos
2. **Orden de operaciones**: Crear directorios antes de limpiar contenidos
3. **Patrones de exclusión** deben cubrir artefactos generados por el propio sistema
4. **Documentar extensiones de archivo** como parte de convenciones de proyecto
