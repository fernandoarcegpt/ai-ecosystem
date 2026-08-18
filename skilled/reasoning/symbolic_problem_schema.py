"""
SymbolicProblem - Representación formal explícita entre extracción y razonamiento.

Pipeline:
texto -> extracción -> SymbolicProblem -> validación -> motor -> validación de resultado

Principios:
- No inventar entidades.
- Los motores no interpretan lenguaje natural directamente.
- La extracción debe producir estructuras explícitas.
- Un problema no se considera formalizado si faltan relaciones, entidades o
  restricciones necesarias para ejecutar el motor correspondiente.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Iterable
from enum import Enum
from collections import Counter
import re


class ReasoningMode(Enum):
    """Modos de razonamiento disponibles."""
    NONE = "none"
    GRAPHS = "graphs"
    CONSTRAINTS = "constraints"
    LOGIC = "logic"
    COMBINED = "combined"


@dataclass
class SymbolicConstraint:
    """Restricción formal estructurada."""
    type: str
    value: Any = None
    items: List[str] = field(default_factory=list)
    people: List[str] = field(default_factory=list)
    description: str = ""
    source: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "value": self.value,
            "items": self.items,
            "people": self.people,
            "description": self.description,
            "source": self.source,
        }


@dataclass
class SymbolicProblem:
    """
    Representación formal de un problema simbólico.

    El motor de razonamiento recibe este objeto estructurado y no debe
    reinterpretar el lenguaje natural.
    """

    mode: ReasoningMode
    entities: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    people: List[str] = field(default_factory=list)
    facts: List[Any] = field(default_factory=list)
    rules: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[SymbolicConstraint] = field(default_factory=list)
    relations: List[List[str]] = field(default_factory=list)
    relation_metadata: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    objectives: List[Dict[str, Any]] = field(default_factory=list)
    assumptions: List[Dict[str, Any]] = field(default_factory=list)
    unknowns: List[Dict[str, Any]] = field(default_factory=list)
    queries: List[Any] = field(default_factory=list)
    provenance: List[Dict[str, Any]] = field(default_factory=list)
    source_query: str = ""
    structural_indicators: Dict[str, Any] = field(default_factory=dict)

    def validate_entities(self) -> bool:
        """Valida referencias internas sin inventar entidades."""
        all_items = set(self.items)
        all_people = set(self.people)
        all_entities = set(self.entities)

        for constraint in self.constraints:
            for item in constraint.items:
                if all_items and item not in all_items:
                    raise ValueError(
                        f"Constraint references unknown item: {item}"
                    )
            for person in constraint.people:
                if all_people and person not in all_people:
                    raise ValueError(
                        f"Constraint references unknown person: {person}"
                    )

        for relation in self.relations:
            if len(relation) != 2:
                raise ValueError(
                    f"Graph relation must contain exactly 2 nodes: {relation}"
                )
            if all_entities:
                for node in relation:
                    if node not in all_entities:
                        raise ValueError(
                            f"Relation references unknown entity: {node}"
                        )

        return True

    def validate_solution(self, solution: Dict[str, Any]) -> bool:
        """
        Valida soluciones de asignación.

        Verifica:
        - todos los ítems están asignados;
        - solo se usan personas válidas;
        - max_items_per_person;
        - different_person;
        - same_person, si se usa en el futuro.
        """
        if not solution:
            return False

        if self.items and self.people:
            if set(solution.keys()) != set(self.items):
                return False

            if any(person not in self.people for person in solution.values()):
                return False

            counts = Counter(solution.values())

            for constraint in self.constraints:
                if constraint.type == "max_items_per_person":
                    try:
                        maximum = int(constraint.value)
                    except (TypeError, ValueError):
                        return False
                    if any(count > maximum for count in counts.values()):
                        return False

                elif constraint.type == "different_person":
                    if len(constraint.items) != 2:
                        return False
                    a, b = constraint.items
                    if a not in solution or b not in solution:
                        return False
                    if solution[a] == solution[b]:
                        return False

                elif constraint.type == "same_person":
                    if len(constraint.items) != 2:
                        return False
                    a, b = constraint.items
                    if a not in solution or b not in solution:
                        return False
                    if solution[a] != solution[b]:
                        return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "entities": self.entities,
            "items": self.items,
            "people": self.people,
            "facts": self.facts,
            "rules": self.rules,
            "constraints": [c.to_dict() for c in self.constraints],
            "relations": self.relations,
            "relation_metadata": self.relation_metadata,
            "variables": self.variables,
            "objectives": self.objectives,
            "assumptions": self.assumptions,
            "unknowns": self.unknowns,
            "queries": self.queries,
            "provenance": self.provenance,
            "source_query": self.source_query,
            "structural_indicators": self.structural_indicators,
        }


class ProblemExtractor:
    """
    Extrae SymbolicProblem desde texto.

    Solo reconoce información presente explícitamente en el input o en el
    contexto estructurado suministrado por el llamador.
    """

    _NUMBER_WORDS = {
        "cero": 0,
        "uno": 1,
        "una": 1,
        "un": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
        "diez": 10,
        "once": 11,
        "doce": 12,
        "trece": 13,
        "catorce": 14,
        "quince": 15,
        "dieciseis": 16,
        "dieciséis": 16,
        "diecisiete": 17,
        "dieciocho": 18,
        "diecinueve": 19,
        "veinte": 20,
    }

    @staticmethod
    def _unique(values: Iterable[str]) -> List[str]:
        """Deduplicación estable."""
        seen = set()
        result = []
        for value in values:
            value = str(value).strip()
            if value and value not in seen:
                seen.add(value)
                result.append(value)
        return result

    @classmethod
    def _parse_number(cls, token: str) -> Optional[int]:
        token = token.strip().lower()
        if token.isdigit():
            return int(token)
        return cls._NUMBER_WORDS.get(token)

    @staticmethod
    def _split_simple_list(text: str) -> List[str]:
        """
        Divide listas simples del tipo:
        A,B,C / Ana, Luis y Marta
        """
        cleaned = text.strip().strip(" .;:")
        if not cleaned:
            return []
        parts = re.split(r"\s*,\s*|\s+\by\b\s+", cleaned, flags=re.IGNORECASE)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def _slug(value: str) -> str:
        """Identificador estable y legible para variables/predicados."""
        import unicodedata

        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = "".join(
            char for char in normalized if not unicodedata.combining(char)
        )
        return re.sub(r"[^A-Za-z0-9_]+", "_", ascii_value).strip("_")

    @staticmethod
    def _source_record(
        text: str,
        match: re.Match,
        kind: str,
        confidence: float = 1.0,
    ) -> Dict[str, Any]:
        return {
            "kind": kind,
            "source_text": match.group(0),
            "span": [match.start(), match.end()],
            "confidence": confidence,
        }

    @classmethod
    def extract(
        cls,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> SymbolicProblem:
        """
        Extrae y fusiona estructuras simbólicas explícitas.

        No usa una cadena exclusiva de prioridades: una consulta puede
        contener simultáneamente grafos, restricciones y lógica.
        """
        context = context or {}
        lower = text.lower()

        problem = SymbolicProblem(
            mode=ReasoningMode.NONE,
            source_query=text,
        )

        def merge_component(component: SymbolicProblem) -> None:
            problem.entities = cls._unique(
                list(problem.entities) + list(component.entities)
            )
            problem.items = cls._unique(
                list(problem.items) + list(component.items)
            )
            problem.people = cls._unique(
                list(problem.people) + list(component.people)
            )

            problem.facts.extend(component.facts)
            problem.rules.extend(component.rules)
            problem.constraints.extend(component.constraints)

            for relation in component.relations:
                if relation not in problem.relations:
                    problem.relations.append(relation)

            problem.variables.update(component.variables)
            problem.objectives.extend(component.objectives)
            problem.assumptions.extend(component.assumptions)
            problem.unknowns.extend(component.unknowns)
            problem.queries.extend(component.queries)
            problem.provenance.extend(component.provenance)
            problem.relation_metadata.extend(component.relation_metadata)
            problem.structural_indicators.update(
                component.structural_indicators
            )

        # --------------------------------------------------
        # ASIGNACIONES / RESTRICCIONES
        # --------------------------------------------------

        assignment_trigger = (
            "entre" in lower
            and any(
                verb in lower
                for verb in (
                    "reparte",
                    "asigna",
                    "asignar",
                    "distribuye",
                    "distribuir",
                )
            )
        )

        if assignment_trigger:
            merge_component(cls.extract_assignable_entities(text))

        # --------------------------------------------------
        # GRAFOS
        #
        # "ciclo" o "grafo" solos NO bastan.
        # Exigimos relaciones formalizables.
        # --------------------------------------------------

        has_arrow = "->" in text or "→" in text

        dependency_pattern_es = re.search(
            r"\b[A-Za-zÁÉÍÓÚÜÑáéíóúüñ_][\wÁÉÍÓÚÜÑáéíóúüñ_-]*"
            r"\s+depende\s+de\s+"
            r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ_][\wÁÉÍÓÚÜÑáéíóúüñ_-]*\b",
            text,
            flags=re.IGNORECASE,
        )

        dependency_pattern_en = re.search(
            r"\b[A-Za-z_][\w_-]*\s+depends\s+on\s+"
            r"[A-Za-z_][\w_-]*\b",
            text,
            flags=re.IGNORECASE,
        )

        if has_arrow or dependency_pattern_es or dependency_pattern_en:
            graph_problem = cls.extract_graph_problem(text)

            # Una dependencia humana desnuda puede ser laboral,
            # económica, emocional, técnica, etc.
            # Formalizamos la relación, pero NO la tratamos como
            # evidencia determinista sin revisión.
            graph_context_words = (
                "grafo",
                "dependencia",
                "dependencias",
                "orden topológico",
                "orden topologico",
                "topología",
                "topologia",
                "ciclo",
                "arista",
                "nodo",
            )

            if (
                (dependency_pattern_es or dependency_pattern_en)
                and not has_arrow
                and not any(word in lower for word in graph_context_words)
            ):
                graph_problem.structural_indicators[
                    "human_review"
                ] = True
                graph_problem.structural_indicators[
                    "review_reason"
                ] = "bare_dependency_relation_is_ambiguous"

            merge_component(graph_problem)

        # --------------------------------------------------
        # LÓGICA FAMILIAR
        #
        # Requiere una proposición explícita "X es madre/padre de Y".
        # Así "placa madre de mi computadora" no activa PyDatalog.
        # --------------------------------------------------

        kinship_fact = re.search(
            r"\b[A-Za-zÁÉÍÓÚÜÑáéíóúüñ_-]+\s+"
            r"es\s+(?:padre|madre)\s+de\s+"
            r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ_-]+\b",
            text,
            flags=re.IGNORECASE,
        )

        if kinship_fact:
            merge_component(cls.extract_logic_problem(text))

        # --------------------------------------------------
        # RESTRICCIONES ARITMÉTICAS
        # --------------------------------------------------

        if re.search(
            r"\b[A-Za-z_]\w*\s*(?:>=|<=|>|<|=)\s*-?\d+",
            text,
        ):
            merge_component(cls.extract_constraints_problem(text))

        # --------------------------------------------------
        # PLANIFICACIÓN DE TRANSFERENCIAS DOCUMENTALES
        # --------------------------------------------------

        if any(
            marker in lower
            for marker in (
                "transferencia documental",
                "transferencias documentales",
                "cajas listas",
                "inventario definitivo",
                "capacidad disponible",
            )
        ):
            merge_component(cls.extract_transfer_plan(text))

        # --------------------------------------------------
        # CONTEXTO ESTRUCTURADO EXPLÍCITO
        # --------------------------------------------------

        cls._merge_structured_context(problem, context)
        cls._infer_mode_from_structure(problem)
        problem.validate_entities()

        return problem

    @classmethod
    def _merge_structured_context(
        cls,
        problem: SymbolicProblem,
        context: Dict[str, Any],
    ) -> None:
        """Fusiona solo información estructurada explícita."""
        if context.get("items"):
            problem.items = cls._unique(context["items"])

        if context.get("people"):
            problem.people = cls._unique(context["people"])

        if context.get("entities"):
            problem.entities = cls._unique(
                list(problem.entities) + list(context["entities"])
            )

        if context.get("relations"):
            relations = []
            for relation in context["relations"]:
                if isinstance(relation, (list, tuple)) and len(relation) == 2:
                    relations.append([str(relation[0]), str(relation[1])])
            if relations:
                problem.relations = relations
                problem.entities = cls._unique(
                    list(problem.entities)
                    + [node for rel in relations for node in rel]
                )

        if context.get("dependencies"):
            dependencies = context["dependencies"]

            # Si ya vienen como pares, tratarlos como relaciones explícitas.
            if (
                isinstance(dependencies, list)
                and dependencies
                and all(
                    isinstance(dep, (list, tuple)) and len(dep) == 2
                    for dep in dependencies
                )
            ):
                dep_relations = [
                    [str(dep[0]), str(dep[1])]
                    for dep in dependencies
                ]
                problem.relations.extend(dep_relations)
                problem.entities = cls._unique(
                    list(problem.entities)
                    + [node for rel in dep_relations for node in rel]
                )
            elif isinstance(dependencies, list):
                # Una lista plana se conserva como entidades, pero NO se
                # inventan aristas entre elementos consecutivos.
                problem.entities = cls._unique(
                    list(problem.entities)
                    + [str(dep) for dep in dependencies]
                )

        if context.get("facts"):
            problem.facts = list(context["facts"])

        if context.get("rules"):
            problem.rules = list(context["rules"])

        if context.get("constraints"):
            for raw in context["constraints"]:
                if isinstance(raw, SymbolicConstraint):
                    problem.constraints.append(raw)
                elif isinstance(raw, dict):
                    problem.constraints.append(
                        SymbolicConstraint(
                            type=raw.get("type", "unknown"),
                            value=raw.get("value"),
                            items=list(raw.get("items", [])),
                            people=list(raw.get("people", [])),
                            description=raw.get("description", ""),
                            source=dict(raw.get("source", {})),
                        )
                    )
                elif isinstance(raw, str):
                    parsed = cls.extract_constraints_problem(raw)
                    problem.constraints.extend(parsed.constraints)
                    problem.items = cls._unique(
                        list(problem.items) + list(parsed.items)
                    )

        if context.get("structural_indicators"):
            problem.structural_indicators = dict(
                context["structural_indicators"]
            )

        for key in (
            "objectives",
            "assumptions",
            "unknowns",
            "queries",
            "provenance",
            "relation_metadata",
        ):
            if context.get(key):
                current = getattr(problem, key)
                current.extend(list(context[key]))

        if context.get("variables"):
            problem.variables.update(dict(context["variables"]))

    @staticmethod
    def _infer_mode_from_structure(problem: SymbolicProblem) -> None:
        """Ajusta el modo según la estructura realmente extraída."""
        has_graph = bool(problem.relations)
        has_constraints = bool(
            problem.constraints or (problem.items and problem.people)
        )
        has_logic = bool(problem.facts or problem.rules)

        modes = sum((has_graph, has_constraints, has_logic))

        if modes > 1:
            problem.mode = ReasoningMode.COMBINED
        elif has_graph:
            problem.mode = ReasoningMode.GRAPHS
        elif has_constraints:
            problem.mode = ReasoningMode.CONSTRAINTS
        elif has_logic:
            problem.mode = ReasoningMode.LOGIC

    @classmethod
    def extract_transfer_plan(cls, text: str) -> SymbolicProblem:
        """Formaliza planes documentales solo a partir de frases explícitas.

        Esta ruta deliberadamente acotada convierte el caso operativo usado
        por Archivo Central en una regresión reproducible sin delegar la
        creación de hechos al LLM.
        """
        problem = SymbolicProblem(
            mode=ReasoningMode.NONE,
            source_query=text,
        )

        unit_pattern = (
            r"((?:[A-ZÁÉÍÓÚÜÑ]{2,8}|[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)"
            r"(?:\s+(?:[A-ZÁÉÍÓÚÜÑ]{2,8}|"
            r"[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)){0,2})"
        )
        ready_pattern = re.compile(
            rf"\b{unit_pattern}\s+(?:tiene|cuenta\s+con)\s+(\d+)\s+"
            r"cajas?\s+(?:listas?|organizadas?|listas?\s+para\s+transferir)",
        )

        units: List[str] = []
        ready: Dict[str, int] = {}
        for match in ready_pattern.finditer(text):
            unit = match.group(1).strip()
            boxes = int(match.group(2))
            units.append(unit)
            ready[unit] = boxes
            source = cls._source_record(text, match, "fact")
            problem.facts.append(("ready_boxes", unit, boxes))
            problem.provenance.append(source)

        missing_pattern = re.compile(
            rf"\b{unit_pattern}\s+(?:todav[ií]a\s+)?no\s+ha\s+remitido\s+"
            r"(?:el\s+)?inventario\s+definitivo",
        )
        for match in missing_pattern.finditer(text):
            unit = match.group(1).strip()
            units.append(unit)
            source = cls._source_record(text, match, "fact")
            problem.facts.append(("missing_final_inventory", unit))
            problem.provenance.append(source)

        inconsistent_patterns = (
            re.compile(
                rf"\b{unit_pattern}\s+(?:tiene|presenta)\s+(?:un\s+)?"
                r"inventario\s+inconsistente",
            ),
            re.compile(
                rf"\bel\s+inventario\s+de\s+{unit_pattern}\s+es\s+inconsistente",
            ),
        )
        for pattern in inconsistent_patterns:
            for match in pattern.finditer(text):
                unit = match.group(1).strip()
                units.append(unit)
                source = cls._source_record(text, match, "fact")
                fact = ("inventory_inconsistent", unit)
                if fact not in problem.facts:
                    problem.facts.append(fact)
                    problem.provenance.append(source)

        # Flujo explícito escrito con flechas: no se inventan etapas.
        graph_problem = cls.extract_graph_problem(text)
        problem.entities.extend(graph_problem.entities)
        problem.relations.extend(graph_problem.relations)
        for relation in graph_problem.relations:
            relation_match = re.search(
                rf"{re.escape(relation[0])}\s*(?:->|→)\s*"
                rf"{re.escape(relation[1])}",
                text,
            )
            metadata = {
                "source": relation[0],
                "target": relation[1],
                "type": "precedes",
            }
            if relation_match:
                source = cls._source_record(text, relation_match, "relation")
                metadata["provenance"] = source
                problem.provenance.append(source)
            problem.relation_metadata.append(metadata)

        # Reglas de negocio solo cuando la relación causal aparece en el texto.
        rule_specs = (
            (
                r"si\s+falta\s+(?:el\s+)?inventario\s+definitivo[^.;]*"
                r"(?:queda|est[aá])\s+bloquead[ao]",
                "blocked_from_missing_inventory",
                "blocked(X)",
                "missing_final_inventory(X)",
            ),
            (
                r"si\s+(?:el\s+)?inventario\s+es\s+inconsistente[^.;]*"
                r"requiere\s+correcci[oó]n",
                "correction_from_inconsistent_inventory",
                "requires_correction(X)",
                "inventory_inconsistent(X)",
            ),
            (
                r"no\s+puede\s+recibirse[^.;]*si\s+est[aá]\s+bloquead[ao]",
                "cannot_receive_blocked",
                "cannot_receive(X)",
                "blocked(X)",
            ),
            (
                r"no\s+puede\s+recibirse[^.;]*si\s+requiere\s+correcci[oó]n",
                "cannot_receive_correction",
                "cannot_receive(X)",
                "requires_correction(X)",
            ),
        )
        for pattern, name, head, body in rule_specs:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                source = cls._source_record(text, match, "rule")
                problem.rules.append(
                    {"name": name, "head": head, "body": body, "source": source}
                )
                problem.provenance.append(source)

        if problem.rules:
            heads = cls._unique(rule["head"] for rule in problem.rules)
            problem.queries.extend(heads)

        capacity_match = re.search(
            r"capacidad(?:\s+disponible|\s+inicial)?\s+(?:es|de|=)?\s*(\d+)\s+cajas?",
            text,
            flags=re.IGNORECASE,
        )
        capacity = int(capacity_match.group(1)) if capacity_match else None
        if capacity_match:
            source = cls._source_record(text, capacity_match, "constraint")
            problem.provenance.append(source)

        gain_match = re.search(
            r"reorganizaci[oó]n[^.;]*?(?:aumenta|agrega|suma|libera)\s+"
            r"(?:la\s+capacidad\s+en\s+)?(\d+)\s+cajas?",
            text,
            flags=re.IGNORECASE,
        )
        if gain_match:
            source = cls._source_record(text, gain_match, "variable")
            problem.variables["reorganize"] = {"type": "bool", "source": source}
            problem.provenance.append(source)

        problem.entities = cls._unique(list(problem.entities) + units)
        receive_variables = []
        for unit in cls._unique(units):
            variable = f"receive_{cls._slug(unit)}"
            receive_variables.append(variable)
            problem.variables[variable] = {"type": "bool", "entity": unit}

        if receive_variables:
            problem.assumptions.append(
                {
                    "id": "listed_impediments_complete_for_scope",
                    "description": (
                        "Para optimizar el plan, se consideran candidatas las "
                        "unidades con cajas listas que no tengan un impedimento "
                        "derivado de los hechos y reglas proporcionados."
                    ),
                    "scope": list(cls._unique(units)),
                    "source": "system_modeling_policy",
                }
            )

        if ready and capacity is not None:
            weights = {
                f"receive_{cls._slug(unit)}": boxes
                for unit, boxes in ready.items()
            }
            limit: Any = capacity
            if gain_match:
                limit = {
                    "base": capacity,
                    "conditional_variable": "reorganize",
                    "conditional_gain": int(gain_match.group(1)),
                }
            problem.constraints.append(
                SymbolicConstraint(
                    type="weighted_sum_le",
                    value={"weights": weights, "limit": limit},
                    items=list(weights),
                    description="El volumen seleccionado no supera la capacidad disponible",
                    source=(
                        cls._source_record(text, capacity_match, "constraint")
                        if capacity_match else {}
                    ),
                )
            )

        target_match = re.search(
            r"(?:meta|objetivo)\s+(?:institucional\s+)?(?:de|es)?\s*(\d+)\s+"
            r"transferencias?",
            text,
            flags=re.IGNORECASE,
        )
        if target_match and receive_variables:
            source = cls._source_record(text, target_match, "objective")
            problem.objectives.append(
                {
                    "type": "maximize_count",
                    "items": receive_variables,
                    "target": int(target_match.group(1)),
                    "priority": 1,
                    "source": source,
                }
            )
            problem.provenance.append(source)

        if gain_match:
            problem.objectives.append(
                {
                    "type": "minimize_boolean",
                    "variable": "reorganize",
                    "priority": 2,
                    "description": (
                        "No activar la reorganización si no es necesaria para "
                        "cumplir el objetivo prioritario."
                    ),
                }
            )

        if ready:
            problem.objectives.append(
                {
                    "type": "maximize_weighted_sum",
                    "weights": {
                        f"receive_{cls._slug(unit)}": boxes
                        for unit, boxes in ready.items()
                    },
                    "priority": 3,
                }
            )

        for match in re.finditer(
            r"(?:se\s+desconoce|no\s+se\s+conoce)\s+([^.;]+)",
            text,
            flags=re.IGNORECASE,
        ):
            problem.unknowns.append(
                {
                    "description": match.group(1).strip(),
                    "source": cls._source_record(text, match, "unknown", 1.0),
                }
            )

        return problem

    @classmethod
    def extract_assignable_entities(cls, text: str) -> SymbolicProblem:
        """
        Extrae problemas como:

        "Reparte A,B,C,D,E,F entre Ana,Luis,Marta.
         Máximo dos tareas por persona y A y B no pueden estar
         en la misma persona."
        """
        problem = SymbolicProblem(
            mode=ReasoningMode.NONE,
            source_query=text,
        )

        parts = re.split(r"\bentre\b", text, maxsplit=1, flags=re.IGNORECASE)
        if len(parts) != 2:
            return problem

        left, right = parts

        # Ítems: tomar solo el fragmento posterior al verbo de asignación.
        item_match = re.search(
            r"\b(?:reparte|asigna|asignar|distribuye|distribuir)\b\s+(.+)$",
            left,
            flags=re.IGNORECASE,
        )
        item_segment = item_match.group(1) if item_match else left
        items = cls._split_simple_list(item_segment)

        # Personas: solo el primer segmento tras "entre", antes de comenzar
        # las restricciones.
        people_segment = re.split(
            r"[.;]|"
            r",\s*(?=(?:con\s+)?(?:un\s+)?(?:máximo|maximo)\b)|"
            r"\b(?:con\s+)?(?:un\s+)?(?:máximo|maximo)\b",
            right,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0]
        people = cls._split_simple_list(people_segment)

        # Aceptar tokens simples; no imponer límites arbitrarios.
        problem.items = cls._unique(items)
        problem.people = cls._unique(people)

        if problem.items and problem.people:
            problem.mode = ReasoningMode.CONSTRAINTS

        # Máximo N tareas por persona. Acepta números y palabras simples.
        max_match = re.search(
            r"(?:máximo|maximo|como\s+máximo|como\s+maximo|"
            r"con\s+un\s+máximo|con\s+un\s+maximo)\s+"
            r"([0-9]+|[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)\s+"
            r"(?:tareas?|ítems?|items?|elementos?)\s+por\s+persona",
            text,
            flags=re.IGNORECASE,
        )
        if max_match:
            maximum = cls._parse_number(max_match.group(1))
            if maximum is not None:
                problem.constraints.append(
                    SymbolicConstraint(
                        type="max_items_per_person",
                        value=maximum,
                        description=max_match.group(0),
                    )
                )

        # "A y B no pueden estar en la misma persona"
        different_patterns = [
            # A y B no pueden estar juntas/juntos
            r"\b([A-Za-z0-9_]+)\s+y\s+([A-Za-z0-9_]+)\s+"
            r"no\s+pueden\s+estar\s+(?:juntas|juntos)\b",

            # A y B no pueden estar en la misma persona
            r"\b([A-Za-z0-9_]+)\s+y\s+([A-Za-z0-9_]+)\s+"
            r"no\s+pueden\s+estar\s+en\s+la\s+misma\s+persona\b",

            # A y B no pueden asignarse a la misma persona
            r"\b([A-Za-z0-9_]+)\s+y\s+([A-Za-z0-9_]+)\s+"
            r"no\s+pueden\s+(?:asignarse|ser\s+asignados?|ser\s+asignadas?)\s+"
            r"(?:a|en)\s+la\s+misma\s+persona\b",

            # A y B deben estar separadas/separados
            r"\b([A-Za-z0-9_]+)\s+y\s+([A-Za-z0-9_]+)\s+"
            r"deben\s+estar\s+(?:separadas|separados)\b",
        ]

        for pattern in different_patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                problem.constraints.append(
                    SymbolicConstraint(
                        type="different_person",
                        items=[match.group(1), match.group(2)],
                        description=match.group(0),
                    )
                )
                break

        return problem

    @classmethod
    def extract_graph_problem(cls, text: str) -> SymbolicProblem:
        """
        Extrae relaciones de dependencia y aristas explícitas.

        Semántica de dependencia:
        "A depende de B" se formaliza como B -> A,
        porque B debe preceder a A en un orden topológico.
        """
        problem = SymbolicProblem(
            mode=ReasoningMode.GRAPHS,
            source_query=text,
        )

        relations: List[List[str]] = []

        # A -> B -> C / A → B → C. Extraer la cadena completa evita que
        # ``re.findall`` pierda B -> C por usar coincidencias no solapadas.
        node_pattern = (
            r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]"
            r"[\wÁÉÍÓÚÜÑáéíóúüñ_-]*"
        )
        chain_pattern = re.compile(
            rf"\b{node_pattern}(?:\s*(?:->|→)\s*{node_pattern})+\b"
        )
        for chain_match in chain_pattern.finditer(text):
            nodes = re.findall(node_pattern, chain_match.group(0))
            relations.extend(
                [left, right] for left, right in zip(nodes, nodes[1:])
            )

        # "A depende de B" -> B -> A
        for dependent, dependency in re.findall(
            r"\b([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_][\wÁÉÍÓÚÜÑáéíóúüñ_-]*)"
            r"\s+depende\s+de\s+"
            r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_][\wÁÉÍÓÚÜÑáéíóúüñ_-]*)\b",
            text,
            flags=re.IGNORECASE,
        ):
            relations.append([dependency, dependent])

        # "A depends on B" -> B -> A
        for dependent, dependency in re.findall(
            r"\b([A-Za-z_][\w_-]*)\s+depends\s+on\s+"
            r"([A-Za-z_][\w_-]*)\b",
            text,
            flags=re.IGNORECASE,
        ):
            relations.append([dependency, dependent])

        # Deduplicar relaciones preservando orden.
        unique_relations = []
        seen_relations = set()
        for relation in relations:
            key = tuple(relation)
            if key not in seen_relations:
                seen_relations.add(key)
                unique_relations.append(relation)

        problem.relations = unique_relations
        problem.entities = cls._unique(
            node
            for relation in problem.relations
            for node in relation
        )

        return problem

    @staticmethod
    def extract_logic_problem(text: str) -> SymbolicProblem:
        """Extrae hechos familiares y las reglas directa/transitiva de ancestro."""
        problem = SymbolicProblem(
            mode=ReasoningMode.LOGIC,
            source_query=text,
        )

        fact_patterns = [
            (
                "parent",
                r"\b([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_-]+)\s+"
                r"es\s+(?:padre|madre)\s+de\s+"
                r"([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_-]+)\b",
            ),
        ]

        for predicate, pattern in fact_patterns:
            for left, right in re.findall(
                pattern,
                text,
                flags=re.IGNORECASE,
            ):
                problem.facts.append((predicate, left, right))

        if problem.facts:
            problem.rules.append(
                {
                    "name": "ancestor_direct",
                    "head": "ancestor(X, Y)",
                    "body": "parent(X, Y)",
                }
            )
            problem.rules.append(
                {
                    "name": "ancestor_transitive",
                    "head": "ancestor(X, Z)",
                    "body": "parent(X, Y) & ancestor(Y, Z)",
                }
            )

        return problem

    @staticmethod
    def extract_constraints_problem(text: str) -> SymbolicProblem:
        """
        Extrae restricciones aritméticas simples:

        x > 10
        x < 5
        x + y = 10
        """
        problem = SymbolicProblem(
            mode=ReasoningMode.CONSTRAINTS,
            source_query=text,
        )

        for var, val in re.findall(
            r"\b([A-Za-z_]\w*)\s*>=\s*(-?\d+)\b",
            text,
        ):
            problem.constraints.append(
                SymbolicConstraint(
                    type="ge",
                    value=int(val),
                    items=[var],
                    description=f"{var} >= {val}",
                )
            )
            if var not in problem.items:
                problem.items.append(var)

        for var, val in re.findall(
            r"\b([A-Za-z_]\w*)\s*<=\s*(-?\d+)\b",
            text,
        ):
            problem.constraints.append(
                SymbolicConstraint(
                    type="le",
                    value=int(val),
                    items=[var],
                    description=f"{var} <= {val}",
                )
            )
            if var not in problem.items:
                problem.items.append(var)

        for var, val in re.findall(
            r"\b([A-Za-z_]\w*)\s*>\s*(-?\d+)\b",
            text,
        ):
            problem.constraints.append(
                SymbolicConstraint(
                    type="gt",
                    value=int(val),
                    items=[var],
                    description=f"{var} > {val}",
                )
            )
            if var not in problem.items:
                problem.items.append(var)

        for var, val in re.findall(
            r"\b([A-Za-z_]\w*)\s*<\s*(-?\d+)\b",
            text,
        ):
            problem.constraints.append(
                SymbolicConstraint(
                    type="lt",
                    value=int(val),
                    items=[var],
                    description=f"{var} < {val}",
                )
            )
            if var not in problem.items:
                problem.items.append(var)

        for x, y, val in re.findall(
            r"\b([A-Za-z_]\w*)\s*\+\s*([A-Za-z_]\w*)\s*=\s*(-?\d+)\b",
            text,
        ):
            problem.constraints.append(
                SymbolicConstraint(
                    type="sum",
                    value=int(val),
                    items=[x, y],
                    description=f"{x} + {y} = {val}",
                )
            )
            for var in (x, y):
                if var not in problem.items:
                    problem.items.append(var)

        # Igualdad de una sola variable. Primero retiramos las sumas ya
        # reconocidas para no interpretar ``y = 10`` dentro de ``x + y = 10``.
        single_equality_text = re.sub(
            r"\b[A-Za-z_]\w*\s*\+\s*[A-Za-z_]\w*\s*=\s*-?\d+\b",
            "",
            text,
        )
        for var, val in re.findall(
            r"\b([A-Za-z_]\w*)\s*(?<![<>])=\s*(-?\d+)\b",
            single_equality_text,
        ):
            problem.constraints.append(
                SymbolicConstraint(
                    type="eq",
                    value=int(val),
                    items=[var],
                    description=f"{var} = {val}",
                )
            )
            if var not in problem.items:
                problem.items.append(var)

        return problem
