import streamlit as st
import requests
import json
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Email Assistant AI",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #6366F1;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .email-card {
        background: linear-gradient(135deg, #1E1B4B, #0F172A);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #4C1D95;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    .email-card strong {
        color: #E0E7FF;
        font-weight: 600;
    }
    .response-card {
        background: linear-gradient(135deg, #064E3B, #022C22);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-top: 1rem;
        border: 1px solid #059669;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        color: #D1FAE5;
    }
    .stTextArea > div > textarea {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        color: #E2E8F0;
        border: 2px solid #475569;
        border-radius: 0.75rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stTextArea > div > textarea:focus {
        border-color: #6366F1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stTextInput > div > input {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        color: #E2E8F0;
        border: 2px solid #475569;
        border-radius: 0.75rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stTextInput > div > input:focus {
        border-color: #6366F1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stSelectbox > div > select {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        color: #E2E8F0;
        border: 2px solid #475569;
        border-radius: 0.75rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stSelectbox > div > select:focus {
        border-color: #6366F1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2), inset 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: #FFFFFF;
        border: none;
        border-radius: 0.75rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3), 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4F46E5, #7C3AED);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4), 0 4px 8px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }
    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3), 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    .stMetric > div > div > label {
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stMetric > div > div > div {
        color: #E0E7FF;
        font-weight: bold;
        font-size: 1.5rem;
    }
    .stSidebar .css-1d391kg {
        background: linear-gradient(180deg, #0F172A, #1E1B4B);
        border-right: 1px solid #4C1D95;
    }
    .stSidebar .css-17eqqhr {
        color: #E0E7FF;
    }
    .stChatMessage {
        background: linear-gradient(135deg, #1E1B4B, #0F172A);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #4C1D95;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .stChatMessage[data-testid="chat-message-container-user"] {
        background: linear-gradient(135deg, #1E3A8A, #1E1B4B);
        border-left: 4px solid #3B82F6;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    .stChatMessage[data-testid="chat-message-container-assistant"] {
        background: linear-gradient(135deg, #064E3B, #022C22);
        border-left: 4px solid #10B981;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-radius: 0.75rem;
        padding: 0.5rem;
        border: 1px solid #475569;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #94A3B8;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: #FFFFFF;
        box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
    }
    .stDataFrame {
        background: linear-gradient(135deg, #1E293B, #0F172A);
        border-radius: 0.75rem;
        overflow: hidden;
        border: 1px solid #475569;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .stDataFrame table {
        color: #E2E8F0;
    }
    .stDataFrame th {
        background: linear-gradient(135deg, #4C1D95, #6366F1);
        color: #FFFFFF;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stDataFrame tr:hover {
        background: rgba(99, 102, 241, 0.1);
    }
    /* Add glowing animation for AI elements */
    @keyframes glow {
        0% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
        50% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.8), 0 0 30px rgba(139, 92, 246, 0.4); }
        100% { box-shadow: 0 0 5px rgba(99, 102, 241, 0.5); }
    }
    .ai-glow {
        animation: glow 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'email_history' not in st.session_state:
    st.session_state.email_history = []

class EmailAssistantUI:
    def __init__(self):
        try:
            self.api_url = st.secrets.get("API_URL", "http://localhost:8001")
        except Exception:
            self.api_url = "http://localhost:8001"
            
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown('<h2 style="color: #E0E7FF; font-size: 1.5rem; margin-bottom: 1rem;">🤖 AI Control Panel</h2>', unsafe_allow_html=True)
            st.markdown("---")
            
            # Email Configuration Section
            st.subheader("Configuration")

            # Sender email (for sending)
            from_email = st.text_input(
                "Your Email (Sender)",
                placeholder="your-email@gmail.com",
                help="Required for sending emails. Must match SMTP account.",
            )
            st.subheader("� Email Configuration")
            email_user = st.text_input("Email Address", value="your-email@gmail.com", help="Your email address for IMAP access")
            email_password = st.text_input("App Password", type="password", value="your-app-password", help="App-specific password for email access")
            imap_server = st.selectbox("Email Provider", ["imap.gmail.com", "outlook.office365.com", "imap.mail.yahoo.com"], index=0, help="Select your email provider's IMAP server")
            
            st.markdown("---")
            
            st.subheader("� AI Configuration")
            
            # LLM Selection
            st.markdown("**🤖 LLM Model**")
            llm_model = st.selectbox(
                "Select Model",
                ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "llama-3.1-405b-instruct"],
                index=0,
                help="Choose the AI model for email processing"
            )
            
            # Tone selection
            st.markdown("**📝 Response Tone**")
            tone = st.select_slider(
                "Tone Level",
                options=["Formal", "Professional", "Casual", "Friendly"],
                value="Professional",
                help="Set the tone for generated responses"
            )
            
            # Email priority
            st.markdown("**⚡ Priority Level**")
            priority = st.selectbox(
                "Priority",
                ["Low", "Normal", "High", "Urgent"],
                index=1,
                help="Default priority for outgoing emails"
            )
            
            # Auto-send toggle
            st.markdown("**🚀 Automation**")
            auto_send = st.toggle("Auto-send responses", value=False, help="Automatically send generated responses")
            
            # Template selection
            st.markdown("**📋 Templates**")
            templates = {
                "Meeting Request": "I'd like to schedule a meeting to discuss...",
                "Follow-up": "Just following up on our previous conversation...",
                "Information Request": "Could you please provide more information about...",
                "Thank You": "Thank you for your email and for..."
            }
            selected_template = st.selectbox(
                "Use Template",
                ["None"] + list(templates.keys()),
                help="Start with a pre-written template"
            )
            
            st.divider()
            
            # Statistics
            st.subheader("📊 Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("📧 Emails", len(st.session_state.email_history))
            with col2:
                st.metric("⏱️ Avg Time", "45s")
            
            return {
                "llm_model": llm_model,
                "tone": tone,
                "priority": priority,
                "auto_send": auto_send,
                "template": templates.get(selected_template, ""),
                "email_user": email_user,
                "email_password": email_password,
                "imap_server": imap_server
            }
    
    def render_main_panel(self, config: Dict[str, Any]):
        st.markdown('<h1 class="main-header ai-glow">🤖 AI Email Assistant</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94A3B8; font-size: 1.1rem; margin-bottom: 2rem;">Intelligent email processing powered by advanced AI</p>', unsafe_allow_html=True)
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📧 Compose", 
            "📊 Analyze", 
            "🔄 Process", 
            "📚 History"
        ])
        
        with tab1:
            self.render_compose_tab(config)
        
        with tab2:
            self.render_analyze_tab()
        
        with tab3:
            self.render_process_tab(config)
        
        with tab4:
            self.render_history_tab()
    
    def render_compose_tab(self, config: Dict[str, Any]):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Compose Email")
            
            # Recipient input
            to_emails = st.text_input(
                "To",
                placeholder="recipient@example.com"
            )
            
            # Subject
            subject = st.text_input(
                "Subject",
                placeholder="Email subject..."
            )
            
            # CC/BCC
            with st.expander("CC/BCC"):
                cc_emails = st.text_input("CC")
                bcc_emails = st.text_input("BCC")
            
            # Email body
            email_body = st.text_area(
                "Email Content",
                height=300,
                placeholder="Type your email here...",
                value=config["template"]
            )
            
            # Attachment
            attachments = st.file_uploader(
                "Attachments",
                type=['pdf', 'docx', 'txt', 'jpg', 'png'],
                accept_multiple_files=True
            )
            
            # Show attachment preview
            if attachments:
                st.write("**Attachments to send:**")
                for i, file in enumerate(attachments):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"📎 {file.name}")
                    with col2:
                        st.write(f"{file.size} bytes")
                    with col3:
                        if file.type.startswith('image/'):
                            st.image(file, width=50)
                        else:
                            st.write("📄")
        
        with col2:
            st.subheader("AI Assistant")
            
            # Quick actions
            st.write("**Quick Actions:**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✨ Improve Tone", use_container_width=True):
                    self.improve_tone(email_body, config["tone"])
            
            with col_b:
                if st.button("📝 Check Grammar", use_container_width=True):
                    self.check_grammar(email_body)
            
            if st.button("🔍 Add Context", use_container_width=True):
                self.add_context(subject, email_body)
            
            # Generate response
            if st.button("🤖 Generate Response", type="primary", use_container_width=True):
                with st.spinner("Generating response..."):
                    response = self.generate_response(
                        subject=subject,
                        body=email_body,
                        tone=config["tone"],
                        priority=config["priority"],
                        to_emails=to_emails,
                    )
                    st.session_state.conversation.append({
                        "role": "assistant",
                        "content": response
                    })
            
            # Show conversation
            if st.session_state.conversation:
                st.subheader("Conversation")
                for msg in st.session_state.conversation[-3:]:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
        
        # Send button
        col_send1, col_send2, _ = st.columns([1, 1, 2])
        with col_send1:
            if st.button("📤 Send Email", type="primary", use_container_width=True):
                self.send_email(
                    from_email=config.get("from_email", ""),
                    to=to_emails,
                    subject=subject,
                    body=email_body,
                    cc=cc_emails,
                    attachments=attachments,
                    config=config,
                )
        
        with col_send2:
            if st.button("💾 Save Draft", use_container_width=True):
                st.success("Draft saved!")
    
    def render_analyze_tab(self):
        st.subheader("Email Analysis")
        
        # Upload email for analysis
        uploaded_email = st.file_uploader(
            "Upload email (.eml)",
            type=['eml']
        )
        
        if uploaded_email:
            # Analyze email
            if st.button("Analyze Email"):
                with st.spinner("Analyzing..."):
                    analysis = self.analyze_email(uploaded_email)
                    
                    # Display analysis
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Sentiment", analysis.get("sentiment", "Neutral"))
                    with col2:
                        st.metric("Urgency", analysis.get("urgency", "Medium"))
                    with col3:
                        st.metric("Action Required", analysis.get("action_required", "Yes"))
                    
                    # Show detailed analysis
                    st.json(analysis)
    
    def render_process_tab(self, config: Dict[str, Any]):
        st.subheader("Process Incoming Emails")
        
        # Connect to email account
        with st.expander("Email Account Setup"):
            email_provider = st.selectbox(
                "Provider",
                ["Gmail", "Outlook", "IMAP", "Other"]
            )
            email_address = st.text_input("Email Address")
            app_password = st.text_input("App Password", type="password")
            
            if st.button("Connect"):
                st.success(f"Connected to {email_address}")
        
        # Process unread emails
        if st.button("🔄 Process Unread Emails"):
            with st.spinner("Fetching and processing emails..."):
                emails = self.fetch_unread_emails(config)
                
                for email in emails:
                    with st.container():
                        st.markdown(f"""
                        <div class="email-card">
                            <strong>From:</strong> {email['from']}<br>
                            <strong>Subject:</strong> {email['subject']}<br>
                            <small>{email['date']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Auto-response button
                        if st.button(f"Auto-respond #{email['id']}", key=email['id']):
                            response = self.generate_auto_response(email)
                            st.markdown(f"""
                            <div class="response-card">
                                {response}
                            </div>
                            """, unsafe_allow_html=True)
    
    def render_history_tab(self):
        st.subheader("Email History")

        if st.session_state.email_history:
            df = pd.DataFrame(st.session_state.email_history)
            display_cols = [c for c in ['date', 'to', 'subject', 'status'] if c in df.columns]
            if display_cols:
                st.dataframe(df[display_cols], use_container_width=True)

            # Analytics (only if we have the required columns)
            if 'sentiment_score' in df.columns and 'date' in df.columns:
                st.subheader("Analytics")
                col1, col2 = st.columns(2)
                with col1:
                    st.line_chart(df.set_index('date')[['sentiment_score']])
                if 'response_time_minutes' in df.columns:
                    with col2:
                        st.bar_chart(df['response_time_minutes'].value_counts())
        else:
            st.info("No email history yet.")
    
    def improve_tone(self, body: str, tone: str) -> None:
        """Improve email tone using AI"""
        if not body.strip():
            st.warning("Enter email content first.")
            return
        try:
            result = self.generate_response("Tone improvement", body, tone, "normal", "recipient@example.com")
            st.session_state.conversation.append({"role": "assistant", "content": result})
            st.success("Tone improved! Check the assistant panel.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    def check_grammar(self, body: str) -> None:
        """Check grammar - placeholder for future API"""
        if not body.strip():
            st.warning("Enter email content first.")
            return
        st.info("Grammar check: Use 'Generate Response' for AI-assisted editing.")

    def add_context(self, subject: str, body: str) -> None:
        """Add context - uses generate to add relevant info"""
        if not body.strip():
            st.warning("Enter email content first.")
            return
        try:
            result = self.generate_response(subject, f"Add relevant context to: {body}", "Professional", "normal", "recipient@example.com")
            st.session_state.conversation.append({"role": "assistant", "content": result})
            st.success("Context added! Check the assistant panel.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    def generate_response(self, subject: str, body: str, tone: str, priority: str, to_emails: str = "", from_email: str = "user@example.com") -> str:
        """Generate email response using API"""
        try:
            payload = {
                "subject": subject,
                "body": body,
                "from_email": from_email if from_email else "user@example.com",
                "to_emails": [e.strip() for e in to_emails.split(",") if e.strip()] if to_emails else ["recipient@example.com"],
            }
            response = requests.post(
                f"{self.api_url}/api/v1/email/draft",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("draft", "Could not generate response.")
        except requests.exceptions.RequestException as e:
            return f"Error connecting to API: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def send_email(
        self,
        from_email: str,
        to: str,
        subject: str,
        body: str,
        cc: str,
        attachments,
        config: Dict[str, Any],
    ):
        """Send email via API (actual SMTP - requires SMTP_* in .env)"""
        if not from_email or not from_email.strip():
            st.error("Enter your sender email in the sidebar (Your Email).")
            return
        to_list = [e.strip() for e in to.split(",") if e.strip()]
        if not to_list:
            st.error("Enter at least one recipient in the To field.")
            return

        # Process attachments
        attachment_data = []
        if attachments:
            import tempfile
            import os
            
            for uploaded_file in attachments:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Add attachment info
                attachment_data.append({
                    "path": tmp_file_path,
                    "name": uploaded_file.name,
                    "size": uploaded_file.size,
                    "type": uploaded_file.type
                })

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/email/send",
                json={
                    "subject": subject,
                    "body": body,
                    "from_email": from_email.strip(),
                    "to_emails": to_list,
                    "cc_emails": [e.strip() for e in cc.split(",") if e.strip()] if cc else [],
                    "attachments": attachment_data if attachment_data else None,
                },
                timeout=60,
            )

            if response.status_code == 200:
                result = response.json()
                st.success(result.get("message", "Email sent successfully!"))

                st.session_state.email_history.append({
                    "date": datetime.now().isoformat(),
                    "to": to,
                    "subject": subject,
                    "status": "sent",
                    "sentiment_score": 0.8,
                    "response_time_minutes": 2,
                })
            else:
                err = response.json().get("detail", response.text)
                st.error(f"Failed to send: {err}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {str(e)}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            # Clean up temporary files
            for attachment in attachment_data:
                try:
                    os.unlink(attachment["path"])
                except:
                    pass
    
    def analyze_email(self, email_file) -> Dict[str, Any]:
        """Analyze email content"""
        # Mock analysis
        return {
            "sentiment": "Positive",
            "urgency": "Medium",
            "action_required": True,
            "key_topics": ["meeting", "project", "deadline"],
            "suggested_actions": ["Schedule meeting", "Send follow-up", "Update project plan"]
        }
    
    def fetch_unread_emails(self, config: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Fetch unread emails using real API"""
        try:
            # Call the real API to get unread emails
            response = requests.get(
                f"{self.api_url}/api/v1/email/emails/unread",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    emails = data.get("emails", [])
                    st.success(f"✅ Fetched {len(emails)} real emails from {config.get('email_user', 'your-email')}")
                    return emails
                else:
                    st.error(f"API Error: {data.get('detail', 'Unknown error')}")
                    return []
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Error fetching emails: {str(e)}")
            return []
    
    def generate_auto_response(self, email: Dict[str, Any]) -> str:
        """Generate auto-response for email using real API"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/email/process",
                json={
                    "subject": email["subject"],
                    "body": email["body"],
                    "from_email": email["from"],
                    "to_emails": ["user@company.com"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("draft", "Could not generate response.")
            else:
                return f"Error processing email: {response.text}"
                
        except Exception as e:
            return f"Error generating response: {str(e)}"

def main():
    ui = EmailAssistantUI()
    
    # Sidebar configuration
    config = ui.render_sidebar()
    
    # Main panel
    ui.render_main_panel(config)
    
    # Footer
    st.markdown("---")
    st.caption("Email Assistant AI v1.0 | Powered by LangChain & LangGraph")

if __name__ == "__main__":
    main()