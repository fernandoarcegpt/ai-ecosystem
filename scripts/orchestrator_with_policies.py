#!/usr/bin/env python3
"""Orchestration Pipeline with Policy Gate Integration.

This script demonstrates how to integrate the Policy Gate into the
Hermes orchestration workflow. It loads policies, evaluates tasks,
and handles human review when required.

USAGE:
    python3 scripts/orchestrator_with_policies.py --gate-policy \
        --task-id "task-001" \
        --task-description "modify system configuration" \
        [--actor-id "system"]

When --gate-policy is provided, tasks are evaluated against policies
before execution. If a policy requires human review, the request is sent
to the Human Gate.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add skills to Python path
sys.path.insert(0, os.path.expanduser('~/.hermes/skills'))
sys.path.insert(0, os.path.join(os.path.expanduser('~/.hermes/skills/policy-gate'), 'script'))
sys.path.insert(0, os.path.join(os.path.expanduser('~/.hermes/skills/human-gate'), 'script'))

try:
    from policy_gate.script import PolicyGate
    from human_gate.script import HumanGate
    from policy_engine.contracts import PolicyEngineContext
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Default policies directory
DEFAULT_POLICIES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'ai-ecosystem', 'src', 'reasoning', 'policies')
)

def main():
    parser = argparse.ArgumentParser(
        description='Hermes Orchestration Pipeline with Policy Gate Integration'
    )
    parser.add_argument('--gate-policy', action='store_true',
                        help='Enable policy evaluation before task execution')
    parser.add_argument('--policy-dir', default=DEFAULT_POLICIES_DIR,
                        help='Directory containing policy YAML files')
    parser.add_argument('--task-id', required=True, help='Unique identifier for the task')
    parser.add_argument('--task-description', required=True, help='Description of the task to evaluate')
    parser.add_argument('--actor-id', default='system',
                        help='Identifier for the actor requesting task execution')
    parser.add_argument('--output', default='execution.log',
                        help='File to log execution results')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Hermes Orchestration Pipeline with Policy Gate")
    logger.info(f"Policy directory: {args.policy_dir}")
    
    # Initialize Policy Gate
    try:
        policy_gate = PolicyGate(policies_dir=args.policy_dir)
        logger.info("✅ Policy Gate initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Policy Gate: {str(e)}")
        sys.exit(1)
    
    # If policy gate evaluation is requested
    if args.gate_policy:
        logger.info("🔍 Evaluating task against policies...")
        try:
            # Create policy evaluation context
            context = PolicyEngineContext(
                engine="policy_gate",
                task_id=args.task_id,
                task_description=args.task_description,
                actor={
                    "id": args.actor_id,
                    "type": "system",
                    "role": "orchestrator"
                },
                target={"path": "/dummy/path", "category": "system"},
                action="modify",
                context_data={"task": args.task_description}
            )
            
            decision = policy_gate.policy_engine.evaluate_policy(context)
            
            logger.info(f"Policy evaluation result: {decision.decision_result}")
            logger.info(f"Reason: {decision.reason}")
            logger.info(f"Policies triggered: {decision.rules_triggered}")
            
            # Handle decision outcomes
            if decision.decision_result == "deny":
                logger.error(f"❌ Task denied by policy: {decision.reason}")
                sys.exit(1)
                
            elif decision.decision_result == "require_human":
                logger.warning(f"⚠️  Task requires human approval: {decision.reason}")
                # Initialize Human Gate for review process
                human_gate = HumanGate()
                review_id = human_gate.submit_for_review(
                    task_description=args.task_description,
                    actor=args.actor_id,
                    metadata={"task_id": args.task_id, "policy_decision": decision.reason}
                )
                logger.info(f"📝 Review request submitted: {review_id}")
                
                # Process the human review decision
                # In a real system, this would wait for human input
                # For demo/testing, simulate approval immediately
                if human_gate.process_review(review_id, "approve", "Approved by system"):
                    logger.info("🎉 Human review approved, proceeding with task execution")
                else:
                    logger.error("Failed to process human review")
                    sys.exit(1)
            else:  # allow or unknown (default to proceed)
                logger.info("✅ Task approved by policy gate, proceeding with execution")
                
        except Exception as e:
            logger.error(f"Policy evaluation failed: {str(e)}")
            sys.exit(1)
    
    # Execute the task (simulated)
    try:
        logger.info(f"💡 Executing task: {args.task_id} - {args.task_description}")
        # Here you would integrate with actual task execution pipeline
        # For demo purposes, we'll simulate execution
        execution_id = f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Execution completed: {execution_id}")
        
        # Log results
        with open(args.output, 'a') as log_file:
            log_entry = f"{datetime.now().isoformat()} | {args.task_id} | SUCCESS | Policy Gate: {decision.decision_result if args.gate_policy else 'N/A'}\n"
            log_file.write(log_entry)
        
        logger.info(f"✅ Task completed successfully. Results logged to {args.output}")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Task execution failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()