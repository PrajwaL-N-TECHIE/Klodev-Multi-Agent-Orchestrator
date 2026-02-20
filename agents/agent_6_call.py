import os
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from models.state import GraphState
from utils.governance import log_activity

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

def generate_call(state: GraphState) -> GraphState:
    """ONLY generates the call script/instructions. Does NOT dial."""
    log_activity("Agent 6 (Call)", "Drafting call instructions for human review", state)
    
    inputs = state["user_input"]
    icp = state["icp_profile"]
    
    # Extract specific target
    target_phone = inputs.get("target_phone", os.getenv("TEST_PHONE", "+919843315832"))
    
    # 1. Draft the AI's "Brain" (The Script/Instructions)
    # 1. Draft the AI's "Brain" (The Script/Instructions)
    prompt = f"""
    Write a literal, word-for-word cold call script. 
    - Intent: {inputs.get('user_intent')}
    - Target: {icp.get('primary_demographic', 'Decision makers')}
    - Pain Points: {icp.get('pain_points', ['business challenges'])}
    
    CRITICAL RULES:
    1. Write ONLY the exact spoken words of the script. 
    2. Do NOT include any guidelines, timestamps, rule lists, or director notes.
    3. Make it natural, conversational, and respectful of Indian business culture.
    4. Start with: "Hi, this is Maya calling on behalf of Klodev Apex..."
    """
    
    try:
        response = llm.invoke(prompt)
        ai_instructions = response.content.strip()
        execution_status = f"✅ Call script generated. Pending human approval to dial {target_phone}."
    except Exception as e:
        ai_instructions = "Error generating script."
        execution_status = f"❌ Failed to generate script: {str(e)}"
        print(f"❌ Error: {str(e)}")

    # Return just the draft so the UI can display it for approval
    return {
        **state,
        "content_draft": ai_instructions,
        "execution_status": execution_status
    }

def dispatch_live_call(phone_number: str, script: str):
    """The actual trigger that makes the phone ring via Bland AI."""
    try:
        bland_api_key = os.getenv("BLAND_API_KEY")
        
        headers = {'authorization': bland_api_key, 'Content-Type': 'application/json'}
        payload = {
            "phone_number": phone_number,
            "task": f"You are a professional sales agent. Follow these instructions: {script}",
            "voice": "maya",
            "record": True,
            "max_duration": 120,
            "language": "en-IN"
        }
        
        print(f"📞 Human approved! Dispatching LIVE call to: {phone_number}")
        
        api_response = requests.post(
            'https://api.bland.ai/v1/calls',
            json=payload,
            headers=headers
        )
        
        if api_response.status_code == 200:
            call_data = api_response.json()
            print(f"✅ Call initiated! Call ID: {call_data.get('call_id')}")
            return {"status": "success", "message": f"Live call dispatched to {phone_number}!"}
        else:
            print(f"❌ Voice API Error: {api_response.text}")
            return {"status": "error", "message": f"API Error: {api_response.text}"}
            
    except Exception as e:
        print(f"❌ Failed to initiate call: {str(e)}")
        return {"status": "error", "message": str(e)}