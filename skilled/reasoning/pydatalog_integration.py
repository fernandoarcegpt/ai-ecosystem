"""
PyDatalog Integration para razonamiento basado en reglas - CORREGIDO

Reparado para usar PyDatalog REAL con inferencia real.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
import re

# Import PyDatalog module
try:
    import pyDatalog.pyDatalog as pdl  # Modulo principal de PyDatalog
    PYDATALOG_AVAILABLE = True
except ImportError as e:
    PYDATALOG_AVAILABLE = False
    logging.warning(f"PyDatalog not available: {e}")

logger = logging.getLogger(__name__)


@dataclass
class LogicInferenceResult:
    """Resultado de inferencia lógica real"""
    success: bool = False
    derived_facts: List[Dict[str, Any]] = field(default_factory=list)
    bindings: List[Dict[str, str]] = field(default_factory=list)
    error: Optional[str] = None
    inference_complete: bool = False


class PyDatalogEngine:
    """
    Motor de inferencia lógica usando PyDatalog REAL.
    
    Cada instancia limpia el estado global de PyDatalog al crear,
    garantizando aislamiento de estado entre ejecuciones.
    """
    
    def __init__(self):
        if not PYDATALOG_AVAILABLE:
            raise RuntimeError("PyDatalog not installed. Run: pip install pyDatalog")
        
        # Limpiar estado previo de PyDatalog GLOBAL
        # Esto garantiza aislamiento entre ejecuciones
        pdl.clear()
        self.facts: Dict[str, List[Tuple]] = {}
        self.rules: Dict[str, List] = {}
        self._predicates_declared: set = set()
    
    def _declare_predicate(self, predicate_name: str):
        """Declarar predicado en PyDatalog"""
        if predicate_name not in self._predicates_declared:
            pdl.create_terms(predicate_name)
            self._predicates_declared.add(predicate_name)
    
    def add_fact(self, predicate: str, *args) -> None:
        """
        Añadir hecho a la base de conocimiento PyDatalog.
        
        Ejemplo:
        engine.add_fact("parent", "Alice", "Bob")
        → parent('Alice', 'Bob')
        """
        self._declare_predicate(predicate)
        
        # Almacenar localmente
        if predicate not in self.facts:
            self.facts[predicate] = []
        self.facts[predicate].append(args)
        
        # Añadir a PyDatalog
        try:
            # PyDatalog uses syntax: assert_fact(predicate_name, arg1, arg2, ...)
            pdl.assert_fact(predicate, *args)
        except Exception as e:
            logger.warning(f"Failed to add fact to PyDatalog: {e}")
    
    def define_rule(self, rule_name: str, head: str, body: str) -> None:
        """
        Definir regla lógica usando PyDatalog REAL.
        
        Ejemplo:
        engine.define_rule("ancestor_rule", "ancestor(X, Y)", "parent(X, Y)")
        
        Args:
            rule_name: Identificador de la regla
            head: Cabeza de la regla (ej: "ancestor(X, Y)")
            body: Cuerpo de la regla (ej: "parent(X, Y)")
        """
        if rule_name not in self.rules:
            self.rules[rule_name] = []
        
        self.rules[rule_name].append({"head": head, "body": body})
        
        try:
            # Extraer y crear variables
            all_vars = self._extract_variables(head + " " + body)
            for var in all_vars:
                pdl.create_terms(var)
            
            # Declarar predicados
            head_pred = head.split('(')[0] if '(' in head else head
            body_pred = body.split('(')[0] if '(' in body else body
            
            self._declare_predicate(head_pred)
            self._declare_predicate(body_pred)
            
            # La regla en PyDatalog: head <= body
            rule_expr = f"{head} <= {body}"
            pdl.load(rule_expr)
            
        except Exception as e:
            logger.error(f"Failed to define rule in PyDatalog: {e}")
            raise
    
    def _extract_variables(self, text: str) -> List[str]:
        """Extraer variables (palabras que empiezan con mayúscula)"""
        return list(dict.fromkeys(re.findall(r'\b[A-Z]\w*\b', text)))
    
    def query(self, query: str) -> LogicInferenceResult:
        """
        Ejecutar consulta real en PyDatalog y devolver resultados reales.
        
        Args:
            query: Consulta en formato PyDatalog (ej: "ancestor(X, Y)")
            
        Returns:
            LogicInferenceResult con facts derivados y bindings reales
        """
        result = LogicInferenceResult()
        
        try:
            # Extraer variables
            variables = self._extract_variables(query)
            for var in variables:
                pdl.create_terms(var)
            
            if variables:
                # Consulta con variables: "ancestor(X, Y)"
                answer = pdl.ask(query)
                
                if answer is not None:
                    # El objeto Answer de PyDatalog tiene attribute .answers que es una lista de tuples
                    solutions_list = list(answer.answers)
                    
                    for solution in solutions_list:
                        binding = {}
                        for i, var in enumerate(variables):
                            if i < len(solution):
                                binding[var] = str(solution[i])
                        result.bindings.append(binding)
                        
                        # Generar derived_facts
                        derived = {
                            "predicate": query.split('(')[0] if '(' in query else query,
                            "args": [binding.get(var, "") for var in variables],
                            "binding": binding
                        }
                        result.derived_facts.append(derived)
                    
                    result.success = True
                    result.inference_complete = True
                else:
                    result.success = True
                    result.inference_complete = True
            else:
                # Consulta booleana
                answer = pdl.ask(query)
                result.success = True
                result.inference_complete = True
                if answer is not None and answer.answers:
                    result.bindings.append({})
                    result.derived_facts.append({
                        "predicate": query.split('(')[0] if '(' in query else query,
                        "args": []
                    })
                
        except Exception as e:
            result.success = False
            result.error = str(e)
            logger.error(f"PyDatalog query failed: {e}")
        
        return result
    
    def clear_all(self):
        """Limpiar todos los hechos y reglas"""
        pdl.clear()
        self.facts.clear()
        self.rules.clear()
        self._predicates_declared.clear()
    
    def get_fact_count(self) -> int:
        return sum(len(v) for v in self.facts.values())
    
    def get_rule_count(self) -> int:
        return sum(len(v) for v in self.rules.values())


class SymbolicEngine:
    """
    Wrapper de alto nivel que proporciona interfaz compatible con el código existente
    pero usa PyDatalog REAL por debajo.
    """
    
    def __init__(self):
        self.engine = PyDatalogEngine()
        self.facts = self.engine.facts
        self.rules = self.engine.rules
    
    def add_fact(self, predicate: str, *args) -> None:
        self.engine.add_fact(predicate, *args)
    
    def define_rule(self, rule_name: str, head: str, body: str) -> None:
        self.engine.define_rule(rule_name, head, body)
    
    def query(self, query: str, bindings: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Método compatible con la interfaz anterior"""
        result = self.engine.query(query)
        bindings_list = result.bindings
        
        if bindings:
            # Filtrar resultados con bindings
            filtered_bindings = []
            for binding in bindings_list:
                match = True
                for key, value in bindings.items():
                    if key in binding and binding[key] != value:
                        match = False
                        break
                if match:
                    filtered_bindings.append(binding)
            return filtered_bindings
        else:
            return bindings_list
    
    def clear_all(self):
        self.engine.clear_all()
    
    def get_fact_count(self) -> int:
        return self.engine.get_fact_count()
    
    def get_rule_count(self) -> int:
        return self.engine.get_rule_count()