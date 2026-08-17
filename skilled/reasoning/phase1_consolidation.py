"""
Phase 1: Consolidation and Inventory - Existing Reasoning Capabilities

Este módulo realiza un inventario de todas las capacidades de razonamiento ya existentes
en el ecosistema Hermes y prepara el terreno para la arquitectura híbrida.
"""

import os
import sys
import yaml
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@dataclass
class Component:
    """Representación de un componente de razonamiento"""
    name: str
    type: str  # "engine", "integrator", "router", "policy"
    status: str = "active"  # "active", "deprecated", "experimental"
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    capabilities: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    verified: bool = False
    last_tested: str = ""

@dataclass
class ReasoningCapability:
    """Capacidad específica de razonamiento"""
    capability_id: str
    capability_type: str  # "policy", "constraint", "relational", "temporal", "causal"
    engine: str
    confidence: float = 0.0
    available: bool = False
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""

class Phase1Consolidation:
    """
    Fase 1: Consolidación - Identificar y evaluar capacidades existentes
    """
    
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.capabilities: Dict[str, ReasoningCapability] = {}
        self.duplicates: List[Dict[str, str]] = []
        self.gaps: List[str] = []
        
    def load_existing_components(self) -> None:
        """Cargar todos los componentes de razonamiento existentes"""
        reasoning_dir = Path("/home/fernando/ai-ecosystem/skilled/reasoning")
        
        # Mapeo de archivos a componentes
        component_map = {
            "hermes_integration.py": Component(
                name="hermes_integration",
                type="integrator",
                description="Integración del razonamiento simbólico con Hermes"
            ),
            "neuro_symbolic_engine.py": Component(
                name="neuro_symbolic_engine", 
                type="engine",
                description="Motor de razonamiento neurosimbólico principal"
            ),
            "z3_solver_integration.py": Component(
                name="z3_solver_integration",
                type="engine", 
                description="Integración del solver de restricciones Z3"
            ),
            "pydatalog_integration.py": Component(
                name="pydatalog_integration",
                type="engine",
                description="Integración del backend PyDatalog"
            ),
            "networkx_wrapper.py": Component(
                name="networkx_wrapper",
                type="engine",
                description="Integración del wrapper NetworkX"
            ),
            "task_router.py": Component(
                name="task_router",
                type="router",
                description="Enrutador de tareas hacia motores apropiados"
            ),
            "neurosymbolic_integrator.py": Component(
                name="neurosymbolic_integrator",
                type="integrator",
                description="Capa de integración neurosimbólica"
            )
        }
        
        for file_name, component in component_map.items():
            file_path = reasoning_dir / file_name
            if file_path.exists():
                component.config = self._extract_config(file_path)
                self.components[component.name] = component
                print(f"✓ Cargado componente: {component.name}")
            else:
                print(f"✗ Componente no encontrado: {file_name}")
    
    def _extract_config(self, file_path: Path) -> Dict[str, Any]:
        """Extraer configuración de un componente"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            config = {}
            
            # Buscar imports
            if "from reasoning" in content or 'from reasoning' in content.replace(" ", ""):
                config["imports_reasoning"] = True
            
            # Buscar decorators
            if "@dataclass" in content:
                config["has_dataclasses"] = True
                
            # Buscar logging
            if "logging.getLogger" in content:
                config["has_logging"] = True
                
            # Buscar type hints
            if "->" in content and ":" in content:
                config["has_type_hints"] = True
                
            return config
        except Exception as e:
            print(f"Error al extraer configuración de {file_path}: {e}")
            return {}
    
    def analyze_capabilities(self) -> None:
        """Analizar capacidades de cada componente"""
        capability_descriptions = {
            "policy_engine": "Motor de aplicación determinista de políticas",
            "constraint_engine": "Motor de verificación de restricciones complejas",
            "relational_engine": "Motor de razonamiento relacional/recursivo", 
            "graph_engine": "Motor de análisis de grafos y relaciones",
            "human_approval_engine": "Motor de aprobación/aprobación humana",
            "orchestration_engine": "Motor de ciclo de vida de tareas",
            "memory_integration": "Integración con knowledge broker y memoria"
        }
        
        engineered_caps = {
            "hermes_integration": ["policy_engine", "memory_integration", "orchestration_engine"],
            "neurosymbolic_engine": ["graph_engine", "constraint_engine"],
            "z3_solver_integration": ["constraint_engine"],
            "pydatalog_integration": ["relational_engine"],
            "networkx_wrapper": ["graph_engine"],
            "task_router": ["policy_engine", "orchestration_engine"],
            "neurosymbolic_integrator": ["policy_engine", "memory_integration"]
        }
        
        # Asociar capacidades a componentes
        for component_name, capability_names in engineered_caps.items():
            for capability_name in capability_names:
                cap = ReasoningCapability(
                    capability_id=f"{component_name}_{capability_name}",
                    capability_type=capability_name.replace("_engine", ""),
                    engine=self._get_engine_for_capability(capability_name),
                    confidence=self._get_confidence(capability_name),
                    available=True,
                    summary=capability_descriptions.get(capability_name, ""),
                    performance_metrics={}
                )
                self.capabilities[cap.capability_id] = cap
        
        print(f"\n✓ Analizadas capacidades: {len(self.capabilities)} capacidades identificadas")
    
    def _get_engine_for_capability(self, capability_name: str) -> str:
        """Obtener motor de razonamiento para una capacidad"""
        engine_map = {
            "policy_engine": "python",
            "constraint_engine": "z3",
            "relational_engine": "pydatalog",
            "graph_engine": "networkx",
            "human_approval_engine": "python",
            "orchestration_engine": "python",
            "memory_integration": "python"
        }
        return engine_map.get(capability_name, "python")
    
    def _get_confidence(self, capability_name: str) -> float:
        """Obtener confianza para una capacidad"""
        confidence_map = {
            "policy_engine": 0.9,
            "constraint_engine": 0.8,
            "relational_engine": 0.7,
            "graph_engine": 0.8,
            "human_approval_engine": 0.9,
            "orchestration_engine": 0.9,
            "memory_integration": 0.8
        }
        return confidence_map.get(capability_name, 0.5)
    
    def identify_duplicates(self) -> None:
        """Identificar duplicaciones y responsabilidades superpuestas"""
        responsibility_map = {}
        
        # Capacidades implementadas en múltiples componentes
        for component_name, capability_names in {
            "hermes_integration": ["policy_engine", "memory_integration"],
            "neurosymbolic_integrator": ["policy_engine", "memory_integration"]
        }.items():
            for capability in capability_names:
                if capability not in responsibility_map:
                    responsibility_map[capability] = []
                responsibility_map[capability].append(component_name)
        
        for capability, components in responsibility_map.items():
            if len(components) > 1:
                self.duplicates.append({
                    "capability": capability,
                    "components": components,
                    "issue": f"Capacidad '{capability}' implementada en múltiples componentes"
                })
                print(f"⚠ Duplicación encontrada: {capability} -> {components}")
    
    def identify_gaps(self) -> None:
        """Identificar brechas en capacidades críticas"""
        expected_capabilities = {
            "policy_engine", "constraint_engine", "relational_engine", 
            "graph_engine", "human_approval_engine", "orchestration_engine",
            "memory_integration"
        }
        
        # Extraer tipos de capacidad de los IDs
        implemented = set()
        for cap_id in self.capabilities.keys():
            parts = cap_id.split('_')
            if len(parts) >= 2:
                cap_type = parts[1] if len(parts) == 2 else '_'.join(parts[1:]).replace('_engine', '')
                implemented.add(cap_type.replace('_engine', ''))
        
        missing = expected_capabilities - implemented
        
        if missing:
            for gap in sorted(missing):
                self.gaps.append(f"Falta capacidad crítica: {gap}")
                print(f"✗ Falta: {gap}")
    
    def generate_report(self) -> str:
        """Generar reporte de consolidación"""
        report = "=" * 60 + "\n"
        report += "Fase 1: Consolidación y Inventario\n"
        report += "=" * 60 + "\n\n"
        
        report += f"Componentes cargados: {len(self.components)}\n"
        for name, component in self.components.items():
            report += f"  - {component.name} ({component.type}): {component.description}\n"
        
        report += f"\nTotal capacidades identificadas: {len(self.capabilities)}\n"
        for cap_id, capability in self.capabilities.items():
            report += f"  - {capability.capability_id}: {capability.summary}\n"
        
        report += f"\nDuplicaciones encontradas: {len(self.duplicates)}\n"
        for dup in self.duplicates:
            report += f"  - {dup['issue']}\n"
        
        report += f"\nBrechas identificadas: {len(self.gaps)}\n"
        for gap in self.gaps:
            report += f"  - {gap}\n"
        
        report += "\n" + "=" * 60 + "\n"
        report += "PRIORIDADES DE IMPLEMENTACIÓN\n"
        report += "=" * 60 + "\n\n"
        
        if self.duplicates:
            report += "1. RESOLVER DUPLICACIONES\n"
            report += "   Eliminar duplicaciones en: policy_engine, memory_integration\n\n"
        
        if self.gaps:
            report += "2. AÑADIR CAPACIDADES FALTANTES\n"
            for gap in sorted(self.gaps):
                capability = gap.split(": ")[1]
                report += f"   - Añadir {capability}\n"
            report += "\n"
        
        report += "3. ESTANDARIZAR CONTRATOS E INTERFACES\n"
        report += "   Definir contratos claros para todos los motores\n"
        
        return report

def main():
    """Ejecutar Fase 1: Consolidación"""
    print("Fase 1: Consolidación y Inventario\n")
    print("Analizando componentes de razonamiento existentes...\n")
    
    consolidation = Phase1Consolidation()
    consolidation.load_existing_components()
    consolidation.analyze_capabilities()
    consolidation.identify_duplicates()
    consolidation.identify_gaps()
    
    report = consolidation.generate_report()
    print(report)
    
    # Guardar reporte
    with open("/home/fernando/ai-ecosystem/phase1_consolidation_report.md", "w") as f:
        f.write(report)
    
    print(f"\nReporte guardado en: /home/fernando/ai-ecosystem/phase1_consolidation_report.md")
    
    # Resumir hallazgos
    print("\n" + "=" * 60)
    print("RESUMEN DE LA FASE 1")
    print("=" * 60)
    
    print(f"✓ Componentes: {len(consolidation.components)}")
    print(f"✓ Capacidades: {len(consolidation.capabilities)}")
    print(f"⚠ Duplicaciones: {len(consolidation.duplicates)}")
    print(f"✗ Brechas: {len(consolidation.gaps)}")
    
    if consolidation.duplicates or consolidation.gaps:
        print("\n⚠️  Acciones requeridas: Corregir duplicaciones y brechas")
        return 1
    else:
        print("\n✅ Consolidación completada exitosamente")
        return 0

if __name__ == "__main__":
    exit(main())