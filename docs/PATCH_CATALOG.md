# Catálogo vigente de parches, migraciones y respaldos

> Fuente principal para determinar la vigencia de artefactos bajo `patches/`.
> Revisado el 2026-08-17 contra la rama
> `fix/core-verification-and-orchestration`. Un diff o informe no demuestra por
> sí solo que el cambio esté aplicado.

| Parche o colección | Ruta | Problema o finalidad | Componente | Estado | Evidencia y versión | Dependencias y riesgos |
|---|---|---|---|---|---|---|
| Notex audio-only | `patches/2026-08-02_notex_audio_only_imports/` | Propuesta de simplificación de imports para un modo de audio | `notex/main.go` | Obsoleto | El objetivo no existe en el árbol actual; `notex/main.go` tampoco existe | No aplicar el diff sobre otro proyecto sin identificar su commit base |
| Ruta de Kùzu | `patches/2026-08-04_knowledge_broker_db_path/` | Añadir `.kuzu` a la ruta de la base | `src/ingest.py` | Aplicado | El sufijo sigue vigente; el 2026-08-17 la ruta fija fue sustituida por `KNOWLEDGE_DB_PATH` con default relativo | La limpieza de `knowledge_base*` sigue siendo un riesgo operativo |
| Copia automática del árbol | `patches/2026-08-17_auto_copied_files/` | Respaldo masivo importado con metadatos | múltiples | Solo respaldo | `metadata.json`; no hay evidencia de aplicación como parche | Puede contener documentación duplicada o desfasada; no es fuente operativa |
| Historial de respaldos | `patches/backups/history/` | Preservar instantáneas anteriores | múltiples | Solo respaldo | Árbol versionado sin relación única con un commit demostrable | Gran volumen, duplicados y rutas antiguas; consultar solo para recuperación |
| Infraestructura de registro | `patches/PARTE_GENERAL.md` | Bitácora original de dos parches | proceso documental | Reemplazado | Reemplazado por este catálogo | Conserva afirmaciones históricas no reproducidas |
| Índice anterior | `patches/PATCHES_INDEX.md` | Índice y guía original del directorio | proceso documental | Reemplazado | Reemplazado por este catálogo | Contiene rutas y comandos inexistentes |
| Plantilla de parche | `patches/plantillas/PARTE_Tipo.md` | Formato para documentar parches futuros | proceso documental | Pendiente | Plantilla presente; no validada como automatización | Debe registrar evidencia y evitar declarar estados sin prueba |
| Referencia de prompt | `patches/SYSTEM_PROMPT_REFERENCE.md` | Conservar instrucciones de sistema anteriores | prompts | Solo respaldo | Archivo presente; no se carga por el runtime verificado | Puede contradecir instrucciones actuales; no copiar como configuración activa |

## Criterio de estados

- **Pendiente**: existe una intención o artefacto, sin evidencia de aplicación.
- **Aplicado**: el resultado esperado se observa en el código actual.
- **Reemplazado**: otro documento o parche es la referencia vigente.
- **Obsoleto**: el objetivo ya no existe o no corresponde al árbol actual.
- **Solo respaldo**: se conserva para recuperación o trazabilidad y no debe ejecutarse.

## Mantenimiento

Al crear o importar un parche, añádalo aquí y en
[`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md). Antes de marcarlo aplicado,
registre el archivo objetivo, una evidencia observable y, si puede
determinarse, el commit o rama. Si no puede demostrarse, use **Pendiente**.
