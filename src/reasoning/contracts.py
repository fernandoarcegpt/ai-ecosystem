"""
Contracts para el sistema de razonamiento híbrido de Hermes.

Estos contratos definen interfaces claras y tipadas para la comunicación entre
los diferentes componentes del sistema.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Literal
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    RECEIVED = "received"
    CONTEXT_BUILDING = "context_building"
    PLANNED = "planned"
    POLICY_CHECK = "policy_check"
    WAITING_APPROVAL = "waiting_approval"
    AUTHORIZED = "authorized"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ROLLED_BACK = "rolled_back"

class DecisionResult(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_HUMAN = "require_human"
    UNKNOWN = "unknown"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Actor:
    """Representa un actor (humano, ejecutor, sistema) en la orquestación de tareas"""
    id: str
    type: str  # "human", "executor", "system", "agent"
    role: str
    capabilities: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

@dataclass
class FilePath:
    """Representa una ruta de archivo con contexto para políticas"""
    path: str
    absolute_path: str
    is_critical: bool = False
    is_protected: bool = False
    category: str = ""  # "secrets", "production", "source", "docs"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskPlan:
    """Plan estructurado propuesto para una tarea"""
    task_id: str
    description: str
    priority: TaskPriority
    requested_by: Actor
    executor: Actor
    status: TaskStatus = TaskStatus.RECEIVED
    steps: List[Dict[str, Any]] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    risk_hints: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # "low", "medium", "high", "critical"
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    checkpoints: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class Evidence:
    """Evidencia para soporte de una decisión"""
    source: str
    content: Dict[str, Any]
    confidence_score: float = 1.0
    source_type: str = ""  # "policy", "memory", "knowledge_broker", "human"
    file_path: Optional[FilePath] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Decision:
    """Decisión tomada por el motor de políticas o un motor simbólico"""
    # Non-default fields first
    decision_id: str
    task_id: str
    requested_by: Actor
    decision_result: DecisionResult
    reason: str
    engine: str
    # Fields with default values follow
    evidence: List[Evidence] = field(default_factory=list)
    rules_triggered: List[str] = field(default_factory=list)
    facts_used: List[Dict[str, str]] = field(default_factory=list)
    engine_version: str = "1.0"
    confidence: float = 1.0
    required_actions: List[str] = field(default_factory=list)
    expiration: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionResult:
    """Resultado de una ejecución"""
    execution_id: str
    task_id: str
    executor: Actor
    status: str  # "success", "failed", "timeout", "partial"
    output: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    artifacts_created: List[FilePath] = field(default_factory=list)
    artifacts_modified: List[FilePath] = field(default_factory=list)
    verification_results: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time: float = 0.0
    exit_code: Optional[int] = None

@dataclass
class VerificationResult:
    """Resultado de verificación"""
    verification_id: str
    task_id: str
    verifier: Actor
    verification_status: str  # "passed", "failed", "warning"
    test_cases_executed: int = 0
    test_cases_passed: int = 0
    failures: List[Dict[str, str]] = field(default_factory=list)
    warnings: List[Dict[str, str]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    detailed_results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HumanReviewRequest:
    """Solicitud de aprobación humana para acciones críticas"""
    # Non-default fields first
    review_id: str
    task_id: str
    requested_by: Actor
    review_reason: str
    proposed_plan: TaskPlan
    # Fields with default values follow
    requested_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "approved", "rejected", "timeout"
    evidence: List[Evidence] = field(default_factory=list)
    reviewer: Optional[Actor] = None
    decision: Optional[Decision] = None
    response: Optional[str] = None
    reminder_sent: bool = False

@dataclass
class Checkpoint:
    """Checkpoint para rollback"""
    # Non-default fields first
    checkpoint_id: str
    task_id: str
    created_by: Actor
    description: str
    version: str
    state: Dict[str, Any] = field(default_factory=dict)
    # Fields with default values follow
    created_at: datetime = field(default_factory=datetime.now)
    is_complete: bool = True
    requires_approval: bool = True

@dataclass
class Policy:
    """Definición de política desde la fuente canónica YAML"""
    id: str
    version: str
    description: str
    priority: str
    when: Dict[str, Any]
    effect: str
    obligations: List[str] = field(default_factory=list)

@dataclass
class PolicyEngineContext:
    """Contexto para evaluación de políticas"""
    # Non-default fields first
    engine: str
    task_id: str
    task_description: str
    actor: Actor
    target: Union[FilePath, Dict[str, Any]]
    action: str
    # Fields with default values follow
    context_data: Dict[str, Any] = field(default_factory=dict)
    previous_decisions: List[Decision] = field(default_factory=list)
    policy_version: str = "1.0"
    timestamp: datetime = field(default_factory=datetime.now)
    compliance_checks: List[Dict[str, Any]] = field(default_factory=list)

# Interfaces principales

class PolicyEngineInterface:
    """Interface para motores de políticas"""
    
    def evaluate_policy(self, context: PolicyEngineContext) -> Decision:
        """Evaluar una tarea contra políticas"""
        raise NotImplementedError
    
    def load_policies(self, policy_dir: str) -> bool:
        """Cargar políticas desde directorio YAML"""
        raise NotImplementedError
    
    def get_policy_by_id(self, policy_id: str) -> Optional[Policy]:
        """Obtener política por ID"""
        raise NotImplementedError
    
    def reload_policies(self) -> bool:
        """Recargar políticas desde la fuente"""
        raise NotImplementedError

class HumanGateInterface:
    """Interface para aprobación/aprobación humana"""
    
    def submit_for_review(self, review_request: HumanReviewRequest) -> HumanReviewRequest:
        """Enviar tarea para revisión humana"""
        raise NotImplementedError
    
    def process_review(self, review_id: str, reviewer: Actor, decision: DecisionResult, response: str) -> HumanReviewRequest:
        """Procesar decisión humana"""
        raise NotImplementedError
    
    def check_pending_reviews(self) -> List[HumanReviewRequest]:
        """Obtener revisiones pendientes"""
        raise NotImplementedError

class AuditLoggerInterface:
    """Interface para auditoría y rastreo"""
    
    def log_decision(self, decision: Decision) -> bool:
        """Registrar decisión"""
        raise NotImplementedError
    
    def log_execution(self, result: ExecutionResult) -> bool:
        """Registrar ejecución"""
        raise NotImplementedError
    
    def log_verification(self, result: VerificationResult) -> bool:
        """Registrar verificación"""
        raise NotImplementedError
    
    def create_checkpoint(self, checkpoint: Checkpoint) -> bool:
        """Crear checkpoint"""
        raise NotImplementedError
    
    def rollback_to_checkpoint(self, checkpoint_id: str, reason: str) -> bool:
        """Rollback a checkpoint"""
        raise NotImplementedError

class OrchestratorInterface:
    """Interface para el orquestador principal de Hermes"""
    
    def execute_task(self, plan: TaskPlan) -> Union[ExecutionResult, HumanReviewRequest]:
        """Ejecutar una tarea (o enviar para revisión si es crítica)"""
        raise NotImplementedError
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Obtener estado de tarea"""
        raise NotImplementedError
    
    def rollback_task(self, task_id: str, reason: str) -> bool:
        """Rollback de tarea"""
        raise NotImplementedError