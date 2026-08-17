#!/usr/bin/env python3
"""
Script para verificar todos los parches activos.
Audita cada parche en patches/ y valida que sus scripts de verificación pasen.
"""

import os
import subprocess
import sys
from pathlib import Path

def verify_patch(patch_dir):
    """Verificar un directorio de parche individual."""
    try:
        # Verificar que exista PARTE.md
        parte_md = patch_dir / "PARTE.md"
        if not parte_md.exists():
            return False, "Falta PARTE.md"

        # Verificar si hay script de verificación
        verify_script = patch_dir / "scripts" / "verify_changes.py"
        if verify_script.exists():
            # Ejecutar script de verificación desde el directorio del parche
            # Asegurarse de usar Python absoluto
            result = subprocess.run(
                [sys.executable, str(verify_script)],
                cwd=str(patch_dir),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                return False, f"Verificación fallida: {result.stderr.strip() or result.stdout.strip()}"

        # Verificar que copies/ exista si está documentado
        copies_dir = patch_dir / "copies"
        if copies_dir.exists():
            # Asegurarnos de que contiene al menos un archivo
            if not any(copies_dir.iterdir()):
                return False, "Carpeta copies/ está vacía"

        return True, "OK"
    except subprocess.TimeoutExpired:
        return False, "Timeout al ejecutar verificación"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"

def main():
    # Obtener el directorio del proyecto desde la ubicación del script
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent  # /home/fernando/ai-ecosystem

    patches_dir = project_root / "patches"
    # Solo considerar carpetas que empiecen con fecha (formato YYYY-MM-DD_*)
    patch_dirs = sorted([d for d in patches_dir.iterdir()
                         if d.is_dir() and d.name.startswith("2026-")])

    # Excluir parches redundantes o no funcionales
    excluded_patches = ["2026-08-17_auto_copied_files"]
    patch_dirs = [d for d in patch_dirs if d.name not in excluded_patches]

    print("=== RESUMEN DE VERIFICACIÓN DE PARCHES ===\n")
    all_verified = True
    for patch_dir in patch_dirs:
        success, message = verify_patch(patch_dir)
        status = "✅ VERIFICADO" if success else "❌ FALLÓ"
        print(f"{status} {patch_dir.name}: {message}")
        if not success:
            all_verified = False

    if all_verified:
        print("\n🎉 ¡Todos los parches verificados correctamente!")
        sys.exit(0)
    else:
        print("\n🚨 ¡Algunos parches fallaron la verificación!")
        sys.exit(1)

if __name__ == "__main__":
    main()