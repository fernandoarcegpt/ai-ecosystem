"""
Simple test to verify Policy Engine functionality
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test import
try:
    from reasoning.policy_engine import PolicyEngine
    print("✓ PolicyEngine imported successfully")
    
    # Create engine
    policy_dir = "/home/fernando/ai-ecosystem/src/reasoning/policies"
    engine = PolicyEngine(policy_dir)
    print(f"✓ Engine created, loaded {len(engine.loaded_policies)} policies")
    
    # Show policies
    for pid, policy in engine.loaded_policies.items():
        print(f"  - {pid}: {policy.effect} ({policy.priority})")
    
    print("\n✓ BASIC TEST PASSED")
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)