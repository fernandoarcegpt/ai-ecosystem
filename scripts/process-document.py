#!/usr/bin/env python3
"""
Script: Process Document for Notex
Simplifies generating OKF-based documentation and storing it in procedures.
Uses existing files if they exist, or creates placeholder content.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Directorios (ACTUALIZADO: procedures ahora en ai-ecosystem/)
PROCEDURES_DIR = Path("/home/fernando/ai-ecosystem/procedures")
DOWNLOADS_DIR = Path.home() / "ai-ecosystem" / ".hermes" / "library" / "downloads"
LOGS_DIR = Path.home() / "ai-ecosystem" / ".hermes" / "logs"

# Colores para output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

def ensure_directories():
    """Crear directorios necesarios"""
    PROCEDURES_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

def create_placeholder_content(title: str, format_type: str):
    """Crear contenido de ejemplo basado en tipo de archivo"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""# {title}

## Descripción

Este es un manual generado automáticamente en formato OKF.  
- **Título**: {title}  
- **Formato**: {format_type}  
- **Fecha de creación**: {timestamp}

## Información del Documento

- **Origen**: Generado por el sistema de documentación OKF con Notex+Python
- **Almacenado en**: {PROCEDURES_DIR}
- **Metadatos asociados**: OKF Procedure Document

## Uso Recomendado

Este documento está pensado para ser consultado por sistemas como Hermes y Claude Code cuando se requiere información estructurada y verificada.

*Note: Este es un archivo de ejemplo. En producción, se rellenaría con contenido real del proceso documentado.*
"""

    return content

def ensure_file_with_content(path: Path, content: str):
    """Crear o sobrescribir un archivo con el contenido dado"""
    path.write_text(content, encoding='utf-8')
    return path

def generate_metadata(title: str, format_type: str, status: str, notebook_name: str):
    """Generar archivo de metadatos OKF-compatible"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    meta = {
        "title": title,
        "format": format_type,
        "timestamp": timestamp,
        "notebook": notebook_name,
        "status": status,
        "source": "documentation-generator",
        "okf_schema": "procedure_document"
    }
    
    meta_file = DOWNLOADS_DIR / f"{timestamp}_{title.replace(' ', '_')}.meta.json"
    meta_file.write_text(json.dumps(meta, indent=2), encoding='utf-8')
    return meta_file

def copy_to_procedures(title: str, content: str):
    """Copiar contenido a procedures de Desktop con encabezado OKF"""
    safe_name = title.replace(' ', '_').replace('/', '_')
    dest = PROCEDURES_DIR / f"{safe_name}.md"
    
    # Asegurar encabezado OKF
    header = f"""---
# OKF Procedure Document
title: "{title}"
generated_at: "{datetime.now().isoformat()}"
schema: procedure_document
status: active
---

# {title}

{content}
"""
    
    safe_content = header + "\n" + content
    safe_content_path = Path(dest)
    safe_content_path.write_text(header + "\n" + content, encoding='utf-8')
    return dest

def main():
    if len(sys.argv) < 2:
        print(f"{RED}Uso: {sys.argv[0]} <título> [formato] [ruta_entrada]{NC}")
        print(f"Ejemplo: {sys.argv[0]} 'Guía de Prueba' txt")
        sys.exit(1)
    
    title = sys.argv[1]
    format_type = sys.argv[2] if len(sys.argv) > 2 else "txt"
    input_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    ensure_directories()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    notebook_name = f"{timestamp}_{title.replace(' ', '_')}"
    
    print(f"{GREEN}=== Generador de Documentación OKF ==={NC}")
    print(f"Título: {title}")
    print(f"Formato: {format_type}")
    print(f"Timestamp: {timestamp}")
    
    # 1. Obtener o crear contenido
    if input_path and Path(input_path).exists():
        # Si el archivo existe, usamos su contenido
        with open(input_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        print(f"{GREEN}✓ Usando contenido existente: {input_path}{NC}")
        content = existing_content
    else:
        # Crear contenido base
        print(f"{YELLOW}⚠ No se encontró archivo de entrada, generando contenido de ejemplo{NC}")
        content = create_placeholder_content(title, format_type)
    
    # 2. Crear archivo temporal para OKF (para copy_to_procedures)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    placeholder_txt = Path(DOWNLOADS_DIR) / f"{timestamp}_{title.replace(' ', '_')}.txt"
    placeholder_txt.write_text(content, encoding='utf-8')
    
    # 3. Copiar a procedures de Desktop con encabezado OKF
    dest_file = ensure_file_with_content(PROCEDURES_DIR / f"{title.replace(' ', '_')}.md", 
                                        f"# {title}\n\n{content}")
    print(f"{GREEN}✓ Documento guardado en procedures: {dest_file}{NC}")
    
    # 4. Guardar metadatos OKF
    meta_file = ensure_file_with_content(DOWNLOADS_DIR / f"{timestamp}_{title.replace(' ', '_')}.meta.json",
                                         json.dumps({
                                             "title": title,
                                             "format": format_type,
                                             "timestamp": timestamp,
                                             "notebook": notebook_name,
                                             "status": "processed",
                                             "source": "documentation-generator",
                                             "okg_schema": "procedure_document"
                                         }, indent=2))
    print(f"{GREEN}✓ Metadatos OKG generados: {meta_file}{NC}")
    
    # 5. Confirmar ubicación final
    print(f"\n{GREEN}=== Documento OKF procesado exitosamente ==={NC}")
    print(f"Archivo en procedures: {dest_file}")
    print(f"Metadatos asociados: {meta_file}")
    print(f"Contenido generado: {len(content)} caracteres")

if __name__ == "__main__":
    main()