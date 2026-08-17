#!/usr/bin/env python3
"""Script para verificar el parche knowledge_broker_db_path"""

import os
import sys

def verify_db_path():
    file_path = "src/ingest.py"
    
    if not os.path.exists(file_path):
        print(f"FAIL: Archivo no encontrado: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    checks = {
        "Ruta con extension .kuzu": 'knowledge_base.kuzu' in content,
        "Directorio kuzu creado": 'os.makedirs(os.path.dirname(db_path), exist_ok=True)' in content,
        "Limpieza de archivos previos": 'knowledge_base' in content and 'os.remove' in content,
        "Patron exclusion .kuzu": '*.kuzu' in content,
        "Patron exclusion .db": '*.db' in content,
    }
    
    print("=== Verificacion Parche knowledge_broker_db_path ===\n")
    all_passed = True
    for name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if not passed:
            all_passed = False
    
    # Verificar archivo de base de datos
    db_path = "/home/fernando/ai-ecosystem/storage/kuzu/knowledge_base.kuzu"
    db_exists = os.path.exists(db_path)
    print(f"\n{'PASS' if db_exists else 'FAIL'} Base de datos existe: {db_path}")
    if not db_exists:
        all_passed = False
    
    print(f"\nResultado: {'TODOS los checks pasaron' if all_passed else 'Algunos checks fallaron'}")
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if verify_db_path() else 1)