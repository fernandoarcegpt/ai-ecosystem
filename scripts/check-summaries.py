#!/usr/bin/env python3
"""
Script: check-summaries.py
Verifica primero en los documentos de resumen antes de realizar búsquedas externas.
Actualizado para nueva ubicación de procedures.
"""

import json
import sys
from pathlib import Path

# Directorios actualizados
PROCEDURES_DIR = Path("/home/fernando/ai-ecosystem/procedures")
LIBRARY_DIR = Path.home() / "ai-ecosystem" / ".hermes" / "library"

def search_summaries(query: str) -> dict:
    """Busca en todos los documentos de summaries disponibles."""
    results = {
        "found": False,
        "source": None,
        "content": None,
        "file": None
    }
    
    # 1. Buscar en procedures (nueva ubicación)
    if PROCEDURES_DIR.exists():
        for md_file in PROCEDURES_DIR.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                if query.lower() in content.lower():
                    results["found"] = True
                    results["source"] = "procedures"
                    results["file"] = str(md_file)
                    # Extraer sección relevante (primeros 500 caracteres)
                    lines = content.split('\n')
                    relevant = []
                    for line in lines:
                        if query.lower() in line.lower():
                            relevant.append(line)
                        if len(relevant) >= 3:
                            break
                    results["content"] = '\n'.join(relevant)[:500]
                    return results
            except Exception:
                continue
    
    # 2. Buscar en library (json)
    for json_file in LIBRARY_DIR.glob("*.json"):
        try:
            content = json.loads(json_file.read_text(encoding='utf-8'))
            content_str = json.dumps(content).lower()
            if query.lower() in content_str:
                results["found"] = True
                results["source"] = "library"
                results["file"] = str(json_file)
                results["content"] = json.dumps(content, indent=2)[:500]
                return results
        except Exception:
            continue
    
    # 3. Buscar en books_catalog.md
    catalog_file = LIBRARY_DIR / "books_catalog.md"
    if catalog_file.exists():
        try:
            content = catalog_file.read_text(encoding='utf-8')
            if query.lower() in content.lower():
                results["found"] = True
                results["source"] = "books_catalog"
                results["file"] = str(catalog_file)
                results["content"] = content[:500]
                return results
        except Exception:
            pass
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Uso: check-summaries.sh <query>")
        print("Ejemplo: check-summaries.sh 'portafolio optimización'")
        sys.exit(1)
    
    query = sys.argv[1]
    
    print(f"🔍 Buscando en summaries: {query}")
    print(f"📁 Procedures: {PROCEDURES_DIR}")
    print(f"📚 Library: {LIBRARY_DIR}")
    print()
    
    results = search_summaries(query)
    
    if results["found"]:
        print(f"✅ ENCONTRADO en: {results['source']}")
        print(f"📄 Archivo: {results['file']}")
        print(f"📝 Contenido: {results['content']}")
        print()
        print("RESULTADO: RESPUESTA ENCONTRADA EN SUMMARIES")
        sys.exit(0)
    else:
        print("❌ NO ENCONTRADO en summaries")
        print("RESULTADO: DELEGAR A SEARCH EXTERNO")
        sys.exit(1)

if __name__ == "__main__":
    main()