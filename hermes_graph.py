# hermes_graph.py
# LangGraph implementation for Hermes with Graphify node
from langgraph.graph import StateGraph, END
from typing import TypedDict, Any, Dict

# Define the state structure for Hermes's LangGraph
class HermesState(TypedDict):
    # Private memory of Hermes (agent-specific state)
    hermes_memory: Dict[str, Any]
    # Shared knowledge from OKF (via Knowledge Broker/Basic Memory)
    shared_knowledge: Dict[str, Any]
    # Input data for the current tool execution
    input: Any
    # Output after tool execution
    output: Any
    # Error message if any
    error: str

def get_hermes_memory(state: HermesState) -> Dict[str, Any]:
    """Retrieve Hermes's private memory from state."""
    return state.get("hermes_memory", {})

def get_shared_knowledge(state: HermesState) -> Dict[str, Any]:
    """Retrieve shared knowledge from OKF via Basic Memory.
    In a full implementation, this would query the Basic Memory index.
    """
    return state.get("shared_knowledge", {})

def graphify_node(state: HermesState) -> HermesState:
    """Graphify node: enriches context with Hermes private memory + shared OKF knowledge.
    This is the local instance of Graphify within Hermes agent.
    """
    hermes_mem = get_hermes_memory(state)
    shared_know = get_shared_knowledge(state)
    
    # Enrich the input with both memory sources
    enriched_input = {
        **state["input"],
        "hermes_context": hermes_mem,
        "shared_context": shared_know
    }
    
    return {
        **state,
        "input": enriched_input,
        "error": None  # Clear any previous error on successful enrichment
    }

def sandbox_tool(state: HermesState) -> HermesState:
    """Mock sandbox tool node - replace with actual tool execution logic.
    In reality, this would interface with Hermes's tool execution system.
    """
    try:
        # Simulate tool execution using enriched input
        # Actual implementation would call the tool with state["input"]
        tool_name = state["input"].get("tool", "unknown")
        output = f"Tool '{tool_name}' executed with context: {list(state['input'].keys())}"
        return {
            **state,
            "output": output,
            "error": None
        }
    except Exception as e:
        return {
            **state,
            "output": None,
            "error": str(e)
        }

def build_hermes_graph():
    """Build and compile the Hermes LangGraph with Graphify integration."""
    workflow = StateGraph(HermesState)
    
    # Add nodes
    workflow.add_node("graphify", graphify_node)
    workflow.add_node("sandbox_tool", sandbox_tool)
    
    # Set entry point to Graphify (runs before any tool)
    workflow.set_entry_point("graphify")
    
    # Define edges: Graphify -> sandbox_tool -> END
    workflow.add_edge("graphify", "sandbox_tool")
    workflow.add_edge("sandbox_tool", END)
    
    return workflow.compile()

# Example usage for testing
if __name__ == "__main__":
    # Initialize test state
    test_state = {
        "hermes_memory": {
            "agent_id": "hermes-001",
            "status": "active",
            "last_tool": None,
            "tool_count": 0
        },
        "shared_knowledge": {
            "project": "ai-ecosystem",
            "version": "1.0.0",
            "shared_tools": ["web_search", "file_read", "code_execute"],
            "environment": "development"
        },
        "input": {
            "tool": "web_search",
            "query": "latest AI agent frameworks",
            "max_results": 5
        },
        "output": None,
        "error": None
    }
    
    # Build and run the graph
    graph = build_hermes_graph()
    result = graph.invoke(test_state)
    
    print("=== Hermes Graph Execution Result ===")
    print(f"Final Output: {result['output']}")
    if result['error']:
        print(f"Error: {result['error']}")
    print("\nEnriched Input Keys:", list(result['input'].keys()))
    print("Hermes Context Keys:", list(result['input'].get('hermes_context', {}).keys()))
    print("Shared Context Keys:", list(result['input'].get('shared_context', {}).keys()))