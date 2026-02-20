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
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        margin-bottom: 2rem;
    }
    .email-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .response-card {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
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
            self.api_url = st.secrets.get("API_URL", "http://localhost:8000")
        except Exception:
            self.api_url = "http://localhost:8000"
            
    
    def render_sidebar(self):
        with st.sidebar:
            st.title("✉️ Email Assistant")
            
            st.subheader("Configuration")

            # Sender email (for sending)
            from_email = st.text_input(
                "Your Email (Sender)",
                placeholder="your-email@gmail.com",
                help="Required for sending emails. Must match SMTP account.",
            )

            # LLM Selection
            llm_model = st.selectbox(
                "LLM Model",
                ["llama-3.1-8b-instant", "llama-3.1-70b-versatile", "llama-3.1-405b-instruct"],
                index=0
            )
            
            # Tone selection
            tone = st.select_slider(
                "Response Tone",
                options=["Formal", "Professional", "Casual", "Friendly"],
                value="Professional" 
            )
            
            # Email priority
            priority = st.selectbox(
                "Priority",
                ["Low", "Normal", "High", "Urgent"],
                index=1
            )
            
            # Auto-send toggle
            auto_send = st.toggle("Auto-send responses", value=False)
            
            # Template selection
            templates = {
                "Meeting Request": "I'd like to schedule a meeting to discuss...",
                "Follow-up": "Just following up on our previous conversation...",
                "Information Request": "Could you please provide more information about...",
                "Thank You": "Thank you for your email and for..."
            }
            selected_template = st.selectbox(
                "Use Template",
                ["None"] + list(templates.keys())
            )
            
            st.divider()
            
            # Statistics
            st.subheader("Statistics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Emails Processed", len(st.session_state.email_history))
            with col2:
                st.metric("Avg Response Time", "45s")
            
            return {
                "llm_model": llm_model,
                "tone": tone,
                "priority": priority,
                "auto_send": auto_send,
                "template": templates.get(selected_template, ""),
                "from_email": from_email or "",
            }
    
    def render_main_panel(self, config: Dict[str, Any]):
        st.title("Email Assistant AI Dashboard")
        
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
            self.render_process_tab()
        
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
    
    def render_process_tab(self):
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
                emails = self.fetch_unread_emails()
                
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

        try:
            response = requests.post(
                f"{self.api_url}/api/v1/email/send",
                json={
                    "subject": subject,
                    "body": body,
                    "from_email": from_email.strip(),
                    "to_emails": to_list,
                    "cc_emails": [e.strip() for e in cc.split(",") if e.strip()] if cc else [],
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
    
    def fetch_unread_emails(self) -> list[Dict[str, Any]]:
        """Fetch unread emails"""
        # Mock data
        return [
            {
                "id": "1",
                "from": "client@company.com",
                "subject": "Project Update Request",
                "date": "2024-01-15",
                "body": "Can you provide an update on the project timeline?"
            }
        ]
    
    def generate_auto_response(self, email: Dict[str, Any]) -> str:
        """Generate auto-response for email"""
        return f"""
        Thank you for your email regarding "{email['subject']}".
        
        I'll look into this and get back to you with an update shortly.
        
        Best regards,
        AI Assistant
        """

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