from langgraph.graph import StateGraph, START, END
from models.state import GraphState
from agents.agent_1_classifier import classify_input
from agents.agent_2_icp_rag import match_icp
from agents.agent_3_router import route_platform
from agents.agent_4_linkedin import generate_linkedin
from agents.agent_5_email import generate_email
from agents.agent_6_call import generate_call
from utils.governance import human_approval_node

def route_logic(state: GraphState) -> str:
    """Reads the 'next_node' state and tells LangGraph where to go."""
    return state["next_node"]

def build_advanced_graph():
    workflow = StateGraph(GraphState)
    
    # 1. Add all nodes
    workflow.add_node("classify", classify_input)
    workflow.add_node("icp_match", match_icp)
    workflow.add_node("router", route_platform)
    
    # Specialized output channels
    workflow.add_node("route_to_linkedin", generate_linkedin)
    workflow.add_node("route_to_email", generate_email)
    workflow.add_node("route_to_call", generate_call)
    
    # Governance node
    workflow.add_node("governance_check", human_approval_node)
    
    # 2. Add standard edges
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", "icp_match")
    workflow.add_edge("icp_match", "router")
    
    # 3. ADVANCED: Add Conditional Edges based on Agent 3's decision
    workflow.add_conditional_edges(
        "router", 
        route_logic, # The function that checks the state
        {
            "route_to_linkedin": "route_to_linkedin",
            "route_to_email": "route_to_email",
            "route_to_call": "route_to_call"
        }
    )
    
    # 4. Route all generation nodes to Governance
    workflow.add_edge("route_to_linkedin", "governance_check")
    workflow.add_edge("route_to_email", "governance_check")
    workflow.add_edge("route_to_call", "governance_check")
    workflow.add_edge("governance_check", END)
    
    return workflow.compile()