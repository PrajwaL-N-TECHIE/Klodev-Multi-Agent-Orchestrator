import os
import smtplib
import hashlib
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from langchain_google_genai import ChatGoogleGenerativeAI
from models.state import GraphState
from utils.governance import log_activity

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# ============================================
# DATABASE SETUP FOR TRACKING & FOLLOW-UPS
# ============================================

def init_database():
    """Create database tables for tracking emails and follow-ups in the main DB"""
    conn = sqlite3.connect('klodev.db')
    cursor = conn.cursor()
    
    # Ensure the email_tracking table exists in the main DB
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT UNIQUE,
            recipient_email TEXT,
            campaign TEXT,
            subject TEXT,
            sent_at TIMESTAMP,
            opened_at TIMESTAMP,
            opened_count INTEGER DEFAULT 0,
            campaign_name TEXT
        )
    ''')
    
    # Table for scheduling follow-ups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS follow_ups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_tracking_id TEXT,
            recipient_email TEXT,
            follow_up_date TIMESTAMP,
            follow_up_template TEXT,
            status TEXT DEFAULT 'pending',
            sent_at TIMESTAMP,
            FOREIGN KEY (original_tracking_id) REFERENCES email_tracking(tracking_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on module load
init_database()

# ============================================
# EMAIL TRACKING FUNCTIONS
# ============================================

def generate_tracking_id(email, subject):
    """Generate unique tracking ID for each email"""
    unique_string = f"{email}_{subject}_{datetime.now()}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]

def save_tracking_info(tracking_id, email, subject, campaign="general"):
    """Save email tracking information to main klodev database"""
    conn = sqlite3.connect('klodev.db')
    cursor = conn.cursor()
    
    # Use generic campaign name if subject is used as campaign fallback
    cursor.execute('''
        INSERT INTO email_tracking (tracking_id, recipient_email, subject, sent_at, campaign_name, campaign)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (tracking_id, email, subject, datetime.now(), campaign, campaign))
    
    conn.commit()
    conn.close()
    
    print(f"🔍 Tracking saved for email to {email} (ID: {tracking_id}) in klodev.db")

def add_tracking_pixel(email_content, tracking_id):
    """Add invisible tracking pixel to email"""
    pixel_url = f"http://localhost:5000/track/{tracking_id}.png"
    pixel_html = f'<img src="{pixel_url}" width="1" height="1" style="display:none;">'
    
    # Add to end of email
    return email_content + "\n" + pixel_html

# ============================================
# FOLLOW-UP SCHEDULER FUNCTIONS
# ============================================

def schedule_follow_up(original_tracking_id, recipient_email, days_delay, template_name="standard_follow_up"):
    """Schedule a follow-up email"""
    follow_up_date = datetime.now() + timedelta(days=days_delay)
    
    conn = sqlite3.connect('klodev.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO follow_ups (original_tracking_id, recipient_email, follow_up_date, follow_up_template, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (original_tracking_id, recipient_email, follow_up_date, template_name))
    
    conn.commit()
    conn.close()
    
    print(f"📅 Follow-up scheduled for {recipient_email} on {follow_up_date.strftime('%Y-%m-%d')} in klodev.db")

def generate_follow_up_content(original_email, template_name):
    """Generate follow-up email content using Gemini"""
    prompt = f"""
    Write a follow-up email based on this original email:
    
    Original Email: {original_email[:500]}...
    
    Template Type: {template_name}
    
    Requirements:
    - Be polite and not pushy
    - Reference the previous email
    - Add new value/case study
    - Clear call to action
    - Professional tone
    
    Return the complete follow-up email.
    """
    
    response = llm.invoke(prompt)
    return response.content.strip()

def process_follow_ups():
    """Background thread to process and send follow-ups"""
    while True:
        try:
            conn = sqlite3.connect('klodev.db')
            cursor = conn.cursor()
            
            # Find pending follow-ups that are due
            cursor.execute('''
                SELECT id, original_tracking_id, recipient_email, follow_up_template 
                FROM follow_ups 
                WHERE status='pending' AND follow_up_date <= ?
            ''', (datetime.now(),))
            
            due_follow_ups = cursor.fetchall()
            
            for fu in due_follow_ups:
                fu_id, original_tracking_id, recipient_email, template = fu
                
                # Get original email content
                cursor.execute('''
                    SELECT subject FROM email_tracking WHERE tracking_id = ?
                ''', (original_tracking_id,))
                original = cursor.fetchone()
                
                if original:
                    # Generate and send follow-up
                    follow_up_content = generate_follow_up_content(
                        f"Original subject: {original[0]}", 
                        template
                    )
                    
                    # Extract subject
                    lines = follow_up_content.split('\n')
                    subject = "Following up on our previous email"
                    for line in lines[:3]:
                        if line.lower().startswith('subject'):
                            subject = line.replace('Subject:', '').replace('subject:', '').strip()
                            break
                    
                    # Send the follow-up
                    sender_email = os.getenv("EMAIL_ADDRESS")
                    sender_password = os.getenv("EMAIL_APP_PASSWORD").replace(" ", "")
                    
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = recipient_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(follow_up_content, 'plain'))
                    
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                    server.quit()
                    
                    # Mark as sent
                    cursor.execute('''
                        UPDATE follow_ups SET status='sent', sent_at=? WHERE id=?
                    ''', (datetime.now(), fu_id))
                    
                    print(f"📧 Follow-up sent to {recipient_email}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Follow-up processor error: {e}")
        
        # Check every hour
        time.sleep(3600)

# Start follow-up processor in background thread
follow_up_thread = threading.Thread(target=process_follow_ups, daemon=True)
follow_up_thread.start()

# ============================================
# MAIN EMAIL GENERATION FUNCTION
# ============================================

# ============================================
# MAIN EMAIL GENERATION FUNCTION
# ============================================

def generate_email(state: GraphState) -> GraphState:
    log_activity("Agent 5 (Email)", "Drafting personalized email with tracking & follow-ups", state)
    
    inputs = state["user_input"]
    target_email = inputs.get("target_email", "klodevtest@gmail.com")
    icp = state["icp_profile"]
    
    # Extract specific target from Agent 2's DB Match
    target_name = "Professional"
    target_company = "your company"
    target_role = icp.get('primary_demographic', 'Executive')
    
    priority_leads = icp.get("priority_leads", [])
    if priority_leads and len(priority_leads) > 0:
        top_lead = priority_leads[0]
        target_name = top_lead.get("name", target_name)
        target_company = top_lead.get("company", target_company)
        target_role = top_lead.get("role", target_role)
    
    # Get business context
    business_context = inputs.get('business_behavior', 'Enterprise SaaS sales outreach')
    
    # 1. Draft the Content using Gemini
    prompt = f"""
    Write a professional, HYPER-PERSONALIZED sales cold email based on:
    - Intent: {inputs.get('user_intent', 'B2B outreach')}
    - Business Context: {business_context}
    
    TARGET RECIPIENT:
    - Name: {target_name}
    - Role: {target_role}
    - Company: {target_company}
    - General ICP Context: {icp.get('primary_demographic', 'C-level executives')}
    - Pain Points: {icp.get('pain_points', ['digital transformation', 'efficiency', 'growth'])}
    
    YOUR NAME: Prajwal
    YOUR TITLE: Lead Solutions Architect
    YOUR COMPANY: Klodev Nexus
    
    Include:
    - Compelling subject line (start with "Subject:"). Try to include {target_company} in the subject if it makes sense.
    - Personalized greeting: "Hi {target_name}," or "Dear {target_name},"
    - Icebreaker: Specifically mention their role as {target_role} at {target_company} to show you aren't sending a generic blast.
    - Clear value proposition addressing their pain points
    - Call to action for a demo
    - Professional signature with your details
    
    Make it persuasive but professional.
    """
    
    response = llm.invoke(prompt)
    email_content = response.content.strip()
    
    # 2. Extract subject line
    lines = email_content.split('\n')
    subject = f"Information about AI Analytics for {target_company}"
    for line in lines[:3]:
        if line.lower().startswith('subject'):
            subject = line.replace('Subject:', '').replace('subject:', '').strip()
            # Remove subject line from content
            email_content = email_content.replace(line, '', 1).strip()
            break
    
    # 3. Generate tracking ID
    tracking_id = generate_tracking_id(target_email, subject)
    
    # 4. Add tracking pixel
    email_with_tracking = add_tracking_pixel(email_content, tracking_id)
    
    # 5. Save tracking info (Now goes to klodev.db)
    save_tracking_info(tracking_id, target_email, subject, campaign="enterprise_outreach")
    
    # 6. ACTUALLY SEND THE EMAIL
    try:
        sender_email = os.getenv("EMAIL_ADDRESS")
        sender_password = os.getenv("EMAIL_APP_PASSWORD").replace(" ", "")
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = target_email
        msg['Subject'] = subject
        msg.attach(MIMEText(email_with_tracking, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        execution_status = f"✅ Email successfully sent to {target_email} with tracking ID: {tracking_id}"
        log_activity("Agent 5 (Email)", f"Email sent to {target_email} with tracking", state)
        print(f"📧 Email sent to {target_email} (Tracking: {tracking_id})")
        
        # 7. Schedule follow-ups (3 days, 7 days, 14 days)
        schedule_follow_up(tracking_id, target_email, 3, "gentle_reminder")
        schedule_follow_up(tracking_id, target_email, 7, "case_study")
        schedule_follow_up(tracking_id, target_email, 14, "final_opportunity")
        print(f"📅 3 follow-ups scheduled for {target_email}")
        
    except Exception as e:
        execution_status = f"❌ Failed to send email: {str(e)}"
        print(f"❌ Email error: {str(e)}")
    
    # 8. Prepare email for display (without tracking pixel)
    return {
        "content_draft": email_content,
        "execution_status": execution_status,
        "tracking_id": tracking_id,
        "follow_ups_scheduled": "3 (3, 7, 14 days)"
    }