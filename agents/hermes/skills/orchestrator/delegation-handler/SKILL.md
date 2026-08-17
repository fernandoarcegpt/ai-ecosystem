---
name: delegation-handler
description: "Skill que delega tareas complejas a habilidades especializadas, evitando ejecutarlas en Claude Code"
platforms: [linux]
---

# Delegation Handler

## Funcionalidad Principal
Este skill evalúa tareas y delega a habilidades especializadas cuando es necesario, evitando que se ejecuten en Claude Code:

- ✅ Evaluación de complejidad
- ✅ Identificación de skills requeridas
- ✅ Enrutamiento a skills adecuadas

## Flujo de Ejecución
1. **Análisis de tarea**: Identifica palabras clave y scope
2. **Búsqueda en memory**: Revisa si tiene contexto existente
3. **Evaluación de riesgo**: Determina si necesita delegación
4. **Asignación:**
   - ♍ Tareas simples: Ejecuta internamente
   - 🔍 Tareas técnicas: Asigna a skills especializadas (ej: quant-analyst)
   - 🔭 Tareas casi imposibles: Notifica al usuario

## Parámetros Clave
```bash
--task "descripción tarea"
--required-skills [skill1, skill2]
--priority [alta/mediana/baja]
--deadline [timestamp]
```

## Ejemplo de Enlace
```bash
delegation-handler "optimizar cartera con z-scores" 
  --required-skills [portfolio-optimization, data-verifier] 
  --priority alta 
  --deadline "2026-08-01"
```

## Integraciones
- Connects a `orchestrator-main`
- Uses `memory_search` before delegating
- Calls skipped tasks to `research-search-master`

## Proceso de Failure
1. ⚠️ Si delegación no responde en 30s: Retry una vez
2. ⚠️ Si devuelve error: Usa `research-search-master` como fallback
3. ❌ Task concluido: Notifica al orchestrator