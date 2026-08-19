# Documentación

El punto de entrada es [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md). El
índice indica qué documento es principal, cuál es histórico, cuándo debe
consultarse y qué cambios obligan a actualizarlo.

Referencias principales:

- [Arquitectura vigente](../ARCHITECTURE.md)
- [Operación y pruebas](../README.md)
- [Historial de cambios y versiones](../CHANGELOG.md)
- [Instrucciones para agentes](../CLAUDE.md)
- [Política de conservación y no borrado](RETENTION_POLICY.md)
- [Catálogo de parches](PATCH_CATALOG.md)
- [Informe de verificación](verification-report.md)

El historial de cambios distingue la versión general de `ai-ecosystem` de la
versión propia del plugin `neurosymbolic-integration`, y debe actualizarse ante
cambios funcionales, de arquitectura, contratos de tool, motores o criterios
de verificación.

La política de conservación es obligatoria: los agentes no destruyen contenido
del proyecto. Cuando algo deba retirarse de su ubicación activa se mueve a
`vault/`, se registra en `vault/INDEX.md` y queda pendiente de revisión manual
del propietario.

La documentación específica de la calculadora que antes ocupaba este archivo
queda representada por `src/taskhero/README.md` y las pruebas de la aplicación;
este directorio vuelve a cumplir su función de entrada documental general.
