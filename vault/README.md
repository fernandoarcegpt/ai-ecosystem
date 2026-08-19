# Vault de conservación

Este directorio es el baúl de cuarentena de `ai-ecosystem`.

Los agentes y automatizaciones no deben borrar definitivamente contenido del proyecto. Cuando un archivo o directorio deje de ser necesario en su ubicación activa, debe trasladarse aquí siguiendo `docs/RETENTION_POLICY.md`.

## Reglas

- No purgar automáticamente este directorio.
- No usar `rm`, `git rm` ni APIs de borrado sobre su contenido.
- Conservar, cuando sea posible, la ruta original bajo una carpeta `YYYY-MM-DD/`.
- Registrar cada traslado en `vault/INDEX.md`.
- La eliminación definitiva queda reservada al propietario del repositorio y se realiza manualmente.

## Ejemplo

```text
vault/2026-08-19/path/original/archivo.ext
```

El baúl no debe utilizarse para conservar secretos o credenciales expuestas; esos casos requieren intervención humana específica.
