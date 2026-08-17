# Plantilla PARTE.md para Nuevos Parches

## Plantilla para Documentación de Parches

Use esta plantilla al crear una nueva entrada en el repositorio de parches.

---

## Parche: [nombre_descriptivo]

**Fecha**: YYYY-MM-DD  
**Sesión**: [session_id]  
**Componente**: [ruta/al/archivo]  
**Tipo**: [corrección/arquitectura/funcionalidad/etc.]

---

## �� 🛠��️ Descripción del Problema

[Descripción detallada del problema que motivó el parche]

## �� 🔧 Solución Aplicada

### Diff Completo

```diff
--- a/[ruta/al/archivo]
+++ b/[ruta/al/archivo]
[contenido del diff]
```

### Estado Actual Verificado

[Queda confirmado en el archivo modificado]

---

## �� 🎯 Impacto

| Aspecto | Antes | Después |
|---------|-------|---------|
| [Aspecto] | [Estado] | [Estado] |

---

## �� 📊 Pruebas Realizadas

[Enlace o referencia al archivo `pruebas/test_result.txt`]

---

## �� 🐛 Problemas Encontrados

1. [Problema 1]  
   - **Causa**: [Explicación]  
   - **Solución**: [Cómo se resolvió]  
2. [Problema 2]  

---

## � ✅ Verificación Final

- [ ] Checklist de verificaciones realizadas
- [ ] [ ] Pruebas automáticas ejecutadas
- [ ] [ ] Validación manual completada

---

## �� 📚 Referencias

- **Sesión original**: [session_id]  
- **Archivo modificado**: [ruta/al/archivo]  
- [Otros enlaces relevantes]