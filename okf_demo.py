#!/usr/bin/env python3
"""
OKF Demo — Flujo completo de Open Knowledge Format wiki.
Demuestra crear, validar, escribir y transferir una nota de proyecto.
"""

from pathlib import Path
from process_wiki import (
    list_wiki_files,
    read_wiki_file,
    write_wiki_file,
    write_to_wiki_vault,
)
from knowledge_broker import validate

# Ruta del proyecto dentro de la wiki
PROJECTS_DIR = Path(__file__).parent / "wiki_memoria" / "proyectos"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("=== OKF DEMO — Flujo de Wiki Memory ===\n")

    # 1. Crear una nota de proyecto válida (siguiendo formato_reportes.md)
    note_content = """# Proyecto Um Cobriza

## Estado actual
- ✅ Implementación del módulo de validación
- 🔄 Integración con Knowledge Broker pendiente
- ⏳ Pruebas unitarias en progreso

## Próximos pasos
1. Finalizar escritura en vault de Obsidian
2. Añadir tests de carga
3. Documentar API de intercambio

## Responsable
- Fernándo Arce (fernandoarcegpt)

## Última actualización
2026-07-08
"""

    filename = "um_cobriza.md"
    project_path = PROJECTS_DIR / filename

    # 2. Validar el contenido
    print("[1] Validando contenido...")
    validation = validate(note_content)
    if not validation.get("aprobado"):
        print(f"   ❌ Rechazado: {validation.get('detalle')}")
        return
    print("   ✅ Contenido aprobado")

    # 3. Escribir localmente en wiki_memoria/proyectos/
    print(f"[2] Escribiendo nota en {project_path}...")
    write_wiki_file(str(project_path.relative_to(Path(__file__).parent / "wiki_memoria")), note_content)
    print("   ✅ Nota escrita localmente")

    # 4. Intentar transferir al Knowledge Broker
    print("[3] Intentando transferir al Knowledge Broker...")
    try:
        success = write_to_wiki_vault(filename, note_content)
        if success:
            print("   ✅ Transferencia exitosa al broker")
            # Eliminar del staging si existiera (en este demo no estaba en staging)
        else:
            print("   ⚠ Transferencia falló (revisar configuración del broker)")
    except Exception as e:
        print(f"   ❌ Error durante transferencia: {e}")

    # Explicación breve del pipeline
    print("\n=== Explicación del pipeline ===")
    print("1. Almacenamiento físico: las notas viven como archivos .md en wiki_memoria/")
    print("2. Ejecución: process_wiki.py provee las herramientas list/read/write y el flujo")
    print("3. Razonamiento: el agente (o el usuario) decide qué crear y valida contra normativa")
    print("4. El Knowledge Broker actúa como puente hacia Obsidian Vault (si está configurado)")
    print("5. Los metadatos .index.json y .changelog.log registran cada operación")

    # Mostrar estado actual de proyectos
    print("\n=== Estado del directorio de proyectos ===")
    for f in PROJECTS_DIR.glob("*.md"):
        print(f" - {f.name} ({f.stat().st_size} bytes)")

if __name__ == "__main__":
    main()