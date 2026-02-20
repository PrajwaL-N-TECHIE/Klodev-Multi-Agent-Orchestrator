from langchain_google_genai import ChatGoogleGenerativeAI
from models.state import GraphState
from utils.governance import log_activity

# Initialize Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

def generate_linkedin(state: GraphState) -> GraphState:
    """Generates a LinkedIn post or DM aligned with assessment rubrics."""
    log_activity("Agent 4 (LinkedIn)", "Generating engagement-focused LinkedIn content", state)
    
    inputs = state.get("user_input", {})
    icp = state.get("icp_profile", {})
    
    # 👇 NEW: Extract the specific matched lead data from the state!
    # (Check your Agent 2 to confirm if the key is "matched_lead" or inside "icp_profile")
    matched_lead = state.get("matched_lead", {})
    lead_name = matched_lead.get("name", "the contact")
    company = matched_lead.get("company", "their company")
    
    target_role = icp.get('primary_demographic', 'Technology Leaders')
    
    # Format pain points safely
    pain_points_raw = icp.get('pain_points', ['scaling infrastructure and optimizing workflows'])
    pain_points = ", ".join(pain_points_raw) if isinstance(pain_points_raw, list) else pain_points_raw
    
    objective = inputs.get('business_behavior', 'build connections')

    # 👇 UPDATED PROMPT: Inject the real name and strictly forbid placeholders!
    prompt = f"""
    Write a highly engaging LinkedIn DM targeting: {target_role}.
    Business Objective: {objective}
    Target Pain Points: {pain_points}

    CRITICAL PERSONALIZATION (FOLLOW EXACTLY):
    - You are writing directly to {lead_name} who works at {company}.
    - DO NOT use placeholders like [Name], [Company], or [Insert Topic]. 
    - You MUST use the actual name "{lead_name}" and company "{company}" seamlessly in the message.

    CRITICAL REQUIREMENTS (FOLLOW EXACTLY):
    1. Tone: Must be professional yet conversational. Sound human, approachable, and insightful. Avoid stiff corporate jargon.
    2. Messaging: Must be engagement-focused. Start with a strong hook, offer real value, and ask a thought-provoking question to spark discussion.
    3. Call-To-Action (CTA): Must be a networking-optimized CTA (e.g., "Would love to connect," "Open to a quick virtual coffee?"). Do NOT use a hard sales pitch.
    
    Format: Keep it highly readable with short paragraphs or line breaks.
    """
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        status = "✅ LinkedIn content generated successfully"
    except Exception as e:
        content = f"Error generating LinkedIn content: {str(e)}"
        status = "❌ Failed to generate LinkedIn content"

    return {
        **state,
        "content_draft": content,
        "execution_status": status
    }