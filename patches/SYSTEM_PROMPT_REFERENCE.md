# System Prompt Reference - Patch Management System

> **Existe un sistema permanente de gestión y respaldo de parches:**
> - **Carpeta central**: `/home/fernando/ai-ecosystem/patches/` - contiene documentación, backups e historial de todos los parches
> - **Skill específico**: `patch-management` - ubicado en `~/.hermes/skills/patch-management/`
> - **Regla obligatoria**: **Antes y después de actualizar Hermes Agent, plugins, dependencias o cualquier componente modificado, debe consultarse el skill `patch-management` y la carpeta central de parches.**

## Referencia Rápida para el Agente

```
📌 REGLA: "Existe un sistema de gestión de parches. Consúltalo antes/después de actualizar."
📁 Ubicación: /home/fernando/ai-ecosystem/patches/
🛠️ Skill: patch-management
⚡ Acción: patch-management "revisar" | "verificar" | "migrar" | "revertir"
```

---

## Integración con Flujo de Actualización

| Evento | Acción Requerida | Skill/Comando |
|--------|------------------|---------------|
| **Actualizar Hermes Agent** | `patch-management "revisar antes de actualizar"` | patch-management |
| **Actualizar plugin/dependencia** | `patch-management "revisar antes de actualizar"` | patch-management |
| **Post-actualización** | `patch-management "verificar parches"` | patch-management |
| **Nuevo parche creado** | `patch-management "registrar nuevo parche"` | patch-management |
| **Revertir parche** | `patch-management "revertir"` | patch-management |
| **Migrar parche** | `patch-management "migrar"` | patch-management |

---

## Documentación Obligatoria (mantenida en patches/)

Para cada parche se conserva:
1. Parche original (`.patch`, `.diff`)
2. Problema que resolvía y comportamiento esperado
3. Componente y versión afectada
4. Archivos/funciones/configuraciones afectados
5. Dependencias relacionadas
6. Procedimiento de aplicación y reversión
7. Pruebas realizadas y resultados
8. Criterios de necesidad continua
9. Instrucciones de migración/reconstrucción
10. Puntos equivalentes en versiones futuras
11. Historial de adaptaciones (v1 → v2 → v3...)
12. Relación con otros parches
13. Estado actual (activo, migrado, obsoleto, etc.)

---

## Decisiones de Migración (estados soportados)

```
activo → pendiente de revisión → compatible
    ↓
migrado → adaptado → reaplicado
    ↓
reemplazado → integrado upstream → obsoleto → retirado
```

---

## Principio Fundamental

> **No solo se conserva el archivo del parche, sino el CONOCIMIENTO necesario para reconstruir la modificación aunque el código original haya cambiado completamente.**

La carpeta `patches/` es la **fuente de verdad permanente**. El skill `patch-management` proporciona el **procedimiento** para trabajar con ella.