import hashlib
from datetime import datetime

def rbac_check(user_role: str, required_role: str = "Marketing_User") -> bool:
    """Enforces Role-Based Access Control (RBAC) hierarchy."""
    roles = {"Viewer": 1, "Marketing_User": 2, "Admin": 3}
    
    user_level = roles.get(user_role, 0)
    required_level = roles.get(required_role, 2)
    
    if user_level < required_level:
        raise PermissionError(f"Access Denied: '{user_role}' lacks required permissions.")
    return True

def log_activity(agent_name: str, action: str, state: dict) -> dict:
    """Creates prompt logging and audit trails with cryptographic hashes."""
    timestamp = datetime.now().isoformat()
    raw_log = f"[{timestamp}] {agent_name} executed: {action}"
    
    # Generate an MD5 Hash simulating encrypted data records
    log_hash = hashlib.md5(raw_log.encode()).hexdigest()
    secure_log_entry = f"{raw_log} | Hash: {log_hash}"
    
    if "audit_trail" not in state:
        state["audit_trail"] = []
        
    state["audit_trail"].append(secure_log_entry)
    return state

def human_approval_node(state: dict) -> dict:
    """
    A Human-in-the-loop (HITL) pause node for AI Governance. 
    In LangGraph, this allows the system to pause and wait for an admin
    to review the content before executing distribution.
    """
    log_activity("Governance Gate", "Content drafted. Pending human review before distribution.", state)
    
    # In a full production app, this would pause and wait for UI input.
    # For this Flask assessment demo, we simulate the approval flag being checked.
    state["is_approved"] = True 
    
    return state