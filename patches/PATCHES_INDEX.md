# Bitácora de Parches y Modificaciones del Proyecto

> **Estado: histórico y reemplazado.** El catálogo vigente, que distingue
> evidencia, respaldos y riesgos, es `docs/PATCH_CATALOG.md`.

> **Propósito**: Registro centralizado de todos los cambios significativos realizados en el proyecto, complementando el historial de Git con contexto técnico, decisiones, pruebas e incidencias.

## 📅 Tabla de Contenidos

| Fecha | Parche | Componente | Estado | Dependencias | Resultado |
|-------|--------|------------|--------|--------------|-----------|
| 2026-08-07 | Creación de estructura de parches | `patches/` | ✅ Verificado | - | Estructura completa creada |
| 2026-08-04 | knowledge_broker_db_path | `src/ingest.py` | ✅ Aplicado | kùzudb, propertygraphindex | Ruta DB corregida, base de datos funcional |
| 2026-08-02 | notex_audio_only_imports | `notex/main.go` | ⚠️ Revisar | runtime, time | Importes actualizados parcialmente (modo audio-only) |

---

## 📅 Cronología de Cambios (2026-08-02 a 2026-08-07)

### 2026-08-02 - notex_audio_only_imports
**Archivo**: `notex/main.go`  
**Tipo**: Refactorización de arquitectura  
**Objetivo**: Reducir Notex a un modo **audio-only** para grabación y transcripción.

#### Cambios Clave:
- Eliminación de importaciones no utilizadas (`golog`, `rotatelogs`)
- Mantenimiento de importaciones críticas para audio: `runtime`, `time`
- Añadida dependencia `runtime` para funciones de stack tracing

#### Contexto:
- Se introdujo un nuevo modo de operación (`-audio-only`) para que Notex se centre en funciones de audio
- Se implementaron validaciones en el código para asegurar que solo se use con transcripción de audio
- Se añadió soporte para `runtime.Stack` para manejo de excepciones en modo audio

**Ver más**: [notex_audio_only_imports](/patches/2026-08-02_notex_audio_only_imports/)

---

### 2026-08-04 - knowledge_broker_db_path
**Archivo**: `src/ingest.py`  
**Tipo**: Corrección de configuración / Ruta de archivo

#### Problema Principal:
La ruta de la base de datos KùzuDB no incluía la extensión `.kuzu`, causando fallos en la inicialización del motor de base de datos vectorial.

#### Solución Aplicada:
```diff
- db_path = "$HOME/ai-ecosystem/storage/kuzu/knowledge_base"
+ db_path = "$HOME/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
```

#### Detalles Técnicos:
- Se añadió la extensión `.kuzu` para coincidir con la convención de archivos de base de datos KùzuDB
- Se verificó que el directorio `storage/kuzu/` existiera antes de crear el archivo
- Se mantuvo el proceso de limpieza de archivos previos para evitar conflictos

#### Dependencias Afectadas:
- **kùzudb** - Motor de base de datos vectorial
- **propertygraphindex** - Índice de grafo para consultas semánticas

#### Resultado Verificado:
- ✅ Base de datos creada correctamente en `storage/kuzu/knowledge_base.kuzu`
- ✅ Pipeline de ingestión ejecutándose sin errores de ruta
- ✅ PropertyGraphIndex integrado y funcional

**Ver más**: [knowledge_broker_db_path](/patches/2026-08-04_knowledge_broker_db_path/)

---

## 📊 Registro de Dependencias por Parche

| Parche | Dependencias Críticas | Dependencias Secundarias | Estado de Migración |
|--------|----------------------|--------------------------|---------------------|
| knowledge_broker_db_path | kùzudb, propertygraphindex | - | ✅ Compatible con v1.0 |
| notex_audio_only_imports | runtime, time | golog, rotatelogs (eliminadas) | ⚠️ Pendiente de revisión |

---

## 🔄 Historial de Estados de Parche

| Patch | Estado Inicial | Estado Post-Actualización | Acción Requerida |
|-------|----------------|---------------------------|------------------|
| knowledge_broker_db_path | pendiente_revision | compatible | Mantener documentación actual |
| notex_audio_only_imports | pendiente_revision | adaptado | Guardar en history/ |

---

## 📝 Metadatos del Sistema

| Campo | Valor |
|-------|-------|
| Total de parches registrados | 2 |
| Última actualización | 2026-08-17 |
| Skill principal | patch-management |
| Cron job activo | 0 0 * * * (backup diario a las 12 AM) |
| Verificación automática | Pendiente (skill patch-verification) |
