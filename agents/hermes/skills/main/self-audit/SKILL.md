---
name: self-audit
description: "Skill para evaluar cambios en el ecosistema: verifica que las habilidades y archivos modificados sean consistentes, válidos y no rompan la integración. Incluye detección de cambios no declarados y evaluación de consistencia de descripciones vs implementación."
platforms: [linux, macos, windows]
tags: [audit, self-evaluation, validation, monitoring]
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Self-Audit Skill

> Antes de auditar, consulte `docs/DOCUMENTATION_INDEX.md` para seleccionar las
> fuentes del área. La verificación ejecutable vigente es `npm run verify:all`;
> los comandos no presentes en `package.json` o `scripts/` son históricos.

## Propósito

Esta habilidad permite **evaluar cambios** en el ecosistema de forma dinámica, asegurando que:

1. **Todas las habilidades** (incl. `orchestrator-main`, `research-search-master`, etc.) sigan siendo **funcionales** después de cualquier modificación.  
2. **Los archivos** (SKILL.md, scripts, configuraciones) cumplan con **sintaxis y convenciones** del proyecto.  
3. **Los cambios** realizados en el sistema son **evaluados** para confirmar que no introducen incoherencias o vulnerabilidades.  

## Flujo de trabajo

1. **Detectar cambios**:  
   - Ejecutar `self-audit --detect` para listar archivos modificados recientemente.  
2. **Evaluar cambios**:  
   - Ejecutar `self-audit --audit` para validar cada cambio detectado.  
   - El skill verifica:  
     - Sintaxis de archivos (markdown, bash, JSON, etc.).  
     - Coherencia entre la descripción del skill y su implementación.  
     - Ausencia de dependencias rotas (p.ej., referencias a skills que ya no existen).  
3. **Reporte**: genera un informe detallado con:  
   - Lista de cambios detectados.  
   - Estado de cada cambio (✅ válido, ⚠️ advertencia, ❌ error crítico).  
   - Recomendaciones de corrección.  

## Comandos disponibles

| Acción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--detect` | Lista los archivos modificados en los últimos 24 h. | `self-audit --detect` |
| `--audit` | Ejecuta la validación completa de los cambios detectados. | `self-audit --audit` |
| `--repair` | Aplica correcciones automáticas a errores comunes (p.ej., sintaxis de markdown, paths incorrectos). | `self-audit --repair` |
| `--help` | Muestra ayuda y ejemplos de uso. | `self-audit --help` |

## Flujo de trabajo recomendado

1. **Antes de crear o modificar una skill**:  
   - Ejecuta `self-audit --detect` para confirmar que no existen cambios pendientes que puedan interferir.  
2. **Realiza los cambios** (edita archivos, añade skills, etc.).  
3. **Ejecuta** `self-audit --audit` para validar que todo sigue funcionando.  
4. Si el resultado muestra errores críticos, corrígelos y repite el proceso hasta que el estado sea **✅ valid**.  

## Buenas prácticas

- **No modificar** archivos de habilidades sin antes ejecutar `self-audit --detect`.  
- **Mantener** la consistencia entre la descripción del skill (frontmatter) y su contenido real.  
- **Probar** cualquier cambio con `orchestrator-main` antes de considerarlo definitivo.  
- **Documentar** cualquier cambio relevante en la sección de *Change Log* del skill correspondiente.

## Notas técnicas

- La herramienta usa `git` internamente para detectar cambios en archivos bajo control de versión (si el repositorio está versionado).  
- Si el proyecto no usa git, el skill se basa en timestamps de modificación de archivos.  
- La evaluación incluye **sintaxis**, **coherencia de descripción**, y **compatibilidad de dependencias** (p.ej., referencias a skills que ya no existen).  

## Ejemplo de uso

```bash
# 1. Verificar qué archivos cambiaron en las últimas 24h
self-audit --detect

# 2. Ejecutar la auditoría completa
self-audit --audit

# 3. Si aparecen errores críticos, aplicar la corrección sugerida y volver a ejecutar --audit
self-audit --repair   # (opcional, solo si se detectaron errores automáticos)
```

## Notas importantes

- **No se ejecuta automáticamente** en cada cambio; el usuario debe invocar `--audit` manualmente o programar una tarea cron para hacerlo periódicamente.  
- La auditoría **no modifica** archivos por sí misma, solo informa y, opcionalmente, aplica correcciones simples con `--repair`.  
- La auditoría se ejecuta en el **directorio de trabajo actual**; asegúrate de estar en la raíz del proyecto (`$HOME/ai-ecosystem`) antes de correrla.

---

**Este skill complementa a `orchestrator-main` y garantiza que cualquier modificación en el ecosistema sea **evaluada** antes de considerarse válida.**
