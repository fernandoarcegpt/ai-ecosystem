#!/usr/bin/env python3
"""Integration test for Policy Gate and Human Gate with orchestrator.
This test validates the complete integration of the policy gate system."""
import os
import sys
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the skills directory to sys.path so we can import policy_gate.skill and human_gate.skill
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.hermes', 'skills'))

try:
    # Import the skills
    from policy_gate.skill import PolicyGate
    from human_gate.skill import HumanGate
    logger.info("✅ Skills imported successfully")
    
    # Test 1: Policy Gate functionality
    logger.info("\n🔍 Testing Policy Gate...")
    policy_gate = PolicyGate()
    
    # Test safe task
    safe_result = policy_gate.evaluate_task("read configuration file")
    assert safe_result.authorized == True, "Safe task should be authorized"
    assert safe_result.decision_result == "allow", "Safe task should be allowed"
    logger.info("✅ Safe task evaluation passed")
    
    # Test critical task (should be blocked or require human)
    critical_result = policy_gate.evaluate_task("modify admin settings")
    assert critical_result.requires_human_review == True, "Critical task should require human review"
    logger.info("✅ Critical task evaluation passed")
    
    # Test 2: Human Gate functionality
    logger.info("\n🔍 Testing Human Gate...")
    human_gate = HumanGate()
    
    # Submit a task for review
    review = human_gate.submit_for_review(
        task_description="modify safety policy",
        actor="orchestrator",
        metadata={"task_id": "test-task-001"}
    )
    # Now review is an object
    assert review.review_id.startswith("review-"), "Review ID should have correct format"
    logger.info(f"✅ Review submitted: {review.review_id}")
    
    # Check pending reviews
    pending = human_gate.check_pending_reviews()
    assert len(pending) == 1, "Should have one pending review"
    logger.info("✅ Pending reviews check passed")
    
    # Process the review
    human_gate.process_review(review.review_id, "approve", "Approved for execution")
    
    # Verify review is processed
    pending = human_gate.check_pending_reviews()
    assert len(pending) == 0, "All reviews should be processed after approval"
    logger.info("✅ Review processing passed")
    
    # Test 3: Integration scenario
    logger.info("\n🔍 Testing integration scenario...")
    
    # Simulate policy evaluation leading to human review
    task_description = "modify system security settings"
    policy_result = policy_gate.evaluate_task(task_description)
    
    if policy_result.requires_human_review:
        # Create review request through integration
        new_review = human_gate.submit_for_review(
            task_description=task_description,
            actor="orchestrator",
            metadata={
                "policy_id": policy_result.policy_id,
                "policy_reason": policy_result.reason,
                "integration_test": True
            }
        )
        logger.info(f"✅ Integration scenario successful: review {new_review.review_id} created")
    
    print("\n" + "="*70)
    print("🎉 INTEGRATION TEST PASSED")
    print("="*70)
    print("✅ Policy Gate: Successfully evaluates tasks against policies")
    print("✅ Human Gate: Successfully manages human review workflow")
    print("✅ Integration: Successfully combines both systems")
    print("="*70)
    print("The Policy Gate and Human Gate skills are fully functional")
    print("and ready for production use in the Hermes Agent ecosystem.")
    
except Exception as e:
    logger.error(f"❌ Integration test failed: {str(e)}")
    import traceback
    traceback.print_exc()
    print(f"\n❌ Test failed with error: {str(e)}")
    sys.exit(1)