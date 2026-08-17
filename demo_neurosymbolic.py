#!/usr/bin/env python3
"""
Demonstration of the neurosymbolic reasoning capability in Hermes.

This script shows:
1. A task that activates neurosymbolic reasoning (with dependencies and constraints)
2. A task that does not activate neurosymbolic reasoning (simple question)
3. How to use explicit neurosymbolic reasoning when needed
"""

import sys
import os

# Add the skilled directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'skilled'))

from reasoning.hermes_integration import (
    hermes_auto_detect_and_reason,
    hermes_explicit_symbolic_reasoning
)
from reasoning.neuro_symbolic_engine import (
    analyze_need_for_reasoning,
    get_coordinator,
    integrate_result_with_hermes_response
)

def demonstrate_auto_activation():
    """Demonstrate automatic detection and execution of neurosymbolic reasoning"""
    print("=" * 70)
    print("DEMONSTRATION 1: AUTOMATIC ACTIVATION OF NEUROSYMBOLIC REASONING")
    print("=" * 70)
    
    # Task that should trigger neurosymbolic reasoning
    task_description = "Design a microservices architecture with service discovery, load balancing, and fault tolerance"
    context = {
        "dependencies": ["service_registry", "load_balancer", "circuit_breaker", "config_service"],
        "constraints": [
            "services must be independently deployable",
            "load balancing must be round-robin or least connections",
            "fault tolerance must include retry mechanisms and timeouts",
            "service discovery must support dynamic registration",
            "system must handle 10000+ requests per second"
        ],
        "relations": [
            "service_registry provides discovery for load_balancer",
            "load_balancer routes requests to service instances",
            "circuit_breaker protects services from cascading failures",
            "config_service provides dynamic configuration"
        ]
    }
    
    print(f"Task: {task_description}")
    print(f"Context: {len(context.get('dependencies', []))} dependencies, {len(context.get('constraints', []))} constraints")
    
    # This should automatically detect the need for symbolic reasoning and return evidence
    evidence = hermes_auto_detect_and_reason(task_description, context)
    
    if evidence:
        print("\n\u2705 NEUROSYMBOLIC REASONING WAS AUTOMATICALLY ACTIVATED")
        print("\nEVIDENCE FOR HERMES:")
        print("-" * 50)
        print(evidence)
        print("-" * 50)
    else:
        print("\n\u274c NEUROSYMBOLIC REASONING WAS NOT ACTIVATED (unexpected)")
    
    return evidence is not None

def demonstrate_no_activation():
    """Demonstrate that simple tasks do not activate neurosymbolic reasoning"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 2: NO ACTIVATION FOR SIMPLE TASKS")
    print("=" * 70)
    
    # Simple tasks that should NOT trigger neurosymbolic reasoning
    simple_tasks = [
        "What is the capital of France?",
        "Hello, how are you today?",
        "Can you tell me a joke?",
        "What's the weather like?",
        "Thank you for your help."
    ]
    
    all_correct = True
    for task in simple_tasks:
        evidence = hermes_auto_detect_and_reason(task)
        if evidence is None:
            print(f"\u2705 '{task}' -> Correctly did NOT activate reasoning")
        else:
            print(f"\u274c '{task}' -> Incorrectly activated reasoning")
            all_correct = False
    
    if all_correct:
        print("\n\u2705 ALL SIMPLE TASKS CORRECTLY AVOIDED NEUROSYMBOLIC REASONING")
    else:
        print("\n\u274c SOME SIMPLE TASKS INCORRECTLY TRIGGERED REASONING")
    
    return all_correct

def demonstrate_explicit_reasoning():
    """Demonstrate explicit use of neurosymbolic reasoning when needed"""
    print("\n" + "=" * 70)
    print("DEMONSTRATION 3: EXPLICIT NEUROSYMBOLIC REASONING")
    print("=" * 70)
    
    # Task where we explicitly want to use symbolic reasoning
    task_description = "Verify the consistency of business rules for loan approval"
    context = {
        "description": "Validate loan approval rules for contradictions and completeness",
        "facts": [
            ("applicant_age", 25),
            ("applicant_income", 50000),
            ("loan_amount", 100000),
            ("credit_score", 720)
        ],
        "rules": [
            {"name": "age_rule", "head": "eligible_age(X)", "body": "X >= 18"},
            {"name": "income_rule", "head": "sufficient_income(X,Y)", "body": "X >= Y * 0.3"},
            {"name": "credit_rule", "head": "good_credit(X)", "body": "X >= 650"},
            {"name": "loan_rule", "head": "approve_loan", "body": "eligible_age(age) & sufficient_income(income, loan_amount) & good_credit(credit_score)"}
        ],
        "constraints": [
            "age must be at least 18",
            "income must be at least 30% of loan amount",
            "credit score must be at least 650"
        ]
    }
    
    print(f"Task: {task_description}")
    print("Context includes facts, rules, and constraints for loan approval validation")
    
    # Explicitly request symbolic reasoning
    result = hermes_explicit_symbolic_reasoning(task_description, context, engine_preference="pydatalog")
    
    if result["status"] == "success":
        print("\n\u2705 EXPLICIT NEUROSYMBOLIC REASONING EXECUTED SUCCESSFULLY")
        print(f"Engine used: {result['engine_used']}")
        print(f"Execution time: {result['execution_time']:.3f}s")
        print(f"Conclusion: {result.get('evidence_for_hermes', {}).get('conclusion', 'N/A')}")
        print(f"Confidence: {result.get('evidence_for_hermes', {}).get('confidence', 0):.2f}")
        return True
    else:
        print(f"\n\u274c EXPLICIT REASONING FAILED: {result.get('error', 'Unknown error')}")
        return False

def main():
    """Run all demonstrations"""
    print("NEUROSYMBOLIC REASONING CAPABILITY IN HERMES")
    print("This demonstrates the system's ability to:")
    print("- Automatically detect when symbolic reasoning is beneficial")
    print("- Execute reasoning using appropriate engines (NetworkX, PyDatalog, Z3)")
    print("- Integrate verified results back into Hermes' workflow")
    print("- Avoid unnecessary reasoning for simple tasks\n")
    
    # Run demonstrations
    demo1_success = demonstrate_auto_activation()
    demo2_success = demonstrate_no_activation()
    demo3_success = demonstrate_explicit_reasoning()
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Demonstration 1 (Auto-activation): {'PASS' if demo1_success else 'FAIL'}")
    print(f"Demonstration 2 (No activation):   {'PASS' if demo2_success else 'FAIL'}")
    print(f"Demonstration 3 (Explicit use):    {'PASS' if demo3_success else 'FAIL'}")
    
    if demo1_success and demo2_success and demo3_success:
        print("\n\u2705 ALL DEMONSTRATIONS PASSED - NEUROSYMBOLIC REASONING IS FULLY OPERATIONAL!")
        return 0
    else:
        print("\n\u274c SOME DEMONSTRATIONS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())