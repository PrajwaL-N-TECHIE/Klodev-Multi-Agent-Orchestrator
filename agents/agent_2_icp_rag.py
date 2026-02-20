from langchain_google_genai import ChatGoogleGenerativeAI
from models.state import GraphState
from utils.governance import log_activity
import json
import re
import sqlite3

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

def get_contacts_from_db():
    """Helper to fetch real leads from the local database."""
    try:
        conn = sqlite3.connect('klodev.db')
        c = conn.cursor()
        # Fetching key data points for the AI to analyze
        c.execute("SELECT name, role, company, email, phone, lead_score FROM contacts")
        contacts = c.fetchall()
        conn.close()
        
        # Format into a readable string for the LLM
        contact_list = []
        for contact in contacts:
            contact_list.append(
                f"Name: {contact[0]}, Role: {contact[1]}, Company: {contact[2]}, "
                f"Email: {contact[3]}, Phone: {contact[4]}, Lead Score: {contact[5]}"
            )
        return "\n".join(contact_list)
    except Exception as e:
        print(f"⚠️ Database error: {e}")
        return "No contacts found or database error."

def match_icp(state: dict) -> dict:
    """Agent 2: Match classification with ICP profiles and prioritize real database leads"""
    
    classification = state.get("classification", "Unknown")
    
    log_activity("Agent 2 (ICP Module)", f"Matching category: {classification} against real DB leads", state)
    
    # 1. Fetch real leads from the database
    db_contacts = get_contacts_from_db()
    
    # 2. Inject both the classification AND the real leads into the prompt
    prompt = f"""
    You are Agent 2: ICP Module.
    Your task is to analyze the classified category: '{classification}' and match it against our database of leads to identify priority targets.
    
    Here are the leads currently in our database:
    {db_contacts}
    
    Return a detailed ICP profile in valid JSON format with these exact keys:
    - primary_demographic (detailed description of target audience)
    - pain_points (list of 3-5 specific pain points)
    - business_objectives (list of 2-3 objectives)
    - historical_best_channel (one of: 'route_to_linkedin', 'route_to_email', 'route_to_call')
    - priority_leads (Select the top 1-3 contacts from the database provided above who are the best match for this ICP. Include their 'name', 'company', 'role', 'email', 'phone', and a brief 'reason_for_match'.)
    
    Example format:
    {{
        "primary_demographic": "CTO, VPs of Engineering at Enterprise SaaS companies",
        "pain_points": ["Legacy system integration", "Scalability issues", "Security compliance"],
        "business_objectives": ["Digital transformation", "Cost reduction", "Innovation acceleration"],
        "historical_best_channel": "route_to_linkedin",
        "priority_leads": [
            {{
                "name": "Rahul Sharma",
                "company": "Tech Mahindra",
                "role": "CTO",
                "email": "rahul.sharma@techmahindra.com",
                "phone": "+919876543210",
                "reason_for_match": "High lead score (95) and CTO role aligns perfectly with enterprise software decision-making."
            }}
        ]
    }}
    
    Return ONLY the JSON, no other text.
    """
    
    try:
        response = llm.invoke(prompt)
        # Extract JSON from response
        json_str = response.content.strip()
        # Remove markdown code blocks if present
        json_str = re.sub(r'```json\s*|\s*```', '', json_str)
        icp_data = json.loads(json_str)
        
        # Log the successful match to the console
        if icp_data.get("priority_leads") and len(icp_data["priority_leads"]) > 0:
            top_lead = icp_data["priority_leads"][0]
            print(f"🎯 Matched Top Lead: {top_lead['name']} from {top_lead['company']} (Score: {top_lead.get('reason_for_match', 'N/A')})")
            
            # Optional: Dynamically update the state with the real target's contact info
            # so Agents 4, 5, and 6 actually contact this specific person!
            if "user_input" in state:
                state["user_input"]["target_email"] = top_lead.get("email", state["user_input"].get("target_email"))
                state["user_input"]["target_phone"] = top_lead.get("phone", state["user_input"].get("target_phone"))
                
    except Exception as e:
        print(f"⚠️ ICP parsing error: {e}")
        # Default ICP data if it fails
        icp_data = {
            "primary_demographic": "Senior IT/Technology Leadership",
            "pain_points": ["Struggling to operationalize AI at scale"],
            "business_objectives": ["Digital transformation"],
            "historical_best_channel": "route_to_email",
            "priority_leads": []
        }
    
    return {**state, "icp_profile": icp_data}