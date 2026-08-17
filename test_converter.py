#!/usr/bin/env python3
"""
Test script para probar el conversor EPUB/PDF a Markdown
"""
import sys
import os
sys.path.insert(0, '/home/fernando/ai-ecosystem/.claude/skills/converter-markdown')

try:
    from converter_a_texto import convertir_a_markdown
    print("Módulo importado correctamente")

    # Probar con un archivo EPUB
    resultado = convertir_a_markdown(
        "/home/fernando/ai-ecosystem/downloads/2000.epub.images",
        "/home/fernando/ai-ecosystem/wiki_memoria/90_Libreria_Libros",
        True,
        True
    )

    print("Resultado de la conversión:")
    import json
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()