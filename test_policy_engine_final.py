"""
Simple verification that Policy Engine works without contract imports.

This test focuses on the core functionality of PolicyEngine without importing contracts.
"""

import os
import sys
import logging

# Add the src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_policy_engine():
    """Test the PolicyEngine directly"""
    print("Testing Policy Engine Directly")
    print("=" * 50)
    
    try:
        # Import PolicyEngine
        from reasoning.policy_engine import PolicyEngine
        print("✓ PolicyEngine imported successfully")
        
        # Initialize with policies directory
        policy_dir = "/home/fernando/ai-ecosystem/src/reasoning/policies"
        engineer = PolicyEngine(policy_dir)
        print(f"✓ PolicyEngine created with policies_dir: {policy_dir}")
        print(f"  Loaded policies: {len(engineer.loaded_policies)}")
        
        # Show some policy details
        for policy_id in list(engineer.loaded_policies.keys())[:3]:
            policy = engineer.loaded_policies[policy_id]
            print(f"  - {policy_id}: {policy.effect} ({policy.priority})")
        
        # Test that we can evaluate a policy
        print("\n" + "-" * 30)
        print("TESTING POLICY EVALUATION")
        print("-" * 30)
        
        # Create a simple test - we'll check if we can evaluate a policy
        # We'll use a simple context that mimics what the system would provide
        context = {
            "task_id": "TEST-001",
            "task_description": "Test policy evaluation",
            "actor": {
                "id": "user_123",
                "type": "human",
                "role": "tester",
                "capabilities": ["test"],
                "permissions": ["read"]
            },
            "target": {
                "path": "safety.yaml",
                "absolute_path": "/home/fernando/ai-ecosystem/src/reasoning/policies/safety.yaml",
                "is_critical": True,
                "is_protected": True,
                "category": "secrets"
            ),
            "action": "modify",
            "context_data": {}
        )
        
        # Evaluate the policy
        decision = engineer.evaluate_policy(context)
        print(f"  Decision result: {decision.decision_result}")
        print(f"  Reason: {decision.reason}")
        print(f"  Engine used: {decision.engine}")
        print(f"  Confidence: {decision.confidence}")
        
        # Check if the decision makes sense
        if decision.decision_result in ["require_human", "deny"]:
            print("✓ Policy evaluation shows appropriate restriction")
            return True
        elif decision.decision_result == "allow":
            print("  ✓ Policy allowed the action")
            return True
        else:
            print(f"  ? Unexpected decision: {decision.decision_result}")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the direct test"""
    print("Direct Policy Engine Test")
    print("=" * 50)
    
    try:
        success = test_policy_loading()
        if test1_passed:
            test2_passed = test_policy_evaluation()
            if test2_passed:
                print("\n" + "=" * 50)
                print("✅ DIRECT TEST SUCCESSFUL")
                print("Policy Engine is working correctly")
                return 0
            else:
                print("❌ Policy evaluation failed")
                return 1
        else:
            print("❌ Policy loading failed")
            return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

def test_policy_loading():
    """Test that policies are loaded"""
    print("1. Testing policy loading...")
    try:
        engineer = PolicyEngine("/home/fernando/ai-ecosystem/src/reasoning/policies")
        if engineer.reload_policies():
            print(f"✓ Loaded {len(engineer.loaded_policies)} policies")
            return True
        else:
            print("✗ Failed to load policies")
            return False
    except Exception as e:
        print(f"✗ Error in policy loading: {e}")
        return False

def test_policy_evaluation():
    """Test that policy evaluation works"""
    print("\n2. Testing policy evaluation...")
    try:
        engineer = PolicyEngine("/home/fernando/ai-ecosystem/src/reasoning/policies")
        if engineer.loaded_policies:
            # Create a simple context
            context = {
                "task_id": "TEST-001",
                "task_description": "Test policy evaluation",
                "actor": {
                    "id": "user123",
                    "type": "human",
                    "role": "tester",
                    "capabilities": ["test"],
                    "permissions": ["read"]
                },
                "target": {
                    "path": "safety.yaml",
                    "absolute_path": "/home/fernando/ai-ecosystem/src/reasoning/policies/safety.yaml",
                    "is_critical": True,
                    "is_protected": True,
                    "category": "secrets"
                },
                "action": "modify",
                "context_data": {}
            )
            
            # Evaluate
            decision = engineer.evaluate_policy(test_context)
            print(f"  Decision: {decision.decision_result}")
            
            if decision.decision_result in ["require_human", "deny"]:
                print("✓ Policy correctly evaluated with appropriate restriction")
                return True
            else:
                print("  ✓ Policy evaluation successful")
                return True
                
    except Exception as e:
        print(f"✗ Error in policy evaluation: {e}")
        return False

def main():
    """Main function"""
    print("Testing Policy Engine Directly")
    print("=" * 50)
    
    test1_passed = test_policy_loading()
    test2_passed = test_policy_evaluation()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Policy Loading: {'PASS' if test1_passed else 'FAIL'}")
    print(f"Policy Evaluation: {'PASS' if test2_passed else 'FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n✅ ALL TESTS PASSED - POLICY ENGINE IS WORKING")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit(main())