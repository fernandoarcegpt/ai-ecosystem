#!/usr/bin/env python3
"""
Script para revertir el parche knowledge_broker_db_path
Cambia: /home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu
A:      /home/fernando/ai-ecosystem/storage/kuzu/knowledge_base
"""

import os

def revert_db_path():
    file_path = "src/ingest.py"
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Revertir el cambio
    content = content.replace(
        'db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"',
        'db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base"'
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Revertido: {file_path}")
    print("Advertencia: La base de datos KuzuDB dejara de funcionar correctamente")

if __name__ == "__main__":
    revert_db_path()