"""
Z3 Solver Integration para resolución de restricciones - CORREGIDO

Reparado para:
1. Crear variables reales Z3
2. Formalizar restricciones correctamente
3. Devolver resultados sat/unsat reales
"""

from z3 import Solver, Int, Bool, And, Or, Not, Implies, sat, unsat, unknown, ModelRef
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class ConstraintStatus(Enum):
    """Estado de restricción formalizada"""
    SATISFIABLE = "satisfiable"
    UNSATISFIABLE = "unsatisfiable"
    UNKNOWN = "unknown"
    ERROR = "error"


class ConstraintFormalizationError(Exception):
    """Error cuando una restricción no puede formalizarse correctamente"""
    pass


class ConstraintSolver:
    """
    Solver Z3 con aislamiento de estado por instancia.
    
    Cada instancia crea su propio solver - NO comparte estado.
    """
    
    def __init__(self):
        self.solver = Solver()
        self.variables: Dict[str, Any] = {}
        self.constraints_applied: List[str] = []
    
    def add_integer_variable(self, name: str, min_val: Optional[int] = None, max_val: Optional[int] = None) -> Int:
        """Crear variable entera Z3 con límites opcionales"""
        var = Int(name)
        self.variables[name] = var
        
        if min_val is not None:
            self.solver.add(var >= min_val)
        if max_val is not None:
            self.solver.add(var <= max_val)
            
        return var
    
    def add_boolean_variable(self, name: str) -> Bool:
        """Crear variable booleana Z3"""
        var = Bool(name)
        self.variables[name] = var
        return var
    
    def add_constraint_direct(self, z3_expr) -> bool:
        """Agregar restricción Z3 directamente (expresión ya construida)"""
        try:
            self.solver.add(z3_expr)
            self.constraints_applied.append(str(z3_expr))
            return True
        except Exception as e:
            logger.warning(f"Z3 constraint addition failed: {e}")
            return False

    def add_constraint(self, expression: str) -> bool:
        """Formaliza un subconjunto explícito de expresiones aritméticas.

        Se mantiene deliberadamente pequeño y no usa ``eval``: comparaciones
        de una variable con un entero y sumas de variables igualadas a un
        entero.
        """
        expression = expression.strip()
        comparison = re.fullmatch(
            r"([A-Za-z_]\w*)\s*(>=|<=|>|<|==|=)\s*(-?\d+)",
            expression,
        )
        if comparison:
            name, operator, raw_value = comparison.groups()
            if name not in self.variables:
                return False
            value = int(raw_value)
            variable = self.variables[name]
            operators = {
                ">": variable > value,
                "<": variable < value,
                ">=": variable >= value,
                "<=": variable <= value,
                "=": variable == value,
                "==": variable == value,
            }
            return self.add_constraint_direct(operators[operator])

        sum_match = re.fullmatch(
            r"([A-Za-z_]\w*(?:\s*\+\s*[A-Za-z_]\w*)+)\s*=\s*(-?\d+)",
            expression,
        )
        if sum_match:
            names = [name.strip() for name in sum_match.group(1).split("+")]
            return self.constraint_sum_eq(names, int(sum_match.group(2)))

        return False
    
    def constraint_gt(self, var_name: str, value: int) -> bool:
        """Restricción: variable > value"""
        if var_name not in self.variables:
            return False
        self.solver.add(self.variables[var_name] > value)
        self.constraints_applied.append(f"{var_name} > {value}")
        return True
    
    def constraint_lt(self, var_name: str, value: int) -> bool:
        """Restricción: variable < value"""
        if var_name not in self.variables:
            return False
        self.solver.add(self.variables[var_name] < value)
        self.constraints_applied.append(f"{var_name} < {value}")
        return True
    
    def constraint_eq(self, var_name: str, value: int) -> bool:
        """Restricción: variable = value"""
        if var_name not in self.variables:
            return False
        self.solver.add(self.variables[var_name] == value)
        self.constraints_applied.append(f"{var_name} = {value}")
        return True
    
    def constraint_sum_eq(self, var_names: List[str], total: int) -> bool:
        """Restricción: suma(variables) = total"""
        try:
            z3_vars = [self.variables[v] for v in var_names if v in self.variables]
            if len(z3_vars) != len(var_names):
                return False
            self.solver.add(sum(z3_vars) == total)
            self.constraints_applied.append(f"sum({', '.join(var_names)}) = {total}")
            return True
        except Exception as e:
            logger.warning(f"Sum constraint failed: {e}")
            return False
    
    def constraint_and_eq(self, var1: str, var2: str) -> bool:
        """Restricción: var1 = var2"""
        if var1 not in self.variables or var2 not in self.variables:
            return False
        self.solver.add(self.variables[var1] == self.variables[var2])
        self.constraints_applied.append(f"{var1} = {var2}")
        return True
    
    def solve(self) -> Dict[str, Any]:
        """
        Resolver el sistema de restricciones usando Z3 real.
        
        Returns:
            Dict con status, solution_values, constraints aplicadas
        """
        result = {
            "status": "unknown",
            "solution_values": {},
            "formalized_constraints": list(self.constraints_applied),
            "variables_count": len(self.variables)
        }
        
        try:
            if len(self.variables) == 0:
                result["status"] = "skipped"  # No hay variables para resolver
                return result
            
            status = self.solver.check()
            
            if status == sat:
                model = self.solver.model()
                result["status"] = "satisfiable"
                result["solution_values"] = {}
                for var_name, var in self.variables.items():
                    val = model[var]
                    if val is not None:
                        # Convertir a entero Python
                        result["solution_values"][var_name] = val.as_long()
                    else:
                        result["solution_values"][var_name] = None
                result["solution"] = dict(result["solution_values"])
                        
            elif status == unsat:
                result["status"] = "unsatisfiable"
                
            else:
                result["status"] = "unknown"
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            logger.error(f"Z3 solve error: {e}")
            
        return result
    
    def reset(self):
        """Reiniciar el solver para nuevos problemas"""
        self.solver = Solver()
        self.variables = {}
        self.constraints_applied = []
    
    def get_conflict_info(self) -> List[str]:
        """Obtener información sobre conflictos"""
        return list(self.constraints_applied)
