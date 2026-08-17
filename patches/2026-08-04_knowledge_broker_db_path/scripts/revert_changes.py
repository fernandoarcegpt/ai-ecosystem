#!/usr/bin/env python3
"""Script para revertir el parche knowledge_broker_db_path"""

import os
import sys

def revert_db_path():
    file_path = "src/ingest.py"
    
    if not os.path.exists(file_path):
        print(f"ERROR: Archivo no encontrado: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Revertir el cambio
    new_content = content.replace(
        'db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"',
        'db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base"'
    )
    
    if new_content == content:
        print("ERROR: No se encontro el patron a revertir")
        return False
    
    # Backup del archivo original
    backup_path = file_path + ".bak"
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"Backup creado: {backup_path}")
    
    with open(file_path, 'w') as f:
        f.write(new_content)
    
    print("Revertido: src/ingest.py")
    print("ADVERTENCIA: La base de datos KuzuDB dejara de funcionar correctamente")
    print("Para restaurar: git checkout HEAD -- src/ingest.py")
    return True

if __name__ == "__main__":
    success = revert_db_path()
    sys.exit(0 if success else 1)