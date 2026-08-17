#!/usr/bin/env python3
"""Script para verificar configuración del modo audio-only en notex/main.go"""

import re
import sys

def verify_audio_mode():
    with open("notex/main.go", 'r') as f:
        content = f.read()
    
    checks = {
        "audio-only flag": r'audioOnly := flag\.Bool\("audio-only"',
        "audio validation": r'if \*audioOnly',
        "vosk required": r'ENABLE_VOSK_TRANSCRIBER must be true',
        "markitdown disabled": r'ENABLE_MARKITDOWN should be false'
    }
    
    results = {}
    for name, pattern in checks.items():
        found = bool(re.search(pattern, content))
        results[name] = found
    
    print("=== Verificacion Modo Audio-Only ===\n")
    all_passed = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")
        if not passed:
            all_passed = False
    
    print(f"\nResultado: {'TODOS los checks pasaron' if all_passed else 'Algunos checks fallaron'}")
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if verify_audio_mode() else 1)