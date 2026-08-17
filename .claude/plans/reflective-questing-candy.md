# Plan: Implementar una Wiki de Memoria basada en archivos planos (Open Knowledge Format)

## 1. Contexto y objetivo
- La wiki debe almacenar notas y contenidos en archivos de texto (Markdown) dentro de `~/ai-ecosystem/staging/` → `~/ai-ecosystem/vault/`.
- Cada nota representa un "bocado" de memoria que será validado y trasladado al vault mediante el **Knowledge Broker** (`knowledge_broker.py`).
- El flujo incluye: listado de archivos, validación del contenido, escritura segura en el vault y limpieza automática del staging.

## 2. Requisitos funcionales
1. **Listado** de todos los archivos `.md` en `staging/`.
2. **Validación** del formato (no vacío, sintaxis básica Markdown aceptada).
3. **Escritura** en el vault mediante la función `write_to_vault` del broker.
4. **Eliminación** del archivo del staging tras escritura exitosa.
5. **Registro** de acciones (éxitos, rechazos, errores) en consola y opcionalmente en log.

## 3. Arquitectura propuesta
- **Script principal:** `process_wiki.py` (a ejecutar manualmente o vía CLI).
- **Utilidades auxiliares:**
  - `list_wiki_files()` – devuelve rutas de archivos .md.
  - `validate_content(content)` – evalúa reglas de validación.
  - `write_wiki_file(path, content)` – llama a `write_to_vault`.
- **Integración con Knowledge Broker:** usar funciones exportadas (`validate`, `write_to_vault`, `process_staging`).

## 4. Flujo de trabajo paso a paso
1. **Escaneo**: `list_wiki_files()` recopila rutas en `staging/`.
2. **Validación**: Cada contenido pasa por `validate()`. Si `aprobado == True`, continúa.
3. **Escritura**: `write_wiki_file()` invoca `write_to_vault(filename, content)` del broker.
4. **Post‑proceso**: Si la escritura devuelve éxito, el archivo se elimina de `staging/`.
5. **Feedback**: Mensajes en consola indican estado de cada archivo.

## 5. Archivo de planificación (reflective‑questing‑candy.md)
- Este documento (ubicado en `/home/fernando/.claude/plans/`) describe la solución completa y sirve como referencia para futuros ajustes.
- Contendrá:
  - Descripción del problema y objetivo.
  - Diagrama de flujo (texto).
  - Lista de scripts y módulos a crear/modificar.
  - Consideraciones de seguridad (uso de API key, verificación de SSL).
  - Pruebas de aceptación (ejecutar script con notas de prueba y observar resultados en `vault/`).

## 6. Requisitos técnicos
- Python 3.9+.
- Paquetes: `requests`, `urllib3`, `python-dotenv`.
- Variables de entorno en `.obsidian-broker/.env`:
  - `OBSIDIAN_PORT`
  - `OBSIDIAN_API_KEY`
- Permisos de escritura en `vault/` y `staging/`.

## 7. Verificación y pruebas
1. Crear notas de ejemplo en `staging/` con contenido válido y no válido.
2. Ejecutar `python process_wiki.py`.
3. Confirmar que:
   - Las notas válidas aparecen en `vault/`.
   - Las notas inválidas permanecen en `staging/` con mensaje de rechazo.
   - Los archivos procesados se eliminan de `staging/`.
4. Revisar salida en consola para cualquier error o warning.

## 8. Próximos pasos
- Automatizar la ejecución mediante un *hook* de shell o mediante el CLI de Ruflo (`/loop`).
- Añadir *logging* estructurado (JSON) para auditoría.
- Exponer una pequeña interfaz de línea de comandos (`wiki add <path>` / `wiki sync`) que envuelva el flujo.

--- 

*Este plan está listo para ser revisado y aprobado antes de iniciar la implementación.*