import sys
sys.path.insert(0, '/home/fernando/ai-ecosystem/skilled')
from reasoning.neuro_symbolic_engine import NeurosymbolicCoordinator

# Simple test
coordinator = NeurosymbolicCoordinator()
result = coordinator.execute_symbolic_reasoning(
    'Test task',
    {'description': 'Test', 'constraints': ['x > 0']},
    engine_preference='z3'
)
print('Status:', result.status)
print('Success!' if result.status == 'success' else 'Failed:', result.error)