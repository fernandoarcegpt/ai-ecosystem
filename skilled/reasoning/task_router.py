"""Sistema de enrutamiento de tareas y coordinación de agentes

Este módulo implementa la lógica central para:
- Comprensión y planificación de objetivos
- Descomposición en tareas ejecutables  
- Análisis de dependencias y riesgos
- Selección automática de agentes especializados
- Coordinación de ejecución y verificación
"""

import json
import re
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime

# Importar componentes del ecosistema
REASONING_AVAILABLE = False
try:
    from .networkx_wrapper import GraphAnalyzer
    from .pydatalog_integration import SymbolicEngine
    from .z3_solver_integration import ConstraintSolver
    from . import NeuroSymbolicEngine, ENABLED, CURRENT_MODE
    REASONING_AVAILABLE = True
except ImportError:
    pass

class TaskStatus(Enum):
    PROPOSED = "proposed"           # Propuesta inicial
    IN_PROGRESS = "in_progress"     # Trabajo en curso
    PENDING_VERIFICATION = "pending_verification"  # Resultado pendiente de verificación
    VALIDATED = "validated"        # Resultado validado
    BLOCKED = "blocked"             # Bloqueada por dependencias o información faltante
    FAILED = "failed"               # Falló durante ejecución
    COMPLETED = "completed"         # Tarea completada y verificada

@dataclass
class Task:
    id: str
    description: str
    type: str  # implementation, research, analysis, review, qa
    priority: int
    dependencies: List[str]
    assigned_agent: Optional[str]  # orquestador, builder, researcher, reviewer, qa
    status: TaskStatus
    constraints: List[str]  # Restricciones simbólicas
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str

@dataclass
class RouteDecision:
    agent: str
    confidence: float
    reason: str
    constraints_applied: List[str]

class TaskRouter:
    """Enrutador inteligente de tareas usando razonamiento neurosimbólico"""

    def __init__(self):
        self.swarm_config = self._load_swarm_config()
        self.reasoning_engine = self._initialize_reasoning_engine()
        
    def _load_swarm_config(self) -> List[Dict]:
        """Cargar configuración del sistema de agentes"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            "hermes-workspace", 
            "swarm.yaml"
        )
        
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config.get('workers', [])
        except Exception:
            # Retornar configuración por defecto
            return self._default_swarm_config()

    def _default_swarm_config(self) -> List[Dict]:
        """Configuración base de agentes especializados"""
        return [
            {
                "id": "orchestrator",
                "name": "Orchestrator",
                "specialty": "mission routing, task decomposition, handoffs",
                "capabilities": ["orchestration", "decomposition", "routing"],
                "preferredTaskTypes": ["orchestration", "planning", "routing"],
                "greenlightRequiredFor": ["merge", "publish", "destructive"]
            },
            {
                "id": "km-agent",
                "name": "KM Agent",
                "specialty": "knowledge management, documentation",
                "capabilities": ["gbrain", "razsoc", "obsidian"],
                "preferredTaskTypes": ["knowledge", "curation", "documentation"]
            },
            {
                "id": "builder",
                "name": "Builder",
                "specialty": "focused implementation, tests, small diffs",
                "capabilities": ["implementation", "code-editing", "tests"],
                "preferredTaskTypes": ["implementation", "bugfix", "feature"]
            },
            {
                "id": "researcher",
                "name": "Researcher",
                "specialty": "research, synthesis, source trails",
                "capabilities": ["research", "synthesis", "source-verification"],
                "preferredTaskTypes": ["research", "analysis", "options"]
            },
            {
                "id": "qa",
                "name": "QA",
                "specialty": "browser QA, workflow smoke tests",
                "capabilities": ["browser-qa", "smoke-verification"],
                "preferredTaskTypes": ["qa", "smoke", "browser", "verification"]
            },
            {
                "id": "reviewer",
                "name": "Reviewer",
                "specialty": "security review, logic review, regression detection",
                "capabilities": ["code-review", "security-review", "regression-analysis"],
                "preferredTaskTypes": ["review", "qa", "regression", "verification"]
            }
        ]

    def _initialize_reasoning_engine(self):
        """Inicializar motor de razonamiento neurosimbólico"""
        if REASONING_AVAILABLE and ENABLED:
            try:
                return NeuroSymbolicEngine()
            except Exception:
                return None
        return None

    def decompose_objective(self, objective: str) -> List[Task]:
        """Descomponer un objetivo complejo en tareas ejecutables"""
        tasks = []
        timestamp = datetime.now().isoformat()
        
        # Análisis semántico del objetivo
        objective_lower = objective.lower()
        
        # Identificar patrones de tareas comunes
        patterns = {
            "implementar": {
                "types": ["implementation", "analysis"],
                "agents": ["builder", "researcher"]
            },
            "investigar": {
                "types": ["research", "analysis"],
                "agents": ["researcher", "analyst"]
            },
            "verificar": {
                "types": ["qa", "review"],
                "agents": ["qa", "reviewer"]
            },
            "analizar": {
                "types": ["analysis"],
                "agents": ["researcher", "analyst"]
            },
            "documentar": {
                "types": ["documentation"],
                "agents": ["km-agent"]
            }
        }
        
        # Detectar intención principal
        detected_type = "analysis"
        for keyword, pattern in patterns.items():
            if keyword in objective_lower:
                detected_type = pattern["types"][0]
                break
                
        # Generar tareas básicas
        task_templates = [
            ("Comprensión del problema", "analysis"),
            ("Análisis de contexto", "analysis"),
            ("Diseño de solución", "design"),
            ("Implementación", "implementation"),
            ("Pruebas", "qa"),
            ("Documentación", "documentation")
        ]
        
        # Filtrar y ordenar según tipo detectado
        if detected_type == "implementation":
            selected_indices = [0, 1, 2, 3, 4]
        elif detected_type == "research":
            selected_indices = [0, 1, 3, 5]
        elif detected_type == "qa":
            selected_indices = [4]
        else:
            selected_indices = list(range(len(task_templates)))
            
        # Crear tareas
        for idx in selected_indices:
            name, task_type = task_templates[idx]
            task = Task(
                id=f"task_{idx+1}_{datetime.now().strftime('%H%M%S')}",
                description=f"{name}: {objective}",
                type=task_type,
                priority=len(selected_indices) - idx,
                dependencies=[f"task_{i+1}_{datetime.now().strftime('%H%M%S')}" 
                            for i in range(idx) if idx > 0],
                assigned_agent=None,  # Se asignará durante el enrutamiento
                status=TaskStatus.PROPOSED,
                constraints=[],
                metadata={"source_objective": objective},
                created_at=timestamp,
                updated_at=timestamp
            )
            tasks.append(task)
            
        return tasks

    def route_task(self, task: Task) -> RouteDecision:
        """Seleccionar el agente especializado más adecuado para una tarea"""
        best_match = self._match_agent_by_capability(task)
        
        # Aplicar razonamiento neurosimbólico si está disponible
        if self.reasoning_engine and task.type in ["design", "analysis"]:
            symbolic_decision = self._evaluar_con_simbolico(task)
            if symbolic_decision:
                return symbolic_decision
                
        return RouteDecision(
            agent=best_match["id"],
            confidence=best_match["confidence"],
            reason=best_match["reason"],
            constraints_applied=[]
        )

    def _match_agent_by_capability(self, task: Task) -> Dict:
        """Encontrar agente con capacidades que mejor coinciden con la tarea"""
        best_match = {
            "id": "orchestrator",  # Valor por defecto
            "confidence": 0.5,
            "reason": "Asignación por defecto"
        }
        
        # Coincidencia directa de tipos preferidos
        for agent in self.swarm_config:
            preferred_types = agent.get("preferredTaskTypes", [])
            capabilities = agent.get("capabilities", [])
            
            # Calcular puntuación de coincidencia
            score = 0
            reasons = []
            
            if task.type in preferred_types:
                score += 0.5
                reasons.append(f"Tipo {task.type} en tipos preferidos")
                
            # Verificar si las restricciones de la tarea pueden manejarse con las capacidades del agente
            capability_keywords = [c.lower() for c in capabilities]
            task_keywords = re.findall(r'\b\w+\b', task.description.lower())
            
            overlap = set(task_keywords) & set(capability_keywords)
            score += len(overlap) * 0.1
            if overlap:
                reasons.append(f"Palabras clave coincidentes: {overlap}")
                
            # Mejorar puntuación basada en especialidad
            if "specialty" in agent:
                specialty_words = agent["specialty"].lower().split()
                overlap_spec = set(task_keywords) & set(specialty_words)
                score += len(overlap_spec) * 0.15
                if overlap_spec:
                    reasons.append(f"Especialidad coincidente: {overlap_spec}")
                    
            if score > best_match["confidence"]:
                best_match = {
                    "id": agent["id"],
                    "confidence": min(score, 1.0),
                    "reason": "; ".join(reasons) if reasons else "Coincidencia por capacidades"
                }
                
        return best_match

    def _evaluar_con_simbolico(self, task: Task) -> Optional[RouteDecision]:
        """Usar razonamiento neurosimbólico para mejorar decisión de enrutamiento"""
        if not self.reasoning_engine or not REASONING_AVAILABLE:
            return None
            
        # Usar motor simbólico para validar consistencia de la tarea
        try:
            # Verificar si hay dependencias cíclicas (usando NetworkX)
            graph = GraphAnalyzer()
            for dep in task.dependencies:
                graph.add_nodes([task.id, dep])
                graph.add_edges([(dep, task.id)])
                
            if graph.detect_cycles():
                return RouteDecision(
                    agent="orchestrator",
                    confidence=0.9,
                    reason="Detección de dependencias cíclicas - requiere intervención del orquestador",
                    constraints_applied=["dependencia_ciclica"]
                )
                
            return None  # Si no se encuentran problemas, usar lógica normal de enrutamiento
            
        except Exception as e:
            # En caso de error en razonamiento simbólico, retornar a lógica normal
            return None

    def verify_task_result(self, task: Task, result: Any) -> Dict:
        """Verificar el resultado de una tarea ejecutada"""
        verification = {
            "status": "verified",
            "confidence": 0.8,
            "details": [],
            "recommendations": []
        }
        
        # Verificación básica: ¿el resultado está presente?
        if result is None:
            verification["status"] = "failed"
            verification["confidence"] = 0.1
            verification["details"].append("No se produjo resultado")
            return verification
            
        # Verificación específica según tipo de tarea
        if task.type == "implementation":
            # Verificar que existan pruebas
            if isinstance(result, dict) and result.get("tests_passed"):
                verification["confidence"] = 0.9
                verification["details"].append("Pruebas pasaron correctamente")
            elif "tests failed" in str(result).lower():
                verification["status"] = "needs_review"
                verification["confidence"] = 0.3
                verification["details"].append("Algunas pruebas fallaron")
                
        elif task.type == "research":
            # Verificar calidad de fuentes
            if isinstance(result, dict) and result.get("sources_verified"):
                verification["confidence"] = 0.85
                verification["details"].append("Fuentes verificadas")
                
        elif task.type == "qa":
            # Verificar evidencia de testing
            if isinstance(result, dict) and result.get("smoke_test_passed"):
                verification["confidence"] = 0.95
                verification["details"].append("Test de humo pasado")
                
        return verification

    def generate_task_report(self, tasks: List[Task]) -> Dict:
        """Generar reporte completo del sistema de tareas"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(tasks),
            "status_distribution": {},
            "agent_assignments": {},
            "dependencies": {},
            "issues": []
        }
        
        # Distribución de estados
        for status in TaskStatus:
            count = len([t for t in tasks if t.status == status])
            report["status_distribution"][status.value] = count
            
        # Asignaciones por agente
        for task in tasks:
            if task.assigned_agent:
                if task.assigned_agent not in report["agent_assignments"]:
                    report["agent_assignments"][task.assigned_agent] = 0
                report["agent_assignments"][task.assigned_agent] += 1
                
        # Identificar problemas
        blocked_tasks = [t for t in tasks if t.status == TaskStatus.BLOCKED]
        for task in blocked_tasks:
            report["issues"].append({
                "task_id": task.id,
                "issue": "Bloqueada",
                "description": task.description,
                "reason": task.metadata.get("block_reason", "Desconocido")
            })
            
        # Detectar ciclos en dependencias usando razonamiento simbólico
        if REASONING_AVAILABLE:
            try:
                graph = GraphAnalyzer()
                for task in tasks:
                    graph.add_nodes([task.id])  # Añadir nodo
                    for dep in task.dependencies:
                        if dep in [t.id for t in tasks]:
                            graph.add_edges([(dep, task.id)])
                            
                cycles = graph.detect_cycles()
                if cycles:
                    report["issues"].append({
                        "type": "dependency_cycle",
                        "details": f"Ciclos detectados en dependencias: {cycles}"
                    })
            except Exception:
                pass
                
        return report


# Función principal de demostración
def main():
    """Demostrar el funcionamiento del sistema de enrutamiento"""
    print("=== Sistema de Enrutamiento de Tareas ===\n")
    
    # Crear enrutador
    router = TaskRouter()
    
    # Objetivo de prueba
    objetivo = "Implementar un sistema de autenticación seguro para el swarm"
    
    print(f"Objetivo: {objetivo}\n")
    
    # Descomponer objetivo en tareas
    tasks = router.decompose_objective(objetivo)
    print(f"Tareas generadas: {len(tasks)}\n")
    
    # Mostrar tareas
    for task in tasks:
        print(f"  - {task.id}: {task.description[:60]}... (tipo: {task.type}, prioridad: {task.priority})")
    
    # Enrutar tareas
    print("\n--- Enrutamiento de tareas ---")
    for task in tasks:
        decision = router.route_task(task)
        task.assigned_agent = decision.agent
        task.status = TaskStatus.IN_PROGRESS
        print(f"  {task.id} -> {decision.agent} (confianza: {decision.confidence:.2f})")
        print(f"    Razón: {decision.reason}")
    
    # Simular resultados
    print("\n--- Verificación de resultados ---")
    for task in tasks:
        # Simular resultado
        if task.type == "implementation":
            result = {"tests_passed": True, "code": "..." }
        elif task.type == "qa":
            result = {"smoke_test_passed": True}
        elif task.type == "research":
            result = {"sources_verified": True}
        else:
            result = {"completed": True}
            
        verification = router.verify_task_result(task, result)
        task.status = TaskStatus.COMPLETED if verification["status"] == "verified" else TaskStatus.FAILED
        print(f"  {task.id} -> {verification['status']} (confianza: {verification['confidence']:.2f})")
        for detail in verification["details"]:
            print(f"    - {detail}")
    
    # Generar reporte
    print("\n--- Reporte Final ---")
    report = router.generate_task_report(tasks)
    print(json.dumps(report, indent=2))
    
    print("\n✅ Demostración completada")


if __name__ == "__main__":
    main()