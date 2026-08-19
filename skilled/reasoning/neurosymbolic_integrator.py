"""Compatibilidad con el antiguo ``HermesNeurosymbolicIntegrator``.

La implementación histórica de este módulo quedó reemplazada por el pipeline
canónico ``HermesSymbolIntegration -> MetaReasoner/NeurosymbolicCoordinator``.
Se conserva esta clase únicamente para no romper imports antiguos.
"""

from __future__ import annotations

from .hermes_integration import HermesSymbolIntegration


class HermesNeurosymbolicIntegrator(HermesSymbolIntegration):
    """Alias de compatibilidad hacia la integración neurosimbólica vigente."""

    deprecated = True


__all__ = ["HermesNeurosymbolicIntegrator"]
