import os
import requests
import webbrowser
from urllib.parse import urlencode
from flask import request, redirect, session
from langchain_google_genai import ChatGoogleGenerativeAI
from models.state import GraphState
from utils.governance import log_activity
import json

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

class LinkedInPoster:
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:5000/auth/linkedin/callback")
        self.access_token = None
        self.person_urn = None
        self.token_expires_at = None
        
    def get_auth_url(self):
        """Generate LinkedIn OAuth URL"""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': 'random_state_string',  # In production, use secure random
            'scope': 'w_member_social r_member_social openid profile email'
        }
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(token_url, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            # Token expires in 60 days for non-MDP partners [citation:5]
            return True
        return False
    
    def get_person_urn(self):
        """Get person URN from userinfo endpoint"""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get('https://api.linkedin.com/v2/userinfo', headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            # Convert sub to person URN format [citation:10]
            self.person_urn = f"urn:li:person:{user_info['sub']}"
            return self.person_urn
        return None
    
    def create_post(self, content):
        """Create a LinkedIn post using Posts API [citation:1][citation:10]"""
        if not self.access_token or not self.person_urn:
            return {"error": "Not authenticated with LinkedIn"}
        
        url = "https://api.linkedin.com/rest/posts"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'LinkedIn-Version': '202601',  # Use latest version [citation:10]
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "author": self.person_urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            return {"success": True, "post_id": response.json().get('id')}
        else:
            return {"success": False, "error": response.text}

# Initialize LinkedIn poster
linkedin_poster = LinkedInPoster()

def generate_linkedin_post(state: GraphState) -> GraphState:
    """Agent 7: Generate and post to LinkedIn"""
    log_activity("Agent 7 (LinkedIn Poster)", "Generating and posting LinkedIn content", state)
    
    inputs = state["user_input"]
    icp = state["icp_profile"]
    
    # Check if we have LinkedIn credentials
    if not os.getenv("LINKEDIN_CLIENT_ID") or not os.getenv("LINKEDIN_CLIENT_SECRET"):
        return {
            "content_draft": "LinkedIn credentials not configured. Please set up LinkedIn API keys.",
            "execution_status": "❌ LinkedIn posting unavailable - missing credentials"
        }
    
    # Generate content using Gemini
    prompt = f"""
    You are a LinkedIn content expert. Create a professional, engaging LinkedIn post based on:
    
    Business Context: {inputs.get('business_behavior', '')}
    Target Audience: {icp.get('primary_demographic', 'C-level executives')}
    Pain Points: {icp.get('pain_points', ['digital transformation'])}
    
    REQUIREMENTS:
    1. Professional but conversational tone
    2. Include 3-5 bullet points or numbered insights
    3. End with a question to encourage engagement
    4. Use relevant hashtags (3-5)
    5. Keep it under 1500 characters
    6. Format with line breaks for readability
    
    Return ONLY the post content, no explanations.
    """
    
    response = llm.invoke(prompt)
    post_content = response.content.strip()
    
    # Try to post to LinkedIn
    try:
        if linkedin_poster.access_token and linkedin_poster.person_urn:
            result = linkedin_poster.create_post(post_content)
            if result.get('success'):
                execution_status = f"✅ LinkedIn post published successfully! Post ID: {result.get('post_id')}"
            else:
                execution_status = f"❌ Failed to post: {result.get('error')}"
        else:
            execution_status = "⚠️ LinkedIn not authenticated. Content generated but not posted."
            
    except Exception as e:
        execution_status = f"❌ Error posting to LinkedIn: {str(e)}"
    
    return {
        "content_draft": post_content,
        "execution_status": execution_status,
        "platform": "LINKEDIN"
    }