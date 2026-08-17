"""Módulo de integración del razonamiento neurosimbólico con Hermes

Este módulo conecta el motor de razonamiento neurosimbólico con el ecosistema de Hermes,
permitiendo que la capacidad funcione como parte integral del flujo de trabajo normal
sin requerir activación manual.
"""

from .networkx_wrapper import GraphAnalyzer
from .pydatalog_integration import SymbolicEngine
from .z3_solver_integration import ConstraintSolver
from .task_router import NeuroSymbolicEngine as TaskRouterEngine  # Renombrar para evitar conflicto

class HermesNeurosymbolicIntegrator:
    """Integrador completo de razonamiento neurosimbólico para Hermes"""
    
    def __init__(self, workspace_path: str = "/home/fernando/ai-ecosystem"):
        self.workspace_path = workspace_path
        self.graph_analyzer = GraphAnalyzer()
        self.symbolic_engine = SymbolicEngine()
        self.constraint_solver = ConstraintSolver()
        self.neuro_engine = TaskRouterEngine()
        self.neuron_symbolic_engine = NeuroSymbolicEngine()
        
        # Configuración de activación automática
        self.auto_trigger_enabled = True
        self.auto_trigger_threshold = 3  # Número mínimo de palabras clave para activar
        
    def analyze_and_activate(self, task_context: Dict) -> Dict:
        """
        Analiza la tarea y activa razonamiento neurosimbólico si es beneficioso
        Devuelve información para que Hermes decida cómo proceder
        """
        # 1. Analizar contexto y determinar necesidad de razonamiento
        need_symbolic = self._analyze_for_symbolic_reasoning(task_context)
        
        # 2. Evaluar si los motores están disponibles
        engine_available = REASONING_AVAILABLE
        
        # 3. Determinar modo de activación
        activation_mode = "manual" if not self.auto_trigger_enabled else "auto"
        
        return {
            "needs_symbolic_reasoning": need_symbolic,
            "engine_available": engine_available,
            "activation_mode": activation_mode,
            "analysis": {
                "keywords_detected": self._count_keywords(task_context),
                "structural_patterns": self._detect_structural_patterns(task_context),
                "task_complexity": self._assess_complexity(task_context)
            }
        }
        
    def _analyze_for_symbolic_reasoning(self, context: Dict) -> bool:
        """Analiza si se requiere razonamiento simbólico basado en el contexto"""
        if not REASONING_AVAILABLE:
            return False
            
        # Contar palabras clave que indican necesidad de razonamiento formal
        keywords = {
            'dependency': 1,
            'constraint': 2,
            'conflict': 2,
            'optimization': 2,
            'validation': 2,
            'graph': 1,
            'relation': 1,
            'dependency': 1,
            'sequence': 1,
            'order': 1,
            'compatibility': 1,
            'incompatibility': 1,
            'validation': 1,
            'verification': 1,
            'dependency': 1
        }
        
        task_text = str(context.get('description', '')).lower()
        keyword_count = 0
        for keyword, weight in keywords.items():
            if keyword in task_text:
                score += weight
                
        # Activar razonamiento si se superan umbrales
        return analysis["keyword_count"] >= self.auto_trigger_threshold
        
    def _analyze_for_symbolic_reasoning(self, context: Dict) -> bool:
        """Analiza si se requiere razonamiento formal basado en el contexto"""
        if not REASONING_AVAILABLE:
            return False
            
        # Contar palabras clave que indican necesidad de razonamiento formal
        keywords = {
            'dependency': 1,
            'constraint': 2,
            'conflict': 2,
            'optimization': 2,
            'validation': 2,
            'graph': 1,
            'relation': 1,
            'cycle': 1,
            'topology': 1,
            'dependency': 1,
            'sequence': 1,
            'order': 1,
            'structure': 1,
            'system': 1
        }
        
        task_text = str(context.get('description', '')).lower()
        keyword_count = 0
        
        for keyword, weight in keywords.items():
            if keyword in task_text:
                keyword_count += weight
                
        return keyword_count >= 3  # Umbral mínimo para activar razonamiento
        
    def _count_keywords(self, context: Dict) -> int:
        """Cuenta palabras clave relevantes en la descripción de la tarea"""
        keywords = [
            'dependency', 'constraint', 'conflict', 'optimization',
            'validation', 'graph', 'relation', 'cycle', 'topology',
            'dependency', 'sequence', 'order', 'structure', 'system'
        ]
        
        context_text = str(context.get('description', '')).lower()
        return sum(1 for kw in keywords if kw in task_text)
        
    def _detect_structural_patterns(self, context: Dict) -> List[str]:
        """Detecta patrones estructurales que indican necesidad de razonamiento"""
        patterns = []
        context_text = str(context.get('description', '')).lower()
        
        if 'graph' in context_text and 'path' in context_text:
            patterns.append('graph_path_analysis')
        if 'dependency' in context_text and 'cycle' in context_text:
            patterns.append('dependency_cycle')
        if 'sequence' in context_text and 'condition' in context_text:
            patterns.append('conditional_sequence')
        if 'if' in context_text and 'then' in context_text:
            patterns.append('conditional_logic')
        if 'if' in context_text and 'then' not in context_text:
            patterns.append('conditional_without_then')
            
        return patterns
        
    def _assess_complexity(self, context: Dict) -> str:
        """Evalúa la complejidad de la tarea para determinar nivel de razonamiento"""
        desc = str(context.get('description', '')).lower()
        
        # Criterios de complejidad
        if any(kw in desc_lower for kw in ['graph', 'network', 'structure', 'topology']):
            return 'graph'
        elif any(kw in desc_lower for kw in ['constraint', 'restriction', 'limit', 'bound']):
            return 'constraint'
        elif any(kw in desc_lower for kw in ['dependency', 'sequence', 'chain']):
            return 'dependency'
        elif any(kw in desc_lower for kw in ['rule', 'rule-based', 'rule-engine']):
            return 'rule-based'
        elif any(kw in desc_lower for kw in ['validate', 'verify', 'validate', 'check', 'verify']):
            return 'validation'
        else:
            return 'simple'
            
    def process_task_with_reasoning(self, task_description: str, context: Dict) -> Dict:
        """
        Procesar una tarea con razonamiento neurosimbólico
        - Detecta si es necesario el razonamiento
        - Elige el motor apropiado
        - Devuelve resultados verificables
        """
        # 1. Análisis inicial
        analysis = self._analyze_and_activate(task_description, context)
        
        if not analysis['needs_symbolic_reasoning']:
            return {
                "status": "success",
                "reasoning_used": False,
                "message": "Tarea procesada sin razonamiento simbólico",
                "steps": ["Análisis contextual", "Validación de requisitos"],
                "results": {}
            }
            
        # 2. Activar razonamiento si es necesario
        if not self.reasoning_engine:
            return {
                "status": "error",
                "reasoning_used": False,
                "message": "Motor de razonamiento no disponible",
                "steps": ["Verificación de disponibilidad de motor"],
                "error": "Motor de razonamiento no disponible"
            }
            
        # 2. Procesar con el motor de razonamiento
        if self.reasoning_engine:
            result = self.reasoning_engine.process_task(task_description, context)
            return {
                "status": "success",
                "reasoning_used": True,
                "analysis": analysis,
                "steps": ["Identificación de necesidad", "Activación del motor", "Procesamiento simbólico", "Generación de resultados"],
                "results": processing_result
            }
            
        return {
            "status": "success",
            "reasoning_used": False,
            "message": "Tarea procesada sin razonamiento simbólico",
            "steps": ["Análisis contextual", "Validación de requisitos"],
            "results": {}
        }
        
    def integrate_with_hermes_workflow(self, task_context: Dict) -> Dict:
        """
        Integra con el flujo de trabajo de Hermes para procesar una tarea
        Devuelve información para que Hermes continúe con su flujo normal
        """
        # 1. Analizar necesidad de razonamiento
        analysis = self.analyze_and_activate(task_context)
        
        # 2. Si se requiere razonamiento y está disponible
        if analysis['needs_symbolic_reasoning'] and self.reasoning_engine:
            # 2a. Procesar con razonamiento neurosimbólico
            symbolic_result = self._process_with_symbolic_reasoning(task_description, context)
            
            # 3. Integrar resultado en el flujo de Hermes
            return {
                "status": "processing",
                "reasoning_used": True,
                "analysis": analysis,
                "steps": ["Análisis de contexto", "Activación de razonamiento", "Procesamiento simbólico"],
                "results": symbolic_result.get("results", {}),
                "next_steps": ["Incorporar resultados al razonamiento de Hermes", "Continuar con flujo normal"]
            }
        else:
            # 3. Procesar sin razonamiento simbólico
            return {
                "status": "success",
                "reasoning_used": False,
                "message": "Razonamiento no requerido para esta tarea",
                "steps": ["Análisis de contexto", "Validación de requisitos"],
                "results": {}
            }
            
    def _process_with_symbolic_reasoning(self, task_description: str, context: Dict) -> Dict:
        """Procesar la tarea usando el motor de razonamiento neurosimbólico"""
        # 1. Construir grafo de dependencias
        graph = GraphAnalyzer()
        for item in context.get('dependencies', []):
            graph.add_nodes([task_description, item])
        if 'start' in context:
            graph.add_nodes(['start', task_description])
            graph.add_edges([('start', task_description)])
            
        # 2. Aplicar reglas lógicas si es necesario
        symbolic_result = {}
        if self.symbolic_engine:
            # Ejemplo de regla para validar consistencia
            rules = []
            if 'conflict' in task_description.lower():
                rules.append('not (A and not B)')
                rules.append('not (not A and B)')
                rules.append('not (A and not B)')
                rules.append('not (not A and not B)')
                
            if rules:
                engine = SymbolicEngine()
                for fact in context.get('facts', []):
                    engine.add_fact(fact)
                for rule in rules:
                    engine.define_rule(rule.split('=')[0], rule.split('=')[1])
                    
                # Simular consulta
                result = engine.query('valid')
                symbolic_result = {"valid": True} if result else {"valid": False}
                symbolic_result['constraints'] = context.get('constraints', [])
                symbolic_result['facts'] = context.get('facts', [])
                return symbolic_result
                
        return {"status": "processing", "reasoning_used": True, "steps": ["Análisis", "Procesamiento simbólico", "Validación"]}

    def analyze_task_context(self, task_context: Dict) -> Dict:
        """Analiza el contexto de la tarea para decisiones de razonamiento"""
        return {
            "needs_symbolic_reasoning": self.analyze_and_activate(task_context),
            "engine_available": REASONING_AVAILABLE,
            "analysis": {
                "keywords_detected": self._count_keywords(task_context),
                "structural_patterns": self._detect_structural_patterns(task_context),
                "task_complexity": self._assess_complexity(task_context),
                "recommended_engine": "z3" if "constraint" in str(context).lower() else "networkx" if "graph" in str(context).lower() else "pydatalog"
            }
        }

    def _count_keywords(self, context: Dict) -> int:
        """Cuenta palabras clave en la descripción de la tarea"""
        keywords = [
            'dependency', 'constraint', 'conflict', 'optimization',
            'validation', 'graph', 'relation', 'cycle', 'topology',
            'dependency', 'sequence', 'order', 'structure', 'system'
        ]
        
        text = str(context.get('description', '')).lower()
        return sum(1 for kw in keywords if kw in text)

    def _detect_structural_patterns(self, context: Dict) -> List[str]:
        """Detecta patrones estructurales en la descripción de la tarea"""
        patterns = []
        context_text = str(context.get('description', '')).lower()
        
        if 'graph' in context_text and 'path' in context_text:
            patterns.append('graph_path_analysis')
        if 'cycle' in context_text and 'dependency' in context_text:
            patterns.append('cycle_detection')
        if 'sequence' in context_text and 'condition' in context_text:
            patterns.append('conditional_flow')
        if 'if' in context_text and 'then' in context_text:
            patterns.append('if_then_structure')
        if 'if' in context_text and 'else' in context_text:
            patterns.append('conditional_branching')
            
        return patterns

    def analyze_task_complexity(self, task_description: str, context: Dict) -> str:
        """Evalúa la complejidad de la tarea para determinar nivel de razonamiento"""
        desc = task_description.lower()
        
        if any(kw in desc for kw in ['graph', 'network', 'structure', 'topology', 'nodes', 'edges']):
            return 'graph'
        elif any(kw in desc for kw in ['constraint', 'restriction', 'limit', 'bound', 'capacity']):
            return 'constraint'
        elif any(kw in desc_lower for kw in ['dependency', 'sequence', 'chain', 'dependency']):
            return 'dependency'
        elif any(kw in desc_lower for kw in ['rule', 'rule-based', 'rule-engine', 'policy']):
            return 'rule-based'
        elif any(kw in desc_lower for kw in ['validate', 'verify', 'check', 'validate', 'confirm']):
            return 'validation'
        else:
            return 'simple'
            
    def get_automatic_activation_status(self) -> Dict:
        """Obtiene el estado actual de activación automática"""
        return {
            "enabled": self.auto_trigger_enabled,
            "threshold": self.auto_trigger_threshold,
            "last_analysis": self._analyze_and_activate({}),
            "auto_trigger_count": self.reasoning_stats.get("auto_trigger", 0),
            "manual_trigger_count": self.reasoning_stats.get("manual_trigger", 0)
        }