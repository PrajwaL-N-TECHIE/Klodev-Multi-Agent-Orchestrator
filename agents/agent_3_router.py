from langchain_google_genai import ChatGoogleGenerativeAI
from models.state import GraphState
from utils.governance import log_activity
import os
import re

# Using flash for fast, logical routing decisions
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

def route_platform(state: dict) -> dict:
    """Agent 3: Determine the most effective communication channel"""
    
    # Get inputs safely
    user_input = state.get("user_input", {})
    icp_profile = state.get("icp_profile", {})
    
    log_activity("Agent 3 (Platform Decision)", "Evaluating channels based on urgency and ICP preferences", state)
    
    # Extract values with safe defaults
    urgency = user_input.get('urgency', 'Medium')
    business_behavior = user_input.get('business_behavior', '')
    user_intent = user_input.get('user_intent', '')
    target_phone = user_input.get('target_phone', '')
    
    # 🛡️ THE FIX: Use regex to match exact whole words only (\b means word boundary)
    call_keywords = [r'\bcall me\b', r'\bphone\b', r'\bring\b', r'\bdial\b', r'\bcall now\b', r'\burgent call\b', r'\bcall\b']
    text_to_check = (business_behavior + ' ' + user_intent).lower()
    
    wants_call = any(re.search(pattern, text_to_check) for pattern in call_keywords)
    
    # Check if phone number is provided
    has_phone = bool(target_phone and target_phone.strip())
    
    # Get ICP preferences
    icp_demographic = icp_profile.get('primary_demographic', '')
    historical_channel = icp_profile.get('historical_best_channel', 'route_to_email')
    
    prompt = f"""
    You are Agent 3: Platform Decision Agent.
    Determine the most effective communication channel for content delivery.
    
    Decision Factors:
    - Task urgency: {urgency}
    - ICP communication preferences: {icp_demographic}
    - Historical engagement data / Best Channel: {historical_channel}
    - Phone number available: {'YES' if has_phone else 'NO'}
    - User explicitly requested call: {'YES' if wants_call else 'NO'}
    - Business objective: {business_behavior[:200]}
    
    CRITICAL RULES:
    1. If user explicitly asked for a call (User explicitly requested call: YES), choose 'route_to_call'
    2. If this is a high urgency task with phone number available, prioritize 'route_to_call'
    3. For thought leadership/content marketing, choose 'route_to_linkedin'
    4. For nurturing sequences/detailed information, choose 'route_to_email'
    
    Output exactly one of: 'route_to_linkedin', 'route_to_email', or 'route_to_call'
    Do not output any other text.
    """
    
    try:
        response = llm.invoke(prompt)
        decision = response.content.strip().lower()
    except Exception as e:
        print(f"⚠️ LLM error, using fallback: {e}")
        # Fallback logic
        if wants_call and has_phone:
            decision = 'route_to_call'
        elif 'linkedin' in business_behavior.lower() or 'thought leadership' in business_behavior.lower():
            decision = 'route_to_linkedin'
        else:
            decision = 'route_to_email'
    
    # Validate decision
    valid_routes = ['route_to_linkedin', 'route_to_email', 'route_to_call']
    if decision not in valid_routes:
        decision = 'route_to_email'
    
    # Override for explicit call requests
    if wants_call and has_phone:
        decision = 'route_to_call'
        print("📞 Explicit call request detected - forcing CALL channel")
    
    log_activity("Agent 3 (Platform Decision)", f"Selected channel: {decision}", state)
    print(f"🤖 Agent 3 autonomously decided: {decision}")
    
    # Return with next_node
    return {**state, "next_node": decision}