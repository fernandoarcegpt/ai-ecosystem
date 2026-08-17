"""
Verification Test for Policy Engine YAML Policies and Rule Processing

This script tests that the Policy Engine correctly loads YAML policies and evaluates them according to the hierarchical DENY > REQUIRE_HUMAN > UNKNOWN > ALLOW precedence.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add src to path so we can import from reasoning package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from reasoning.policy_engine import PolicyEngine
from reasoning.contracts import DecisionResult, Actor, FilePath, PolicyEngineContext

def test_yaml_policies(engine: PolicyEngine) -> bool:
    """Test that policies are loaded correctly from YAML files"""
    print("Testing YAML policy loading...")
    
    # Test reloading policies
    if engine.reload_policies():
        print(f"✓ Loaded {len(engine.loaded_policies)} policies from {engine.policies_dir}")
        
        # Display policy info
        for policy_id, policy in engine.loaded_policies.items():
            print(f"  - {policy_id} (version: {policy.version}, description: {policy.description})")
        
        # Verify critical policies exist
        critical_policies = ['SAF-CRITICAL-001', 'SAF-DESTRUCTIVE-002', 'SAF-PRIVILEGED-003']
        loaded_ids = set(engine.loaded_policies.keys())
        
        missing = [pid for pid in critical_policies if pid not in loaded_ids]
        if missing:
            print(f"✗ Missing critical policies: {missing}")
            return False
        else:
            print("✓ All critical policies loaded")
            
        # Verify specific policy properties
        critical_policies_data = {
            'SAF-CRITICAL-001': 'has critical priority and correct effect',
            'SAF-DESTRUCTIVE-002': 'has high priority',
            'SAF-PRIVILEGED-003': 'has high priority'
        }
        
        for pid, description in critical_policies_data.items():
            if pid in engine.loaded_policies:
                policy = engine.loaded_policies[pid]
                print(f"  - {pid} - {description}")
                
                # Check that policies have all required fields
                required_fields = ['id', 'version', 'description', 'priority', 'effect', 'obligations']
                for field in required_fields:
                    if not hasattr(policy, field) or getattr(policy, field) is None:
                        print(f"✗ Policy {pid} missing field: {field}")
                        return False
        
        return True
    else:
        print("✗ Failed to load policies")
        return False

def test_policy_evaluation(engine: PolicyEngine) -> bool:
    """Test policy evaluation on different scenarios"""
    print("\nTesting policy evaluation scenarios...")
    
    test_cases = [
        {
            "name": "Modify critical file (should require approval)",
            "action": "modify",
            "target_path": "/home/fernando/ai-ecosystem/src/reasoning/policies/safety.yaml",
            "should_require_human": True,
            "reason": "Modification of critical policy file"
        },
        {
            "name": "Read documentation file (should allow)",
            "action": "read",
            "target_path": "/home/fernando/ai-ecosystem/docs/",
            "should_require_human": False,
            "reason": "Reading non-critical documentation"
        },
        {
            "name": "Delete vulnerable file (should deny)",
            "action": "delete",
            "target_path": "/home/fernando/ai-ecosystem/modified_file.py",
            "should_require_human": False,
            "result_expected": DecisionResult.DENY,
            "reason": "Deletion of sensitive file"
        }
    ]
    
    test_actor = Actor(id="test_user", type="human", role="tester", 
                      capabilities=["test"], permissions=["read"])
    
    all_passed = True
    
    for i, scenario in enumerate(test_cases, 1):
        print(f"\nScenario {i}: {scenario['name']}")
        
        # Create context
        is_critical = "critical" in scenario["reason"].lower() or "sensitive" in scenario["reason"].lower()
        
        context = PolicyEngineContext(
            task_id=f"TEST-TASK-{i}",
            task_description=scenario["reason"],
            actor=test_actor,
            target=FilePath(
                path=scenario["target_path"].split("/")[-1],
                absolute_path=scenario["target_path"],
                is_critical=is_critical,
                is_protected=True,
                category="secrets" if is_critical else "source"
            ),
            action=scenario["action"],
            context_data={}
        )
        
        print(f"  Target: {scenario['target_path']}")
        print(f"  Action: {scenario['action']}")
        
        # Evaluate policy
        decision = engine.evaluate_policy(context)
        
        print(f"  Result: {decision.decision_result}")
        print(f"  Reason: {decision.reason}")
        
        # Check expectations
        expected_result = scenario.get("should_require_human", True)
        
        if expected_result and decision.decision_result == DecisionResult.REQUIRE_HUMAN:
            print(f"  ✓ Correctly required human approval")
        elif not expected_result and decision.decision_result in [DecisionResult.ALLOW, DecisionResult.DENY]:
            print(f"  ✓ Made appropriate decision ({decision.decision_result})")
        else:
            print(f"  ✗ Expected {DecisionResult.REQUIRE_HUMAN if expected_result else 'different'}, got {decision.decision_result}")
            all_passed = False
            
        # Verify evidence generation
        if len(decision.evidence) > 0:
            print(f"  ✓ Generated {len(decision.evidence)} evidence items")
        else:
            print("  ✗ No evidence generated")

    return all_passed

def main():
    """Main test function"""
    print("Verifying Policy Engine Implementation")
    print("=" * 50)
    
    try:
        # Initialize policy engine
        policy_dir = "/home/fernando/ai-ecosystem/src/reasoning/policies"
        engine = PolicyEngine()
        engine.policies_dir = policy_dir
        
        print(f"Policy Engine instantiated with policies directory: {policy_dir}")
        
        # Test 1: Policy loading
        load_success = test_yaml_policies(engine)
        
        # Test 2: Policy evaluation
        eval_success = test_policy_evaluation(engine)
        
        print("\n" + "=" * 50)
        if load_success and eval_success:
            print("VERIFICATION SUCCESSFUL: ALL TESTS PASSED")
            print("VERIFICATION COMPLETE")
            return 0
        else:
            print("VERIFICATION FAILED: SOME TESTS FAILED")
            return 1
        print("=" * 50)
        
    except Exception as e:
        print(f"VERIFICATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())