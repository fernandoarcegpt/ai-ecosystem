# OKF Wiki Memory System - Documentación de Referencia

> Implementación del Open Knowledge Format (OKF) para gestión de memoria persistente en sistemas de IA autónoma.

## 🎯 Resumen rápido

El OKF Wiki es un sistema de **memoria basada en archivos planos** que sirve como capa de almacenamiento físico para agentes de IA autónoma (Claude Code, Ruflo, etc.). Almacena notas como archivos `.md` en `wiki_memoria/`, provee un pipeline de procesamiento robusto, y sincroniza con Obsidian Vault mediante el Knowledge Broker.

## 📋 Índice

1. [¿Qué es OKF?](#que-es-okf)
2. [Estructura del sistema de archivos](#estructura-del-sistema-de-archivos)
3. [Herramientas principales](#herramientas-principales)
4. [Pipeline de procesamiento](#pipeline-de-procesamiento)
5. [Seguridad](#seguridad)
6. [Integración con Knowledge Broker](#integración-con-knowledge-broker)
7. [Ejemplo de uso](#ejemplo-de-uso)

---

## 🤔 ¿Qué es OKF?

**Open Knowledge Format (OKF)** es una alternativa ligera y portátil a los almacenamiento tradicionales con Graph DBs costosos. Específicamente diseñado para:

- **Agentes de IA autónoma** que necesitan memoria persistente fuera de la sesión actual
- **Flujos de trabajo en tiempo real** con capacidad de recuperación simple
- **Multi-agente systems** donde cada agente almacena conocimiento en notas Markdown planas
- **Transferencia sin fricciones** entre aplicaciones y servicios mediante intercambio de archivos

> Esta implementación sigue la arquitectura de tres capas descrita en CLAUDE.md:
> **Capa 1** (Almacenamiento) → **Capa 2** (Ejecución) → **Capa 3** (Razonamiento)

## 📁 Estructura del sistema de archivos

```
wiki_memoria/                    # Directorio raíz de OKF
├── .index.json                  # Índice para fast lookup
├── .changelog.log               # Historial de modificaciones
├── normativa/                    # Reglas de formato y taxonomía
│   └── formato_reportes.md
├── proyectos/                    # Estado de proyectos
└── staging/                      # Notas pendientes de procesamiento
```

### Componentes clave

| Archivo | Propósito |
|---------|-----------|
| `.index.json` | Registro automático de todos los archivos con timestamps |
| `.changelog.log` | Historial cronológico de operaciones WRITE/TRANSFER |
| `normativa/` | Directrices de estilo y formatos obligatorios |
| `proyectos/` | Notas de estado por proyecto |
| `staging/` | Área de trabajo temporal para nuevas notas |

## 🔧 Herramientas principales

### `list_wiki_files() -> List[str]`

Enumera los archivos pendientes en `staging/`:

```python
from process_wiki import list_wiki_files

archivos = list_wiki_files()
print(archivos)  # ['nota_1.md', 'nota_2.md']
```

### `read_wiki_file(path: str) -> str`

Lee contenido de una nota específica:

```python
from process_wiki import read_wiki_file

content = read_wiki_file("proyectos/um_cobriza.md")
print(content)  # Contenido Markdown
```

### `write_wiki_file(path: str, content: str) -> None`

Crea/actualiza una nota en el árbol de wiki:

```python
from process_wiki import write_wiki_file

write_wiki_file("proyectos/nuevo.md", "# Nuevo Proyecto\n\nDescripción...")
```

### `write_to_wiki_vault(filename: str, content: str) -> bool`

Transfiere una nota al Obsidian Vault:

```python
from process_wiki import write_to_wiki_vault

success = write_to_wiki_vault("nota.md", "# Nota\n\n...")
if success:
    print("Transferido al vault")
```

## 🔄 Pipeline de procesamiento

```
┌─────────────────────────────────────────────────────────────────┐
│                    OKF PIPELINE                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                │
│  staging/*.md                                                 │
│      │                                                         │
│      ▼                                                         │
│  [process_wiki.py]                                            │
│      │                                                         │
│      ├─→ validate() → RECHAZADO → Descartar                    │
│      │                                                         │
│      └─→ validate() → APROBADO →                               │
│              │                                                 │
│              ▼                                                 │
│        write_wiki_file() → wiki_memoria/                        │
│              │                                                 │
│              ▼                                                 │
│        write_to_wiki_vault() → Knowledge Broker                 │
│              │                                                 │
│              ▼                                                 │
│        Obsidian Vault                                         │
│                │                                               │
│                ▼                                               │
│        [SUCCESS] → eliminar staging/*.md                      │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

## 🛡️ Seguridad

### Prevención de Path Traversal

Todas las funciones de escritura/validación usan `sanitizePath()` para prevenir accesos fuera del árbol de wiki:

```python
# Intentar acceder fuera del árbol
write_wiki_file("../../../etc/passwd", "malicious")
# → Exception: "Ruta no permitida: intruso con ../"
```

### Buenas prácticas

- Nunca almacenar credenciales sensibles en notas
- Validar contenido antes de escribir
- Usar `staging/` para notas en progreso
- Elimina notas del staging tras transferencia exitosa

## 🔄 Integración con Knowledge Broker

El Knowledge Broker (`knowledge_broker.py`) es el puente hacia Obsidian:

| Función | USOS |
|---------|------|
| `validate()` | Verifica contenido no vacío |
| `write_to_vault()` | Escribe vía REST API a Obsidian |
| `process_staging()` | Pipeline completo |

Variables de configuración en `.obsidian-broker/.env`:
- `OBSIDIAN_PORT` (default: 27124)
- `OBSIDIAN_API_KEY` (token Bearer)

## 📝 Ejemplo de uso

### Caso 1: Crear una nueva nota

```bash
# 1. Crear nota en staging
echo "# Mi Proyecto\n\nDescripción del proyecto..." > wiki_memoria/staging/mi_proyecto.md

# 2. Ejecutar pipeline
python3 process_wiki.py

# 3. Verificar en vault
cat vault/mi_proyecto.md
```

### Caso 2: Consultar notas existentes

```python
from process_wiki import read_wiki_file

# Leer nota específica
nota = read_wiki_file("proyectos/existing.md")
print(nota)
```

### Caso 3: Lista de notas pendientes

```python
from process_wiki import list_wiki_files

pendientes = list_wiki_files()
for f in pendientes:
    print(f"Pendiente: {f}")
```

## 📊 Metadatos automáticos

### .index.json (actualizado automáticamente)

```json
{
  "proyectos/um_cobriza.md": {
    "action": "write",
    "ts": "2026-07-08T19:00:00"
  }
}
```

### .changelog.log (actualizado automáticamente)

```
[2026-07-08T19:00:00] WRITE proyectos/um_cobriza.md
[2026-07-08T19:01:00] TRANSFER_OK proyectos/um_cobriza.md
```

---

**Versión:** 1.0  
**Última actualización:** 2026-07-08