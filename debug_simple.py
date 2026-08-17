import sys
sys.path.insert(0, '/home/fernando/ai-ecosystem/skilled')
from reasoning.neuro_symbolic_engine import NeurosymbolicCoordinator

coordinator = NeurosymbolicCoordinator()
simple_tasks = [
    "What is the capital of France?",
    "Hello, how are you today?",
    "Can you tell me a joke?",
    "What's the weather like?",
    "Thank you for your help."
]
for task in simple_tasks:
    analysis = coordinator.analyze_context_for_reasoning({"description": task})
    print(f"Task: {task}")
    print(f"  Needs reasoning: {analysis['needs_symbolic_reasoning']}")
    print(f"  Keyword score: {analysis['keyword_score']}")
    print(f"  Matched keywords: {analysis['matched_keywords']}")
    print(f"  Structural patterns: {analysis['structural_patterns']}")
    print()