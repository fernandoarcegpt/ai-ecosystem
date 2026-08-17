"""
Motor de políticas determinista para Hermes.

Este motor aplica políticas definidas en YAML como primera autoridad antes de
cualquier ejecución, implementando una jerarquía de decisión clara:
DENY > REQUIRE_HUMAN > UNKNOWN > ALLOW
"""

import os
import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime

# Importar contratos desde el mismo paquete
from .contracts import PolicyEngineInterface, PolicyEngineContext, Policy, Decision, DecisionResult, Actor, FilePath, Evidence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyEngine(PolicyEngineInterface):
    """
    Motor de políticas determinista.
    - Loads YAML policies from a directory
    - Provides evaluation with audit trails
    - Enforces hierarchical decision precedence
    """
    
    def __init__(self, policies_dir: str = None):
        self.policies_dir = policies_dir or "/home/fernando/ai-ecosystem/src/reasoning/policies"
        self.loaded_policies: Dict[str, Policy] = {}
        self.engine_version = "1.0.0"
        self.last_loaded = None
        
        # Load policies on initialization
        self.load_policies(self.policies_dir)
        
    def load_policies(self, policy_dir: str) -> bool:
        """
        Load policies from YAML files in the given directory.
        
        Args:
            policy_dir: Directory path containing YAML policy files
            
        Returns:
            bool: True if policies loaded successfully, False otherwise
        """
        if not os.path.isdir(policy_dir):
            logger.error(f"Policy directory does not exist: {policy_dir}")
            return False
            
        policy_files = []
        for root, dirs, files in os.walk(policy_dir):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    policy_files.append(os.path.join(root, file))
                
        if not policy_files:
            logger.warning(f"No YAML policy files found in {policy_dir}")
            return False
            
        loaded_count = 0
        for policy_file in policy_files:
            try:
                with open(policy_file, 'r') as f:
                    policies_data = yaml.safe_load(f)
                    
                if not policies_data:
                    logger.warning(f"Empty policy file: {policy_file}")
                    continue
                    
                # Handle different YAML structures
                if isinstance(policies_data, dict):
                    # Single policy entry
                    policies = [policies_data]
                else:
                    # List of policies
                    policies = policies_data
                    
                for policy_dict in policies:
                    # Convert dict to Policy object
                    policy = self._dict_to_policy(policy_dict)
                    if policy:
                        self.loaded_policies[policy.id] = policy
                        loaded_count += 1
                        logger.info(f"Loaded policy: {policy.id} ({policy.effect})")
                        
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error in {policy_file}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error loading policy from {policy_file}: {e}")
                continue
                
        if loaded_count > 0:
            self.last_loaded = datetime.now()
            logger.info(f"Successfully loaded {loaded_count} policies from {policy_dir}")
            return True
        else:
            logger.error(f"Failed to load any policies from {policy_dir}")
            return False
            
    def _dict_to_policy(self, policy_dict: Dict) -> Optional[Policy]:
        """
        Convert a dictionary to a Policy object.
        
        Args:
            policy_dict: Dictionary containing policy data
            
        Returns:
            Policy object or None if conversion fails
        """
        try:
            # Validate required fields
            required_fields = ['id', 'version', 'description', 'priority', 'effect']
            for field_name in required_fields:
                if field_name not in policy_dict:
                    logger.error(f"Policy missing required field: {field_name}")
                    return None
                    
            # Create Policy object
            policy = Policy(
                id=policy_dict['id'],
                version=policy_dict.get('version', '1.0'),
                description=policy_dict['description'],
                priority=policy_dict['priority'],
                when=policy_dict.get('when', []),
                effect=policy_dict['effect'],
                obligations=policy_dict.get('obligations', [])
            )
            return policy
            
        except Exception as e:
            logger.error(f"Error converting policy dict to Policy object: {e}")
            return None
            
    def evaluate_policy(self, context: PolicyEngineContext) -> Decision:
        """
        Evaluate a task against loaded policies.
        
        Args:
            context: PolicyEngineContext containing task details
            
        Returns:
            Decision object with recommendation based on policies
        """
        logger.info(f"Evaluating task '{context.task_id}': {context.task_description}")
        
        # Extract relevant information from context
        actor = context.actor
        target = context.target
        action = context.action
        context_data = context.context_data
        
        # Initialize decision with default values
        decision_result = DecisionResult.ALLOW
        reason = "No matching policies found - default ALLOW"
        engine_version = "1.0.0"
        confidence = 1.0
        rules_triggered = []
        facts_used = []
        evidence_list = []
        
        # Evaluate each loaded policy
        for policy_id, policy in self.loaded_policies.items():
            if self._policy_matches(policy, actor, target, action, context_data):
                rules_triggered.append(policy_id)
                
                # Apply policy effect
                policy_effect = self._apply_policy_effect(policy, policy_id)
                if policy_effect:
                    # Check if this effect overrides previous decision
                    # DENY > REQUIRE_HUMAN > ALLOW
                    if policy_effect == DecisionResult.DENY:
                        decision_result = policy_effect
                        reason = f"Policy {policy_id} DENY: {policy.description}"
                        break
                    elif policy_effect == DecisionResult.REQUIRE_HUMAN:
                        # Only set to REQUIRE_HUMAN if not already DENY
                        if decision_result != DecisionResult.DENY:
                            decision_result = policy_effect
                            reason = f"Policy {policy_id} REQUIRE_HUMAN: {policy.description}"
                    elif policy_effect == DecisionResult.ALLOW:
                        # Only set to ALLOW if not already DENY or REQUIRE_HUMAN
                        if decision_result == DecisionResult.ALLOW:
                            decision_result = policy_effect
                            reason = f"Policy {policy_id} ALLOW: {policy.description}"
                            
                # Create evidence
                evidence = Evidence(
                    source="policy",
                    content={
                        "policy_id": policy_id,
                        "policy_description": policy.description,
                        "policy_effect": policy.effect
                    },
                    confidence_score=1.0,
                    source_type="policy",
                    file_path=target if isinstance(target, FilePath) else None,
                    metadata={"action": action, "context_data": context_data}
                )
                evidence_list.append(evidence)
                
        # Create decision object
        decision = Decision(
            decision_id=f"dec-{context.task_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_id=context.task_id,
            requested_by=actor,
            decision_result=decision_result,
            reason=reason,
            evidence=evidence_list,
            rules_triggered=rules_triggered,
            facts_used=facts_used,
            engine="policy_engine.py",
            engine_version=engine_version,
            confidence=confidence,
            required_actions=self._get_required_actions(rules_triggered),
            expiration=None,
            created_at=datetime.now(),
            metadata={
                "context_task_description": context.task_description,
                "context_action": action,
                "context_target_type": "FilePath" if isinstance(target, FilePath) else "other"
            }
        )
        
        logger.info(f"Decision for task '{context.task_id}': {decision_result}")
        return decision
        
    def _policy_matches(self, policy: Policy, actor: Actor, target: Union[FilePath, Dict[str, Any]], action: str, context_data: Dict[str, Any]) -> bool:
        """
        Check if a policy matches the given context.
        
        Args:
            policy: Policy to evaluate
            actor: Actor performing the task
            target: Target of the action
            action: Action being performed
            context_data: Additional context information
            
        Returns:
            bool: True if policy matches, False otherwise
        """
        # Check if policy has when conditions
        if 'when' not in policy.when or not policy.when:
            return True  # No conditions means always match
            
        # TODO: Implement more sophisticated policy matching logic
        # For now, do a basic check based on policy ID patterns
        # In a real implementation, this would use Datalog/Z3 for complex inference
        
        # Simple matching based on policy ID prefixes
        if policy.id.startswith('SAF-'):
            # Security policies
            if action in ['modify', 'delete'] and isinstance(target, FilePath):
                return True
        elif policy.id.startswith('PERM-'):
            # Permission policies
            if action == 'read' and isinstance(target, FilePath):
                return True
        elif policy.id.startswith('ENV-'):
            # Environment policies
            if 'environment' in context_data:
                return True
        elif policy.id.startswith('AUDIT-'):
            # Audit policies - apply to any modification
            if action == 'modify':
                return True
                
        return False
        
    def _apply_policy_effect(self, policy: Policy, policy_id: str) -> DecisionResult:
        """
        Apply a policy effect.
        
        Args:
            policy: Policy to apply
            policy_id: Policy ID
            
        Returns:
            DecisionResult: The effect to apply
        """
        # Simple effect mapping
        effect_map = {
            'deny': DecisionResult.DENY,
            'require_human': DecisionResult.REQUIRE_HUMAN,
            'allow': DecisionResult.ALLOW,
            'unknown': DecisionResult.UNKNOWN
        }
        
        # Normalize effect string
        effect = policy.effect.lower()
        
        # Handle complex effects (e.g., "deny OR require_human")
        # For now, just use the first effect
        if effect in effect_map:
            return effect_map[effect]
        else:
            # Try to extract first effect from compound
            for simple_effect in ['deny', 'require_human', 'allow', 'unknown']:
                if simple_effect in effect:
                    return effect_map[simple_effect]
                    
        logger.warning(f"Unknown policy effect '{policy.effect}' in policy {policy_id}")
        return DecisionResult.UNKNOWN
        
    def _get_required_actions(self, rules_triggered: List[str]) -> List[str]:
        """
        Get required actions based on triggered rules.
        
        Args:
            rules_triggered: List of policy IDs that were triggered
            
        Returns:
            List of required actions (e.g., "approve_human", "audit_log")
        """
        required_actions = []
        
        for policy_id in rules_triggered:
            if policy_id.startswith('SAF-'):
                # Security policies - require human approval
                required_actions.append("approve_human")
                required_actions.append("audit_log")
            elif policy_id.startswith('ENV-'):
                # Environment policies
                if policy_id.endswith('-PROD'):
                    required_actions.append("approve_human")
            elif policy_id.startswith('AUDIT-'):
                # Audit policies
                required_actions.append("audit_log")
                required_actions.append("create_checkpoint")
                
        # Remove duplicates
        return list(set(required_actions))
        
    def get_policy_by_id(self, policy_id: str) -> Optional[Policy]:
        """
        Get a policy by its ID.
        
        Args:
            policy_id: Policy ID to retrieve
            
        Returns:
            Policy object or None if not found
        """
        return self.loaded_policies.get(policy_id)
        
    def reload_policies(self) -> bool:
        """
        Reload all policies from the policy directory.
        
        Returns:
            bool: True if policies reloaded successfully, False otherwise
        """
        logger.info("Reloading policies...")
        
        # Clear existing policies
        self.loaded_policies.clear()
        
        # Load policies again
        return self.load_policies(self.policies_dir)