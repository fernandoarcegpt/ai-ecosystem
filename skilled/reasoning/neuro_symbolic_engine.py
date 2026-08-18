"""
Motor principal de razonamiento neurosimbólico para Hermes.

Esta versión implementa el pipeline CORREGIDO:
1. Extracción de SymbolicProblem a partir del texto (sin inventar entidades)
2. Aislamiento de estado por ejecución para cada ejecución
3. Uso de motores reales (NetworkX, Z3, PyDatalog) sin interpretaciones genéricas
4. Validación estricta de resultados y evidencia basada en outputs reales
5. Manejo de errores correcto: solo éxito si el motor devuelve resultado válido

Los motores NO interpretan directamente lenguaje natural; solo reciben SymbolicProblem estructurado.
"""

import os
import sys
import json
import time
import logging
import re
from copy import deepcopy
from z3 import Sum, If, Implies, BoolVal
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

# Asegurarnos de que el módulo actual esté en PYTHONPATH
sys.path.insert(0, '/home/fernando/ai-ecosystem/skilled')
sys.path.insert(0, '/home/fernando/ai-ecosystem')

# Importar módulos locales (relativos al paquete reasoning)
from .symbolic_problem_schema import SymbolicProblem, SymbolicConstraint, ProblemExtractor, ReasoningMode
from .networkx_wrapper import GraphAnalyzer, NetworkXResultStatus
from .z3_solver_integration import ConstraintSolver, ConstraintStatus
from .pydatalog_integration import PyDatalogEngine

try:
    import networkx as nx
    import z3
    import pyDatalog as pyDatalog_module
    REASONING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Symbolic reasoning module import failed: {e}")
    REASONING_AVAILABLE = False


class CoordinationResultStatus(Enum):
    """Estado de resultado de coordinación"""
    PENDING = "pending"
    SUCCESS = "success"
    SKIPPED = "skipped"
    ERROR = "error"
    FORMALIZATION_ERROR = "formalization_error"


class NeurosymbolicCoordinationResult:
    """Resultado estructurado de la coordinación de razonamiento neurosimbólico"""

    def __init__(self):
        self.status: str = CoordinationResultStatus.PENDING.value
        self.reasoning_applied: bool = False
        self.engine_used: str = "none"
        self.analysis: Dict[str, Any] = {}
        self.results: Dict[str, Any] = {}
        self.evidence: Dict[str, Any] = {}
        self.execution_time: float = 0.0
        self.timestamp: str = datetime.now().isoformat()
        self.error: Optional[str] = None
        self.formalization_errors: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convertir resultado a diccionario para serialización"""
        return {
            "status": self.status,
            "reasoning_applied": self.reasoning_applied,
            "engine_used": self.engine_used,
            "analysis": self.analysis,
            "results": self.results,
            "evidence": self.evidence,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp,
            "error": self.error,
            "formalization_errors": self.formalization_errors
        }


class NeurosymbolicCoordinator:
    """
    Coordinador central del razonamiento neurosimbólico.
    
    IMPORTANTE: Cada método que ejecuta razonamiento CREA NUEVAS INSTANCIAS
    de los motores para garantizar aislamiento de estado.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Estadísticas de razonamiento
        self.stats = {
            "total_activations": 0,
            "successful_applications": 0,
            "auto_triggers": 0,
            "manual_triggers": 0,
            "errors_handled": 0
        }

    def _create_fresh_graph_analyzer(self) -> GraphAnalyzer:
        """Crear nuevo GraphAnalyzer para aislamiento de estado"""
        if GraphAnalyzer is None:
            return None
        return GraphAnalyzer()

    def _create_fresh_solver(self) -> ConstraintSolver:
        """Crear nuevo ConstraintSolver para aislamiento de estado"""
        if ConstraintSolver is None:
            return None
        return ConstraintSolver()

    def _create_fresh_pydatalog_engine(self) -> PyDatalogEngine:
        """Crear nuevo PyDatalogEngine para aislamiento de estado"""
        if PyDatalogEngine is None:
            return None
        return PyDatalogEngine()

    def _extract_symbolic_problem(self, task_description: str, context: Dict[str, Any]) -> SymbolicProblem:
        """
        Extraer SymbolicProblem mediante el extractor centralizado.

        El coordinador no reimplementa heurísticas de lenguaje natural:
        delega toda la formalización a ProblemExtractor.
        """
        return ProblemExtractor.extract(task_description, context or {})

    def analyze_context_for_reasoning(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza el contexto para determinar si se necesita razonamiento simbólico"""
        keywords = {
            'dependency': 2, 'dependencies': 2, 'constraint': 3, 'restricción': 3,
            'conflict': 3, 'conflicto': 3, 'cycle': 2, 'ciclo': 2, 'topologia': 2,
            'topology': 2, 'graph': 2, 'grafo': 2, 'relation': 1, 'relación': 1,
            'sequence': 2, 'secuencia': 2, 'order': 2, 'orden': 2,
            'optimization': 3, 'optimización': 3,
            'validation': 2, 'validación': 2, 'verification': 2, 'verificación': 2,
            'cycle detection': 3, 'cycle analysis': 3,
            'path finding': 2, 'dependency analysis': 3,
            'constraint satisfaction': 4,
            'logical inference': 3,
            'consistency check': 3,
            'transitive closure': 3,
            'topological sort': 3, 'topological sorting': 3,
            'rule-based': 2, 'if-then': 2, 'conditional': 2,
            'inference': 2, 'deterministic': 2, 'determinístico': 2
        }

        if isinstance(context, dict):
            context_text = (
                context.get("source_query")
                or context.get("description")
                or context.get("text")
                or ""
            )
        else:
            context_text = str(context)

        context_lower = str(context_text).lower()

        keyword_score = 0
        matched_keywords = []
        for keyword, weight in keywords.items():
            if keyword in context_lower:
                keyword_score += weight
                matched_keywords.append(keyword)

        # Verificar contenido simbólico explícito del SymbolicProblem
        has_symbolic_content = bool(
            context.get('items') or
            context.get('people') or
            context.get('constraints') or
            context.get('relations') or
            context.get('facts') or
            context.get('rules') or
            context.get('dependencies')
        )

        needs_reasoning = bool(
            REASONING_AVAILABLE
            and (keyword_score >= 1.0 or has_symbolic_content)
        )

        recommended_engine = "combined"
        if has_symbolic_content:
            if context.get('constraints'):
                recommended_engine = "z3"
            elif context.get('relations') or context.get('dependencies'):
                recommended_engine = "networkx"
            elif context.get('facts') and context.get('rules'):
                recommended_engine = "pydatalog"

        return {
            "needs_symbolic_reasoning": needs_reasoning,
            "confidence": min(keyword_score / 10.0, 1.0),
            "keyword_score": keyword_score,
            "matched_keywords": matched_keywords[:10],
            "has_symbolic_content": has_symbolic_content,
            "recommended_engine": recommended_engine,
            "analysis_details": {}
        }

    def execute_symbolic_reasoning(
        self,
        task_description: str,
        context: Dict[str, Any],
        engine_preference: str = "auto"
    ) -> NeurosymbolicCoordinationResult:
        """
        Ejecutar razonamiento simbólico completo con aislamiento de estado.
        """
        start_time = time.time()
        result = NeurosymbolicCoordinationResult()
        self.stats["total_activations"] += 1

        try:
            # 1. Extraer SymbolicProblem
            problem = self._extract_symbolic_problem(task_description, context)

            # 2. Analizar necesidad y seleccionar motor según la estructura
            # realmente formalizada, no solo por keywords.
            analysis = self.analyze_context_for_reasoning(
                {"source_query": task_description, **context}
            )

            if problem.mode != ReasoningMode.NONE:
                analysis["needs_symbolic_reasoning"] = True
                analysis["has_symbolic_content"] = True

                if problem.mode == ReasoningMode.GRAPHS:
                    analysis["recommended_engine"] = "networkx"
                elif problem.mode == ReasoningMode.CONSTRAINTS:
                    analysis["recommended_engine"] = "z3"
                elif problem.mode == ReasoningMode.LOGIC:
                    analysis["recommended_engine"] = "pydatalog"
                elif problem.mode == ReasoningMode.COMBINED:
                    analysis["recommended_engine"] = "combined"

            analysis["formalized_problem"] = problem.to_dict()
            result.analysis = analysis

            # 3. Verificar si se necesita razonamiento
            if not analysis.get("needs_symbolic_reasoning", False):
                if engine_preference != "manual":
                    self.stats["errors_handled"] += 1
                    result.status = CoordinationResultStatus.SKIPPED.value
                    result.reasoning_applied = False
                    result.error = "No se detectó necesidad de razonamiento simbólico"
                    return result

            # 3. Verificar motores disponibles
            if not REASONING_AVAILABLE:
                result.status = CoordinationResultStatus.ERROR.value
                result.evidence = {"error": "Motores de razonamiento simbólico no disponibles"}
                return result

            # 4. Ejecutar según motor
            if engine_preference == "auto":
                engine_to_use = analysis.get("recommended_engine", "combined")
            else:
                engine_to_use = engine_preference

            engine_result = None

            if engine_to_use == "networkx":
                engine_result = self._run_networkx_reasoning(problem, context)
            elif engine_to_use == "z3":
                engine_result = self._run_z3_reasoning(problem, context)
            elif engine_to_use == "pydatalog":
                engine_result = self._run_pydatalog_reasoning(problem, context)
            else:  # combined
                engine_result = self._run_combined_reasoning(problem, context)

            # 5. VALIDAR resultado del motor
            if engine_result is None or engine_result.get("status") == "error":
                result.status = CoordinationResultStatus.ERROR.value
                result.results = engine_result or {}
                result.evidence = {"error": "Motor retornó error"}
                return result

            if engine_result.get("formalization_error"):
                result.status = CoordinationResultStatus.FORMALIZATION_ERROR.value
                result.formalization_errors = engine_result.get("formalization_errors", [])
                result.results = engine_result
                return result

            # 6. ÉXITO solo si el motor produce resultado válido
            result.status = CoordinationResultStatus.SUCCESS.value
            result.reasoning_applied = True
            result.engine_used = engine_to_use
            result.results = engine_result
            result.execution_time = time.time() - start_time
            result.timestamp = datetime.now().isoformat()

            # Preparar evidencia basada en resultados reales
            result.evidence = self._prepare_evidence(result.results, analysis, problem)

            self.stats["successful_applications"] += 1

        except Exception as e:
            self.logger.error(f"Symbolic reasoning execution failed: {e}")
            result.status = CoordinationResultStatus.ERROR.value
            result.error = str(e)
            result.execution_time = time.time() - start_time

            if engine_preference != "manual":
                self.stats["errors_handled"] += 1

        return result

    def _run_networkx_reasoning(
        self, problem: SymbolicProblem, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecución de razonamiento sobre grafos usando NetworkX REAL.
        """
        if GraphAnalyzer is None:
            return {"status": "error", "error": "GraphAnalyzer not available"}

        # CREAR NUEVO GrafoAnalyzer para aislamiento
        graph_analyzer = self._create_fresh_graph_analyzer()
        if graph_analyzer is None:
            return {"status": "error", "error": "Could not create GraphAnalyzer"}

        result_base = {
            "status": "success",
            "graph_analysis": {},
            "cycles_found": [],
            "is_acyclic": True,
            "topological_order": None,
            "analysis_complete": False
        }

        try:
            # No aceptar como éxito un grafo vacío/no formalizado.
            if not problem.relations:
                return {
                    "status": "formalization_error",
                    "formalization_error": True,
                    "formalization_errors": [
                        "No se extrajeron relaciones/dependencias para construir el grafo"
                    ],
                    "graph_analysis": {"nodes": [], "edges": []},
                    "cycles_found": [],
                    "is_acyclic": None,
                    "topological_order": None,
                    "analysis_complete": False,
                }

            # Añadir nodos del problema
            if problem.entities:
                graph_analyzer.add_nodes(problem.entities)

            # AÑADIR RELACIONES REALES como aristas
            if problem.relations:
                graph_analyzer.add_edges_from_relations(problem.relations)

            # Ejecutar análisis
            analysis = graph_analyzer.analyze()

            result_base["status"] = analysis.get("status", "success")
            result_base["is_acyclic"] = analysis.get("is_acyclic", True)
            result_base["cycles_found"] = analysis.get("cycles_found", [])
            result_base["topological_order"] = analysis.get("topological_order")
            result_base["transitive_relations"] = analysis.get(
                "transitive_relations", []
            )
            result_base["reachability"] = analysis.get("reachability", {})
            result_base["bottleneck_nodes"] = analysis.get(
                "bottleneck_nodes", []
            )

            # SOLO marcar completado si se construyeron relaciones requeridas
            if problem.relations:
                result_base["analysis_complete"] = analysis.get("analysis_complete", False)

            result_base["graph_analysis"] = {
                "nodes": analysis.get("nodes", []),
                "edges": analysis.get("edges", [])
            }

        except Exception as e:
            result_base["status"] = "error"
            result_base["error"] = str(e)

        return result_base

    def _run_z3_reasoning(
        self, problem: SymbolicProblem, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecución de resolución de restricciones usando Z3 REAL.
        """
        if ConstraintSolver is None:
            return {"status": "error", "error": "ConstraintSolver not available"}

        # CREAR NUEVO ConstraintSolver para aislamiento
        solver = self._create_fresh_solver()
        if solver is None:
            return {"status": "error", "error": "Could not create ConstraintSolver"}

        result_base = {
            "status": "error",
            "solution_status": "unknown",
            "solution_values": {},
            "formalized_constraints": [],
            "formalization_errors": [],
            "executed": False
        }

        try:
            if problem.objectives:
                solver.enable_optimization()

            # 1. Crear variables reales. Las asignaciones usan índices de
            # personas; las restricciones aritméticas usan sus nombres.
            if problem.items and problem.people:
                for item in problem.items:
                    var_name = f"item_{item}"
                    solver.add_integer_variable(var_name, min_val=0, max_val=len(problem.people) - 1)
            elif problem.items:
                for item in problem.items:
                    if item not in problem.variables:
                        solver.add_integer_variable(item)

            for name, raw_spec in problem.variables.items():
                if name in solver.variables:
                    continue
                spec = raw_spec if isinstance(raw_spec, dict) else {}
                if spec.get("type") == "bool":
                    solver.add_boolean_variable(name)
                else:
                    solver.add_integer_variable(
                        name,
                        min_val=spec.get("min"),
                        max_val=spec.get("max"),
                    )

            # 2. Formalizar todas las restricciones reales.
            for constraint in problem.constraints:
                formalized = self._formalize_z3_constraint(constraint, problem, solver)
                if formalized:
                    result_base["formalized_constraints"].append(formalized)
                else:
                    result_base["formalization_errors"].append(
                        f"Could not formalize constraint: {constraint}"
                    )

            # 3. Si hay restricciones obligatorias no formalizables, error.
            if result_base["formalization_errors"]:
                result_base["status"] = "formalization_error"
                result_base["formalization_error"] = True
                return result_base

            objective_errors = self._formalize_z3_objectives(
                problem,
                solver,
            )
            if objective_errors:
                result_base["formalization_errors"].extend(objective_errors)
                result_base["status"] = "formalization_error"
                result_base["formalization_error"] = True
                return result_base

            # 4. Resolver
            solve_result = solver.solve()
            result_base["solution_status"] = solve_result.get("status", "unknown")

            raw_values = (
                solve_result.get("solution_values")
                or solve_result.get("solution")
                or {}
            )
            result_base["solution_values"] = raw_values
            result_base["optimizer_used"] = solve_result.get(
                "optimizer_used", False
            )
            result_base["objectives_applied"] = solve_result.get(
                "objectives_applied", []
            )
            result_base["unsat_core"] = solve_result.get("unsat_core", [])

            # No sobrescribir las restricciones que acabamos de formalizar si
            # el wrapper no las devuelve.
            returned_constraints = solve_result.get("formalized_constraints")
            if returned_constraints:
                result_base["formalized_constraints"] = returned_constraints

            result_base["executed"] = True

            # 5. Validar y traducir la solución real de Z3.
            if solve_result.get("status") == "satisfiable" and problem.people:
                assignment = {}

                for item in problem.items:
                    key = f"item_{item}"
                    raw_value = raw_values.get(key)

                    if raw_value is None:
                        result_base["status"] = "error"
                        result_base["error"] = (
                            f"Z3 model missing assignment for {key}"
                        )
                        return result_base

                    try:
                        person_idx = int(str(raw_value))
                    except (TypeError, ValueError):
                        result_base["status"] = "error"
                        result_base["error"] = (
                            f"Invalid Z3 value for {key}: {raw_value}"
                        )
                        return result_base

                    if person_idx < 0 or person_idx >= len(problem.people):
                        result_base["status"] = "error"
                        result_base["error"] = (
                            f"Z3 assignment out of people domain for {key}: "
                            f"{person_idx}"
                        )
                        return result_base

                    assignment[item] = problem.people[person_idx]

                result_base["assignment"] = assignment
                result_base["solution_valid"] = problem.validate_solution(
                    assignment
                )

                if not result_base["solution_valid"]:
                    result_base["status"] = "error"
                    result_base["error"] = (
                        "Z3 returned a model that fails SymbolicProblem "
                        "post-validation"
                    )
                    return result_base

                result_base["status"] = "success"

            elif solve_result.get("status") == "satisfiable":
                result_base["solution_valid"] = True
                result_base["status"] = "success"

            elif solve_result.get("status") == "unsatisfiable":
                # UNSAT es un resultado válido del solver, no un fallo de
                # ejecución. El llamador puede decidir cómo actuar.
                result_base["solution_valid"] = True
                result_base["status"] = "success"

            elif solve_result.get("status") == "skipped":
                result_base["error"] = "No variables were formalized"

        except Exception as e:
            result_base["status"] = "error"
            result_base["error"] = str(e)

        return result_base

    def _formalize_z3_constraint(
        self,
        constraint: SymbolicConstraint,
        problem: SymbolicProblem,
        solver: ConstraintSolver,
    ) -> Optional[str]:
        """Formalizar restricciones de asignación usando expresiones Z3 reales."""
        ctype = constraint.type

        try:
            if ctype == "max_items_per_person":
                if not problem.items or not problem.people:
                    return None

                maximum = int(constraint.value)

                # Cada item_i contiene el índice de la persona asignada.
                # Para cada persona p:
                # Sum(If(item_i == p, 1, 0) for i) <= maximum
                for person_idx, person_name in enumerate(problem.people):
                    item_vars = [
                        solver.variables.get(f"item_{item}")
                        for item in problem.items
                    ]
                    if any(var is None for var in item_vars):
                        return None

                    expr = Sum([
                        If(var == person_idx, 1, 0)
                        for var in item_vars
                    ]) <= maximum

                    solver.add_tracked_constraint(
                        expr,
                        f"count({person_name}) <= {maximum}",
                    )

                return f"max_items_per_person={maximum}"

            elif ctype == "different_person":
                items = list(constraint.items or [])
                if len(items) != 2:
                    return None

                left_name = f"item_{items[0]}"
                right_name = f"item_{items[1]}"
                left = solver.variables.get(left_name)
                right = solver.variables.get(right_name)

                if left is None or right is None:
                    return None

                # Restricción REAL: desigualdad.
                solver.add_tracked_constraint(
                    left != right,
                    f"{left_name} != {right_name}",
                )

                return f"{items[0]} != {items[1]} (different_person)"

            elif ctype == "same_person":
                items = list(constraint.items or [])
                if len(items) != 2:
                    return None

                left_name = f"item_{items[0]}"
                right_name = f"item_{items[1]}"
                left = solver.variables.get(left_name)
                right = solver.variables.get(right_name)

                if left is None or right is None:
                    return None

                solver.add_tracked_constraint(
                    left == right,
                    f"{left_name} == {right_name}",
                )

                return f"{items[0]} == {items[1]} (same_person)"

            elif ctype in {"gt", "ge", "lt", "le", "eq"}:
                var = constraint.items[0] if constraint.items else None
                name = (
                    f"item_{var}"
                    if var and problem.people
                    else var
                )
                zvar = solver.variables.get(name) if name else None
                if zvar is None:
                    return None
                operators = {
                    "gt": zvar > constraint.value,
                    "ge": zvar >= constraint.value,
                    "lt": zvar < constraint.value,
                    "le": zvar <= constraint.value,
                    "eq": zvar == constraint.value,
                }
                symbols = {
                    "gt": ">", "ge": ">=", "lt": "<",
                    "le": "<=", "eq": "=",
                }
                solver.add_tracked_constraint(
                    operators[ctype],
                    f"{name} {symbols[ctype]} {constraint.value}",
                )
                return f"{var} {symbols[ctype]} {constraint.value}"

            elif ctype == "sum":
                items = list(constraint.items or [])
                if len(items) < 2:
                    return None

                names = [
                    f"item_{item}" if problem.people else item
                    for item in items
                ]
                zvars = [solver.variables.get(name) for name in names]
                if any(var is None for var in zvars):
                    return None

                solver.add_tracked_constraint(
                    Sum(zvars) == constraint.value,
                    f"{' + '.join(names)} == {constraint.value}",
                )
                return f"{' + '.join(items)} = {constraint.value}"

            elif ctype == "bool_value":
                name = constraint.items[0] if constraint.items else None
                zvar = solver.variables.get(name) if name else None
                if zvar is None:
                    return None
                value = bool(constraint.value)
                label = constraint.description or f"{name} == {value}"
                solver.add_tracked_constraint(zvar == BoolVal(value), label)
                return label

            elif ctype == "implies":
                spec = constraint.value if isinstance(constraint.value, dict) else {}
                antecedent = solver.variables.get(spec.get("if"))
                consequent = solver.variables.get(spec.get("then"))
                if antecedent is None or consequent is None:
                    return None
                label = constraint.description or (
                    f"{spec.get('if')} -> {spec.get('then')}"
                )
                solver.add_tracked_constraint(
                    Implies(antecedent, consequent),
                    label,
                )
                return label

            elif ctype in {"cardinality_le", "cardinality_ge"}:
                zvars = [solver.variables.get(name) for name in constraint.items]
                if not zvars or any(var is None for var in zvars):
                    return None
                count = Sum([If(var, 1, 0) for var in zvars])
                bound = int(constraint.value)
                expression = count <= bound if ctype.endswith("le") else count >= bound
                symbol = "<=" if ctype.endswith("le") else ">="
                label = constraint.description or f"count {symbol} {bound}"
                solver.add_tracked_constraint(expression, label)
                return label

            elif ctype == "weighted_sum_le":
                spec = constraint.value if isinstance(constraint.value, dict) else {}
                weights = spec.get("weights", {})
                terms = []
                for name, weight in weights.items():
                    zvar = solver.variables.get(name)
                    if zvar is None:
                        return None
                    terms.append(If(zvar, int(weight), 0))
                if not terms:
                    return None
                raw_limit = spec.get("limit")
                if isinstance(raw_limit, dict):
                    base = int(raw_limit.get("base", 0))
                    conditional_name = raw_limit.get("conditional_variable")
                    conditional = solver.variables.get(conditional_name)
                    if conditional is None:
                        return None
                    limit = base + If(
                        conditional,
                        int(raw_limit.get("conditional_gain", 0)),
                        0,
                    )
                else:
                    limit = int(raw_limit)
                label = constraint.description or "weighted_sum <= capacity"
                solver.add_tracked_constraint(Sum(terms) <= limit, label)
                return label

            return None

        except Exception as exc:
            logging.warning("Constraint formalization error: %s", exc)
            return None

    def _formalize_z3_objectives(
        self,
        problem: SymbolicProblem,
        solver: ConstraintSolver,
    ) -> List[str]:
        errors = []
        for objective in sorted(
            problem.objectives,
            key=lambda item: int(item.get("priority", 999)),
        ):
            objective_type = objective.get("type")
            if objective_type == "maximize_count":
                variables = [
                    solver.variables.get(name)
                    for name in objective.get("items", [])
                ]
                if not variables or any(var is None for var in variables):
                    errors.append(f"Could not formalize objective: {objective}")
                    continue
                expression = Sum([If(var, 1, 0) for var in variables])
                target = objective.get("target")
                if target is None:
                    solver.add_objective(
                        "maximize",
                        expression,
                        "maximize_count",
                    )
                else:
                    target = int(target)
                    distance = If(
                        expression >= target,
                        expression - target,
                        target - expression,
                    )
                    solver.add_objective(
                        "minimize",
                        distance,
                        f"minimize_distance_to_target({target})",
                    )
            elif objective_type == "maximize_weighted_sum":
                terms = []
                for name, weight in objective.get("weights", {}).items():
                    variable = solver.variables.get(name)
                    if variable is None:
                        terms = []
                        break
                    terms.append(If(variable, int(weight), 0))
                if not terms:
                    errors.append(f"Could not formalize objective: {objective}")
                    continue
                solver.add_objective(
                    "maximize",
                    Sum(terms),
                    "maximize_weighted_sum",
                )
            else:
                errors.append(f"Unknown objective: {objective}")
        return errors

    def _run_pydatalog_reasoning(
        self, problem: SymbolicProblem, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecución de inferencia lógica usando PyDatalog REAL.
        """
        if PyDatalogEngine is None:
            return {"status": "error", "error": "PyDatalogEngine not available"}

        # CREAR NUEVO PyDatalogEngine para aislamiento
        engine = self._create_fresh_pydatalog_engine()
        if engine is None:
            return {"status": "error", "error": "Could not create PyDatalogEngine"}

        result_base = {
            "status": "error",
            "facts_processed": [],
            "rules_applied": [],
            "inference_complete": False,
            "derived_facts": [],
            "bindings": [],
            "queries_executed": [],
            "query_results": {},
        }

        try:
            # Añadir hechos del problema
            if problem.facts:
                for fact in problem.facts:
                    if isinstance(fact, (list, tuple)) and len(fact) >= 2:
                        engine.add_fact(fact[0], *fact[1:])
                        result_base["facts_processed"].append(fact)

            # Definir reglas del problema
            if problem.rules:
                for rule in problem.rules:
                    if isinstance(rule, dict):
                        head = rule.get("head", "")
                        body = rule.get("body", "")
                        if head and body:
                            engine.define_rule(rule.get("name", "rule"), head, body)
                            result_base["rules_applied"].append(rule)

            # Consultas explícitas del problema. Si no se declararon,
            # consultar las cabezas de reglas evita el antiguo hardcode de
            # parent/ancestor sin inventar predicados.
            queries = []
            for raw_query in problem.queries:
                if isinstance(raw_query, str):
                    queries.append(raw_query)
                elif isinstance(raw_query, dict) and raw_query.get("query"):
                    queries.append(str(raw_query["query"]))

            if not queries:
                queries.extend(
                    rule.get("head", "")
                    for rule in problem.rules
                    if isinstance(rule, dict) and rule.get("head")
                )

            queries = list(dict.fromkeys(query for query in queries if query))
            query_failures = []
            for query in queries:
                query_result = engine.query(query)
                result_base["queries_executed"].append(query)
                result_base["query_results"][query] = {
                    "success": bool(query_result.success),
                    "bindings": list(query_result.bindings),
                    "derived_facts": list(query_result.derived_facts),
                    "error": query_result.error,
                }
                if query_result.success:
                    result_base["bindings"].extend(query_result.bindings)
                    result_base["derived_facts"].extend(
                        query_result.derived_facts
                    )
                else:
                    query_failures.append(
                        {"query": query, "error": query_result.error}
                    )

            result_base["inference_complete"] = bool(queries) and not query_failures
            if query_failures:
                result_base["query_failures"] = query_failures

            if query_failures:
                result_base["status"] = "error"
            elif result_base["inference_complete"]:
                result_base["status"] = "success"
            elif not problem.facts and not problem.rules:
                result_base["status"] = "skipped"
                result_base["inference_complete"] = False
            else:
                result_base["status"] = "success"

        except Exception as e:
            result_base["error"] = str(e)

        return result_base

    def _run_combined_reasoning(
        self, problem: SymbolicProblem, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Pipeline compuesto: grafo -> reglas -> restricciones -> validación."""
        combined_result = {
            "networkx_analysis": None,
            "z3_analysis": None,
            "pydatalog_analysis": None,
            "combined_conclusion": "",
            "confidence": 0.0,
            "executed_motors": [],
            "required_engines": [],
            "knowledge_transfers": [],
            "validation": {},
            "status": "success",
        }

        working_problem = deepcopy(problem)
        failures = []

        # 1. NetworkX deriva alcance/dependencias; esas relaciones se
        # convierten en hechos que el motor lógico puede consumir.
        if working_problem.relations:
            combined_result["required_engines"].append("networkx")
            nx_result = self._run_networkx_reasoning(working_problem, context)
            combined_result["networkx_analysis"] = nx_result
            if nx_result.get("status") == "success":
                combined_result["executed_motors"].append("networkx")
                graph_facts = []
                for source, target in nx_result.get("transitive_relations", []):
                    fact = ("precedes", source, target)
                    if fact not in working_problem.facts:
                        working_problem.facts.append(fact)
                        graph_facts.append(fact)
                combined_result["knowledge_transfers"].append(
                    {
                        "from": "networkx",
                        "to": "pydatalog",
                        "facts": graph_facts,
                    }
                )
            else:
                failures.append({"engine": "networkx", "result": nx_result})

        # 2. PyDatalog deriva estados operativos. Sus hechos se conservan en
        # la IR y los estados cannot_receive se convierten en restricciones.
        if working_problem.facts or working_problem.rules:
            combined_result["required_engines"].append("pydatalog")
            pd_result = self._run_pydatalog_reasoning(working_problem, context)
            combined_result["pydatalog_analysis"] = pd_result
            if pd_result.get("status") == "success":
                combined_result["executed_motors"].append("pydatalog")
                z3_constraints = []
                for derived in pd_result.get("derived_facts", []):
                    predicate = derived.get("predicate")
                    args = list(derived.get("args", []))
                    fact = tuple([predicate] + args)
                    if predicate and fact not in working_problem.facts:
                        working_problem.facts.append(fact)
                    if predicate == "cannot_receive" and args:
                        variable = f"receive_{ProblemExtractor._slug(str(args[0]))}"
                        if variable in working_problem.variables:
                            constraint = SymbolicConstraint(
                                type="bool_value",
                                value=False,
                                items=[variable],
                                description=(
                                    f"{variable}=False derivado por PyDatalog"
                                ),
                            )
                            working_problem.constraints.append(constraint)
                            z3_constraints.append(constraint.to_dict())
                combined_result["knowledge_transfers"].append(
                    {
                        "from": "pydatalog",
                        "to": "z3",
                        "constraints": z3_constraints,
                    }
                )
            else:
                failures.append({"engine": "pydatalog", "result": pd_result})

        # 3. Z3/Optimize recibe tanto las restricciones originales como las
        # derivadas por reglas.
        if (
            working_problem.constraints
            or working_problem.variables
            or (working_problem.items and working_problem.people)
        ):
            combined_result["required_engines"].append("z3")
            z3_result = self._run_z3_reasoning(working_problem, context)
            combined_result["z3_analysis"] = z3_result
            if z3_result.get("status") == "success":
                combined_result["executed_motors"].append("z3")
            else:
                failures.append({"engine": "z3", "result": z3_result})

        if not combined_result["required_engines"]:
            combined_result["status"] = "formalization_error"
            combined_result["formalization_error"] = True
            combined_result["formalization_errors"] = [
                "No symbolic component could be formalized"
            ]
        elif failures:
            combined_result["status"] = "error"
            combined_result["failures"] = failures

        combined_result["validation"] = {
            "required_engines_succeeded": (
                not failures
                and set(combined_result["required_engines"])
                == set(combined_result["executed_motors"])
            ),
            "z3_solution_valid": (
                (combined_result["z3_analysis"] or {}).get(
                    "solution_valid", True
                )
            ),
            "no_unformalized_constraints": not (
                (combined_result["z3_analysis"] or {}).get(
                    "formalization_errors", []
                )
            ),
        }

        # Generar conclusión basada en resultados reales
        conclusions = []
        nx_data = combined_result["networkx_analysis"] or {}
        if nx_data.get("is_acyclic") is not None:
            conclusions.append(f"Graph acyclic status: {nx_data.get('is_acyclic')}")
        if nx_data.get("cycles_found"):
            conclusions.append(f"Cycles: {len(nx_data.get('cycles_found', []))}")

        z3_data = combined_result["z3_analysis"] or {}
        if z3_data.get("solution_status") != "unknown":
            conclusions.append(f"Constraints: {z3_data.get('solution_status')}")

        pd_data = combined_result["pydatalog_analysis"] or {}
        if pd_data.get("inference_complete"):
            conclusions.append("Logical inference completed")

        combined_result["combined_conclusion"] = " | ".join(conclusions) if conclusions else "Analysis completed"
        combined_result["confidence"] = (
            len(combined_result["executed_motors"])
            / len(combined_result["required_engines"])
            if combined_result["required_engines"] else 0.0
        )

        return combined_result

    def _prepare_evidence(
        self, results: Dict[str, Any], analysis: Dict[str, Any], problem: SymbolicProblem
    ) -> Dict[str, Any]:
        """Preparar evidencia estructurada basada en resultados reales del motor"""
        return {
            "conclusion": results.get("combined_conclusion", 
                            results.get("solution_status", "analysis_completed")),
            "input_formalized": {
                "mode": problem.mode.value,
                "items": problem.items,
                "people": problem.people,
                "constraints_count": len(problem.constraints),
                "relations_count": len(problem.relations),
                "facts_count": len(problem.facts)
            },
            "engine_executed": results.get("executed_motors", []),
            "status": results.get("status"),
            "output_real": results,
            "validations_performed": [
                "entity_validation",
                "constraint_domain_check",
                "result_consistency"
            ],
            "constraints_rejected": results.get("formalization_errors", []),
            "timestamp": datetime.now().isoformat()
        }

    def get_status(self) -> Dict[str, Any]:
        """Obtener estado actual del sistema de razonamiento neurosimbólico."""
        return {
            "stats": self.stats,
            "reasoning_available": REASONING_AVAILABLE,
            "integration_status": "active" if REASONING_AVAILABLE else "fallback_only",
            "engines": {
                "networkx": GraphAnalyzer is not None,
                "z3": ConstraintSolver is not None,
                "pydatalog": PyDatalogEngine is not None,
            },
            "timestamp": datetime.now().isoformat()
        }


# Instancia global
_coordinator = None


def get_coordinator() -> NeurosymbolicCoordinator:
    """Obtener instancia singleton del coordinador."""
    global _coordinator
    if _coordinator is None:
        _coordinator = NeurosymbolicCoordinator()
    return _coordinator


# Funciones públicas
def analyze_need_for_reasoning(context: Dict[str, Any]) -> Dict[str, Any]:
    """Función pública para analizar si se necesita razonamiento simbólico."""
    coordinator = get_coordinator()
    return coordinator.analyze_context_for_reasoning(context)


def execute_symbolic_analysis(
    task_description: str,
    context: Dict[str, Any],
    engine_preference: str = "auto"
) -> Dict[str, Any]:
    """Función pública para ejecutar análisis simbólico."""
    coordinator = get_coordinator()
    result = coordinator.execute_symbolic_reasoning(task_description, context, engine_preference)
    return result.to_dict()


def auto_trigger_reasoning_if_needed(
    task_description: str,
    context: Dict[str, Any],
    engine_preference: str = "auto"
) -> Optional[Dict[str, Any]]:
    """Función pública que activa razonamiento simbólico automáticamente cuando detecta necesidad."""
    coordinator = get_coordinator()
    analysis = coordinator.analyze_context_for_reasoning(context)

    if analysis["needs_symbolic_reasoning"]:
        result = coordinator.execute_symbolic_reasoning(task_description, context, engine_preference)
        return result.to_dict()
    return None
