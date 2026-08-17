"""
NetworkX Wrapper para análisis de grafos y dependencias - CORREGIDO

Reparado para:
1. Procesar relaciones reales en aristas
2. Detectar ciclos y DAG correctamente
3. Devolver resultados estructurados
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class NetworkXResultStatus(Enum):
    """Estado de resultado del análisis de grafos"""
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    EMPTY = "empty"


class GraphAnalyzer:
    """
    Analizador de grafos con aislamiento de estado por instancia.
    
    Cada instancia crea su propio grafo - NO comparte estado.
    """
    
    def __init__(self):
        # Cada instancia tiene su propio grafo dirigido
        self.graph: nx.DiGraph = nx.DiGraph()
        self.node_attributes: Dict[str, Dict] = {}
        self.edge_attributes: Dict[Tuple[str, str], Dict] = {}
    
    def add_nodes(self, nodes: List[str]) -> None:
        """Añadir nodos al grafo"""
        self.graph.add_nodes_from(nodes)
    
    def add_edges(self, edges: List[Tuple[str, str]]) -> None:
        """Añadir aristas al grafo procesando relaciones estructuradas"""
        for source, target in edges:
            self.graph.add_edge(source, target)
    
    def add_edges_from_relations(self, relations: List[List[str]]) -> None:
        """
        Convertir relaciones estructuradas en aristas reales.
        
        Ejemplo: [["A","B"], ["B","C"]] → A→B, B→C
        """
        for relation in relations:
            if len(relation) >= 2:
                source, target = relation[0], relation[1]
                if source in self.graph.nodes() or target in self.graph.nodes():
                    self.graph.add_edge(source, target)
                else:
                    # Añadir nodos si no existen
                    self.graph.add_node(source)
                    self.graph.add_node(target)
                    self.graph.add_edge(source, target)
            elif len(relation) == 1:
                self.graph.add_node(relation[0])
    
    def detect_cycles(self) -> List[List[str]]:
        """
        Detectar ciclos en el grafo dirigido.
        
        Returns:
            Lista de ciclos, cada ciclo es una lista de nodos
        """
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except Exception:
            return []
    
    def is_acyclic(self) -> bool:
        """Verificar si el grafo es acíclico (DAG)"""
        return nx.is_directed_acyclic_graph(self.graph)
    
    def get_topological_order(self) -> Optional[List[str]]:
        """
        Obtener orden topológico si el grafo es DAG.
        
        Returns:
            Lista de nodos en orden topológico, o None si hay ciclos
        """
        if self.is_acyclic():
            return list(nx.topological_sort(self.graph))
        return None
    
    def analyze(self) -> Dict[str, Any]:
        """
        Análisis completo del grafo.
        
        Returns estado estructurado para que Hermes pueda usarlo.
        """
        result = {
            "status": NetworkXResultStatus.SUCCESS.value,
            "nodes": list(self.graph.nodes()),
            "edges": [(u, v) for u, v in self.graph.edges()],
            "is_acyclic": self.is_acyclic(),
            "cycles_found": self.detect_cycles(),
            "topological_order": None,
            "analysis_complete": False
        }
        
        if result["is_acyclic"]:
            result["topological_order"] = self.get_topological_order()
            result["analysis_complete"] = True
        else:
            result["status"] = NetworkXResultStatus.PARTIAL.value
            # No marcar como completado si hay ciclos detectados
            if result["cycles_found"]:
                result["status"] = NetworkXResultStatus.SUCCESS.value
                result["analysis_complete"] = True
        
        return result
    
    def count_nodes(self) -> int:
        """Contar número de nodos"""
        return self.graph.number_of_nodes()
    
    def count_edges(self) -> int:
        """Contar número de aristas"""
        return self.graph.number_of_edges()
    
    def clear(self) -> None:
        """Limpiar el grafo para nueva sesión"""
        self.graph.clear()
        self.node_attributes.clear()
        self.edge_attributes.clear()