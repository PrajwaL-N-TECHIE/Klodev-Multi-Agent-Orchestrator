from langchain_google_genai import ChatGoogleGenerativeAI
from models.state import GraphState
from utils.governance import log_activity

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)

def classify_input(state: dict) -> dict:
    """Agent 1: Classify user input"""
    
    user_input = state.get("user_input", {})
    
    time_context = user_input.get('time', '')
    location = user_input.get('location', '')
    business_behavior = user_input.get('business_behavior', '')
    user_intent = user_input.get('user_intent', '')
    
    log_activity("Agent 1 (Classifier)", "Classifying user data", state)
    
    prompt = f"""
    You are Agent 1: Classification Agent.
    Classify the task based on the following input parameters:
    
    Time: {time_context}
    Location: {location}
    Business behavior: {business_behavior}
    User intent: {user_intent}
    
    Provide a concise category name (e.g., 'Enterprise Software Sales', 'Local B2B Outreach').
    Return ONLY the category name. Do not add any extra text.
    """
    
    try:
        response = llm.invoke(prompt)
        category = response.content.strip()
    except Exception as e:
        print(f"⚠️ Classification error: {e}")
        category = "Enterprise SaaS Outreach"
    
    return {**state, "classification": category}