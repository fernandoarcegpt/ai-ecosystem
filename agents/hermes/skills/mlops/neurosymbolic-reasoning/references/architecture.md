# Arquitectura Neurosimbólica

## Componentes principales
1. NeurosymbolicCoordinator - Coordina los motores
2. HermesSymbolIntegration - Expone interfaz Hermes
3. GraphAnalyzer - Wrapper NetworkX (aislamiento de estado garantizado)
4. ConstraintSolver - Wrapper Z3 (nuevo solver por ejecución)
5. SymbolicEngine - Wrapper PyDatalog (nuevo motor por ejecución)

## Diagrama de flujo
task_description -> analyze_context_for_reasoning -> needs_symbolic_reasoning?
                                                           |
                                                          YES
                                                           |
                              engine = recommended_engine
                                                           |
                          +----------------------------------+--------------------------+
                          |                          |                         |
                    networkx_analysis    z3_analysis    pydatalog_analysis
                          |                          |
                          +--------------------------+--------------------------+
                                              |
                                     evidence_for_hermes
                                              |
                                  +-----------+-----------+
                                  |                       |
                       integrate_result          log_stats

## Aislamiento de estado (Requirement #2 reparado)
- Cada ejecución crea nuevos GraphAnalyzer(), ConstraintSolver(), SymbolicEngine()
- El metodo _run_networkx_reasoning() crea nx.DiGraph() local
- No hay comparticion de estado entre llamadas

## Verificacion
Ejecutar test_neurosymbolic.py incluido en el proyecto raiz.