"""
Test del Policy Engine - Verificación funcional directa
"""

import os
import sys

# Añadir src al path
sys.path.insert(0, "/home/fernando/ai-ecosystem/src")

from reasoning.policy_engine import PolicyEngine

def test_policy_engine():
    """Test de carga y evaluación de políticas"""
    print("=" * 50)
    print("Testing Policy Engine")
    print("=" * 50)
    
    # Inicializar PolicyEngine
    policy_dir = "/home/fernando/ai-ecosystem/src/reasoning/policies"
    engineer = PolicyEngine(policy_dir)
    
    print(f"✓ PolicyEngine creado correctamente")
    print(f"  Directorio de políticas: {policy_dir}")
    print(f"  Políticas cargadas: {len(engineer.loaded_policies)}")
    
    # Listar políticas
    for pid, policy in engineer.loaded_policies.items():
        print(f"    - {pid}: {policy.effect} (priority: {policy.priority})")
    
    # Test de recarga
    if engineer.reload_policies():
        print(f"\n✓ Políticas recargadas exitosamente")
        print(f"  Políticas activas tras recarga: {len(engineer.loaded_policies)}")
    else:
        print("✗ Error al recargar políticas")
        return False
    
    print("\n✓ TEST PASSED")
    return True

if __name__ == "__main__":
    try:
        success = test_policy_engine()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)