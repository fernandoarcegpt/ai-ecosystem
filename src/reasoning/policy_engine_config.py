from typing import Dict, List, Any

# Configuration for the policy engine
class PolicyEngineConfig:
    """Configuration for the Policy Engine"""
    
    def __init__(self):
        # Directories for policy storage
        self.POLICIES_DIR = "/home/fernando/ai-ecosystem/src/reasoning/policies"
        self.CONTRACTS_DIR = "/home/fernando/ai-ecosystem/src/reasoning"
        
        # Policy engine settings
        self.STRICT_MODE = True  # Always require explicit approval
        self.DEFAULT_EFFECT = "allow"  # Fallback effect
        self.MAX_POLICIES_TO_EVALUATE = 50  # Prevent performance issues
        self.ENABLE_AUDIT_LOGGING = True
        
        # Policy evaluation settings
        self.PRIORITY_ORDER = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        
        self.EFFECT_PRIORITY = {
            "deny": 1,
            "require_human": 2,
            "allow": 3,
            "unknown": 0
        }
        
        # File patterns for critical files
        self.CRITICAL_FILE_PATTERNS = [
            ".env*",
            "**/.env*",
            "secrets/**",
            "config/production/**",
            "reasoning/policies/**",
            "system-prompts/**",
            "*.key",
            "*.pem",
            "password.*",
            "credential.*",
            "token.*"
        ]
        
        # Dangerous actions
        self.DANGEROUS_ACTIONS = [
            "delete", "rm", "truncate", "clear", "modify", "overwrite",
            "sudo", "su", "chmod 777", "chown *", "visudo", "passwd"
        ]

# Export the configuration
__all__ = ["PolicyEngineConfig"]