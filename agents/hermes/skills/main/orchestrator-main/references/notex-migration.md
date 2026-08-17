# Migración de MemorWise a Notex

## Contexto

Este documento describe la transición de **MemorWise** a **Notex** como componente de procesamiento e indexación de contenido en el flujo de trabajo de Z-Library.

### Cambios clave

1. **Sustitución del motor**: 
   - Se reemplazó `memorwise` por `neatx` (notex) como módulo de procesamiento.
   - Notex soporta ingestión directa mediante el modo `-ingest`.

2. **Modificaciones en el script**:
   - `downloader.sh` fue actualizado para llamar a `notex` en modo ingest.
   - Se eliminaron comandos específicos de `memorwise` y se añadieron verificaciones de `neatx`.

3. **Rutas de almacenamiento**:
   - Los metadatos ahora se guardan en `.hermes/library/downloads/` con el prefijo de notebook generado automáticamente.
   - El directorio de almacenamiento cambió de `.hermes/library/dynamic/` a `.hermes/library/downloads/`.

4. **Ventajas de la migración**:
   - API más robusta de ingestión.
   - Mejor manejo de formatos múltiples (PDF, texto, audio).
   - Integración nativa con Notex UI.

### Verificación post-migración

Ejecución de prueba confirmada:

```bash
cd /home/fernando/ai-ecosystem && ./scripts/downloader.sh "Prueba Z-Library" txt
```

Resultado: generar metadatos y preparar notebook en Notex.

### Notas para futuros agentes

- Verificar que `neatx` está compilado antes de ejecutar ingestión.
- Usar `markitdown` o `pdftotext` para extraer texto previo a ingestión.
- El notebook name sigue el patrón `TIMESTAMP_TITLE`.