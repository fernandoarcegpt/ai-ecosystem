# Knowledge Broker

> **Estado: histórico y reemplazado.** Describe un broker de Obsidian distinto
> del módulo vigente `sharememory/hermes_memory/knowledge_broker.py`.

> Gateway hacia Obsidian Vault mediante Local REST API

## 🎯 Función

El `knowledge_broker.py` actúa como **intermediario de escritura** único entre el ecosistema y el vault de Obsidian. Su función es:

1. Leer notas desde `staging/`
2. Validar su contenido
3. Transferirlas al vault de Obsidian vía REST API
4. Limpiar el staging tras éxito

## 🔧 API

### `validate(content: str) -> dict`
Valida una nota antes de aprobarla.

```python
from knowledge_broker import validate

result = validate("# Nota válida\n\nContenido...")
# {"aprobado": True, "tipo": "ruflo_report", "detalle": "ok"}

result = validate("   ")
# {"aprobado": False, "tipo": "vacio", "detalle": "contenido vacío"}
```

### `write_to_vault(filename: str, content: str) -> bool`
Escribe una nota en el vault mediante Local REST API.

```python
from knowledge_broker import write_to_vault

success = write_to_vault("mi_nota.md", "# Mi Nota\n\n...")
# True si HTTP 200/204, False en error
```

### `process_staging()`
Procesa todos los archivos `.md` pendientes en `staging/`:

```bash
python3 knowledge_broker.py
```

## ⚙️ Configuración

Variables en `.obsidian-broker/.env`:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `OBSIDIAN_PORT` | `27124` | Puerto del Local REST API |
| `OBSIDIAN_API_KEY` | — | Token de autenticación |

## 🔄 Flujo de trabajo

```
staging/
    ↓ (read + validate)
knowledge_broker.py
    ↓ (PUT /vault/{filename})
Obsidian Vault
```

## 📝 Notas

- La verificación SSL está deshabilitada (`verify=False`)
- El broker no escribe si `validate()` rechaza
- No se admiten paths fuera de `staging/`
