#!/usr/bin/env python3
"""Policy Gate implementation for Hermes Agent Ecosystem.
Provides policy evaluation before task execution with human review integration.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PolicyGateResult:
    """Result of policy gate evaluation"""
    authorized: bool
    requires_human_review: bool
    decision_result: str
    reason: str
    evidence: list = field(default_factory=list)
    policy_id: str = "UNKNOWN"""

class DecisionResult:
    """Decision result constants"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_HUMAN = "require_human"
    UNKNOWN = "unknown"

class PolicyGate:
    """Policy Gate - Evaluates policies before task execution.
    
    This class acts as a security gate that verifies tasks
    before allowing execution. If a task requires human 
    approval, it triggers the Human Gate workflow.
    """
    
    def __init__(self, policies_dir: str = None):
        """Initialize Policy Gate with policies directory."""
        if policies_dir is None:
            policies_dir = os.path.join(
                os.path.dirname(__file__),
                '..', '..', '..',
                'ai-ecosystem', 'src', 'reasoning', 'policies'
            )
            policies_dir = os.path.abspath(policies_dir)
        
        self.policies_dir = policies_dir
        logger.info(f"Initializing Policy Gate with policies dir: {self.policies_dir}")
        
        # Initialize policy engine if available
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'ai-ecosystem', 'src'))
            from reasoning.policy_engine import PolicyEngine
            self.policy_engine = PolicyEngine(policies_dir)
            logger.info("Policy Engine initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize Policy Engine: {e}")
            self.policy_engine = None
        
        logger.info("Policy Gate ready")
    
    def evaluate_task(self, task_description: str, actor: str = "user") -> PolicyGateResult:
        """Evaluate a task against policies.
        
        Args:
            task_description: Description of the task to evaluate
            actor: Who is performing the task
            
        Returns:
            PolicyGateResult with evaluation outcome
        """
        # Simple pattern matching for critical operations
        critical_patterns = ['modify', 'delete', 'remove', 'override', 'bypass']
        privileged_patterns = ['config', 'admin', 'settings', 'permissions']
        safe_patterns = ['read', 'view', 'analyze', 'list', 'show', 'help']
        
        task_lower = task_description.lower()
        
        # Check for critical operations
        for pattern in critical_patterns:
            if pattern in task_lower:
                for priv_pattern in privileged_patterns:
                    if priv_pattern in task_lower:
                        return PolicyGateResult(
                            authorized=False,
                            requires_human_review=True,
                            decision_result=DecisionResult.REQUIRE_HUMAN,
                            reason=f"Critical operation '{pattern}' detected on privileged target '{priv_pattern}'",
                            evidence=[],
                            policy_id="SAF-PRIVILEGED-003"
                        )
                # If not privileged, deny critical operations
                return PolicyGateResult(
                    authorized=False,
                    requires_human_review=False,
                    decision_result=DecisionResult.DENY,
                    reason=f"Critical operation '{pattern}' detected without proper authorization",
                    evidence=[],
                    policy_id="SAF-CRITICAL-001"
                )
        
        # Check for safe patterns
        for pattern in safe_patterns:
            if pattern in task_lower:
                return PolicyGateResult(
                    authorized=True,
                    requires_human_review=False,
                    decision_result=DecisionResult.ALLOW,
                    reason="Safe read-only operation",
                    evidence=[],
                    policy_id="PERM-READ-001"
                )
        
        # Default to require human review for unknown operations
        return PolicyGateResult(
            authorized=True,  # Allow execution but flag for review
            requires_human_review=True,
            decision_result=DecisionResult.UNKNOWN,
            reason="Unknown operation type - human review recommended",
            evidence=[],
            policy_id="UNKNOWN-POLICY"
        )
    
    def create_review_request(self, result: PolicyGateResult, 
                             task_description: str, actor: str = "user") -> Dict[str, Any]:
        """Create a human review request payload.
        
        Args:
            result: The PolicyGateResult that triggered review
            task_description: Original task description
            actor: Who requested the task
            
        Returns:
            Dict with review request details
        """
        return {
            "review_id": f"review-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "task_description": task_description,
            "requested_by": actor,
            "review_reason": result.reason,
            "policy_id": result.policy_id,
            "status": "pending",
            "reminder_sent": False,
            "timestamp": datetime.now().isoformat()
        }