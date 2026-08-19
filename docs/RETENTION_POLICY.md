# Política de conservación y no borrado

## Regla principal

En `ai-ecosystem` ningún agente, script, automatización ni flujo asistido debe eliminar de forma definitiva archivos o directorios del proyecto.

Cuando un elemento deje de ser necesario en su ubicación activa, debe **retirarse mediante traslado al baúl `vault/`**, conservando su contenido para revisión humana posterior.

La eliminación definitiva de elementos dentro de `vault/` queda reservada exclusivamente al propietario del repositorio y se realiza manualmente fuera de los flujos automáticos.

## Distinción entre traslado y borrado

Un traslado al baúl puede aparecer técnicamente en Git como una eliminación en la ruta original y una creación en `vault/`. Eso **no se considera borrado destructivo** únicamente si se cumplen todas estas condiciones antes de retirar la ruta original:

1. el contenido ya existe íntegro en la ruta de destino dentro de `vault/`;
2. se verificó que origen y destino corresponden al mismo elemento;
3. el traslado está registrado en `vault/INDEX.md`;
4. la operación forma parte del mismo cambio o transacción lógica de traslado.

Si esas condiciones no pueden garantizarse, el agente debe conservar la ruta original y dejar la tarea bloqueada para revisión humana.

## Acciones prohibidas para agentes y automatizaciones

Salvo una instrucción humana explícita que cambie esta política, no se permite:

- `rm`, `rm -r`, `rm -rf` o equivalentes como mecanismo de descarte de contenido del proyecto;
- `git rm` como mecanismo de descarte definitivo;
- llamadas API de borrado aisladas o sin una copia íntegra y verificada en `vault/`;
- scripts de limpieza que eliminen contenido versionado;
- purgas automáticas dentro de `vault/`;
- reemplazar un archivo por una copia vacía como forma indirecta de borrado.

## Procedimiento correcto para retirar contenido

1. Verificar la ruta, tipo y función del elemento antes de moverlo.
2. Crear una ubicación bajo `vault/YYYY-MM-DD/` que preserve la ruta original.
3. Copiar o mover el elemento al baúl y verificar que el contenido de destino sea íntegro.
4. Registrar el traslado en `vault/INDEX.md` con:
   - fecha;
   - ruta original;
   - ruta en el baúl;
   - motivo;
   - referencia al commit o tarea cuando exista;
   - estado `Pendiente de revisión manual`.
5. Solo después de verificar destino y registro puede retirarse la ruta activa como parte del mismo traslado. Cuando se trabaja localmente, `git mv` es la operación preferida.
6. Actualizar `docs/DOCUMENTATION_INDEX.md` si el elemento retirado era documentación registrada.
7. No borrar después el contenido del baúl. La purga es manual y exclusiva del propietario.

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
→ verificar integridad
→ registrar el movimiento
→ dejar pendiente de revisión manual
```

Nunca significa destrucción automática del contenido.
