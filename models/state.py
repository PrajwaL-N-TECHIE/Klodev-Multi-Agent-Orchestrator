from typing import TypedDict, Dict, Any, List

class GraphState(TypedDict):
    user_input: Dict[str, Any]  # Needs to include: target_email, target_phone
    classification: str         
    icp_profile: Dict[str, Any] 
    next_node: str              
    content_draft: str          
    execution_status: str       # NEW: Did the email/call actually send?
    audit_trail: List[str]      
    is_approved: bool