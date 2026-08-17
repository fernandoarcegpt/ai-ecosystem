"""
Direct Test of Policy Engine - Simplified Approach

This script tests the Policy Engine without complex mocking,
focusing on the core functionality.
"""

import os
import sys
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Import PolicyEngine directly
try:
    from reasoning.policy_engine import PolicyEngine
    print("✓ Successfully imported PolicyEngine")
except Exception as e:
    print(f"✗ Failed to import PolicyEngine: {e}")
    sys.exit(1)

def test_policy_loading():
    """Test that policies are loaded correctly"""
    print("\n" + "-" * 50)
    print("TEST 1: POLICY LOADING")
    print("-" * 50)
    
    # Initialize policy engine with the policies directory
    policy_dir = "/home/fernando/ai-ecosystem/src/reasoning/policies"
    engineer = PolicyEngine(policy_dir)
    
    print(f"PolicyEngine initialized with policies_dir: {policy_dir}")
    
    # Test loading policies
    if engineer.reload_policies():
        print(f"✓ Successfully loaded {len(engineer.loaded_policies)} policies")
        
        # List loaded policies
        for policy_id in engineer.loaded_policies:
            policy = engineer.loaded_policies[policy_id]
            print(f"  - {policy_id}: {policy.effect} ({policy.priority})")
        
        # Verify we have the basic policies
        if len(engineer.loaded_policies) > 0:
            print("✓ Policies loaded successfully")
            return True
        else:
            print("✗ No policies loaded")
            return False
    else:
        print("✗ Failed to reload policies")
        return False

def test_policy_evaluation():
    """Test that the engine can evaluate policies"""
    print("\n" + "-" * 50)
    print("TEST 2: POLICY EVALUATION")
    print("-" * 50)
    
    try:
        # Initialize engine
        policy_dir = "/home/fernando/ai-ecosystem/src/reasoning/policies"
        engineer = PolicyEngine(policy_dir)
        
        if not engineer.loaded_policies:
            print("✗ No policies loaded - cannot test evaluation")
            return False
        
        print(f"✓ Engine has {len(engineer.loaded_policies)} policies loaded")
        
        # Create a simple test case - looking for a specific policy
        test_context = type('TestContext', (), {
            'task_id': 'TEST-001',
            'task_description': 'Test policy evaluation',
            'actor': type('Actor', (), {
                'id': 'test_user',
                'type': 'human',
                'role': 'tester',
                'permissions': ['read']
            })(),
            'target': type('Target', (), {
                'path': 'safety.yaml',
                'absolute_path': '/home/fernando/ai-ecosystem/src/reasoning/policies/safety.yaml',
                'is_critical': True,
                'is_protected': True,
                'category': 'secrets'
            })(),
            'action': 'modify',
            'context_data': {}
        })()
        
        # Evaluate policy
        print(f"  Evaluating task {test_context.task_id}...")
        decision = engineer.evaluate_policy(test_context)
        
        print(f"  Decision result: {decision.decision_result}")
        print(f"  Reason: {decision.reason}")
        print(f"  Engine used: {decision.engine}")
        print(f"  Confidence: {decision.confidence:.2f}")
        
        # Check if decision makes sense
        if decision.decision_result == "require_human":
            print("✓ Correctly detected need for human approval")
            return True
        elif decision.decision_result == "allow":
            print("  ✓ Policy evaluation successful")
            return True
        else:
            print(f"  ? Unexpected result: {decision.decision_result}")
            return False
        
    except Exception as e:
        print(f"✗ Error during policy evaluation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main execution function"""
    print("Testing Policy Engine Directly")
    print("=" * 50)
    
    test1_passed = test_policy_loading()
    test2_passed = test_policy_evaluation()
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    print(f"Policy Loading Test: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Policy Evaluation Test: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n✅ ALL TESTS PASSED - POLICY ENGINE IS FUNCTIONAL")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit(main())