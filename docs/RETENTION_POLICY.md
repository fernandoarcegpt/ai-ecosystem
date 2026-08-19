# Política de conservación y no borrado

## Regla principal

En `ai-ecosystem` ningún agente, script, automatización ni flujo asistido debe eliminar de forma definitiva archivos o directorios del proyecto.

Cuando un elemento deje de ser necesario en su ubicación activa, debe **retirarse mediante traslado al baúl `vault/`**, conservando su contenido para revisión humana posterior.

La eliminación definitiva de elementos dentro de `vault/` queda reservada exclusivamente al propietario del repositorio y se realiza manualmente fuera de los flujos automáticos.

## Acciones prohibidas para agentes y automatizaciones

Salvo una instrucción humana explícita que cambie esta política, no se permite:

- `rm`, `rm -r`, `rm -rf` o equivalentes sobre contenido del proyecto;
- `git rm` como mecanismo de descarte definitivo;
- llamadas API de borrado de archivos;
- scripts de limpieza que eliminen contenido versionado;
- purgas automáticas dentro de `vault/`;
- reemplazar un archivo por una copia vacía como forma indirecta de borrado.

## Procedimiento correcto para retirar contenido

1. Verificar la ruta, tipo y función del elemento antes de moverlo.
2. Crear una ubicación bajo `vault/YYYY-MM-DD/` que preserve la ruta original.
3. Mover el elemento, preferentemente con una operación que conserve historial (`git mv` cuando se trabaja localmente).
4. Registrar el traslado en `vault/INDEX.md` con:
   - fecha;
   - ruta original;
   - ruta en el baúl;
   - motivo;
   - referencia al commit o tarea cuando exista;
   - estado `Pendiente de revisión manual`.
5. Actualizar `docs/DOCUMENTATION_INDEX.md` si el elemento retirado era documentación registrada.
6. No borrar después el contenido del baúl. La purga es manual y exclusiva del propietario.

## Estructura del baúl

Ejemplo:

```text
vault/
└── 2026-08-19/
    └── skilled/
        └── reasoning/
            └── modulo_obsoleto.py
```

La ruta posterior a la fecha debe reproducir, en lo posible, la ruta original. Esto permite saber de dónde salió cada elemento sin depender solo del historial de Git.

## Casos especiales

### Archivos reemplazados

Si un archivo vigente es sustituido por otro, el anterior se traslada al baúl salvo que ambos deban coexistir por compatibilidad.

### Duplicados o respaldos

Un duplicado confirmado se mueve al baúl; no se elimina automáticamente.

### Archivos generados

Los artefactos regenerables no versionados pueden seguir las reglas normales del entorno temporal (`/tmp`, cachés, entornos virtuales, etc.). Esta política protege el contenido del proyecto y especialmente el contenido versionado o deliberadamente conservado.

### Secretos o datos sensibles

Si se detecta accidentalmente un secreto, credencial o dato sensible, no debe copiarse automáticamente al baúl como método de conservación. El flujo debe bloquearse y solicitar intervención humana para rotación, saneamiento y eventual reescritura de historial. La política de no borrado no debe convertir el baúl en un almacén de secretos.

## Responsabilidad humana

`vault/` funciona como una zona de cuarentena y recuperación, no como una papelera automática. Solo el propietario decide qué elementos del baúl se eliminan definitivamente y cuándo hacerlo.

## Criterio operativo

Para agentes y automatizaciones, "eliminar" significa en realidad:

```text
retirar de ubicación activa
→ mover a vault/
→ registrar el movimiento
→ dejar pendiente de revisión manual
```

Nunca significa destrucción automática del contenido.
