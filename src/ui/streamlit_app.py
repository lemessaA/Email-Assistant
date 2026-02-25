import streamlit as st
import requests
import json
import time
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Email Assistant",
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
            self.api_url = st.secrets.get("API_URL", "http://localhost:8000")
        except Exception:
            self.api_url = "http://localhost:8000"
            
    
    def render_sidebar(self):
        with st.sidebar:
            st.markdown('<h2 style="color: #E0E7FF; font-size: 1.5rem; margin-bottom: 1rem;">🤖 🔛</h2>', unsafe_allow_html=True)
            st.markdown("---")
            
            # Email Configuration Section
            st.subheader("Configuration")

            # Sender email (for sending)
            from_email = st.text_input(
                "Your Email (Sender)",
                placeholder="your-email@gmail.com",
                help="Required for sending emails. Must match SMTP account.",
            )
            
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
            
            # Data Management
            st.markdown("---")
            st.subheader("🗂️ Data Management")
            
            if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True, help="Clear all conversation and email history"):
                if st.session_state.conversation or st.session_state.email_history:
                    st.session_state.conversation.clear()
                    st.session_state.email_history.clear()
                    st.success("✅ All data cleared!")
                    st.rerun()
                else:
                    st.info("No data to clear.")
            
            # Show data counts
            col_data1, col_data2 = st.columns(2)
            with col_data1:
                st.metric("💬 Messages", len(st.session_state.conversation))
            with col_data2:
                st.metric("📧 History", len(st.session_state.email_history))
            
            return {
                "llm_model": llm_model,
                "from_email":from_email,
                "tone": tone,
                "priority": priority,
                "auto_send": auto_send,
                "template": templates.get(selected_template, ""),
                
                
                
            }
    
    def render_main_panel(self, config: Dict[str, Any]):
        st.markdown('<h1 class="main-header ai-glow">🤖 Assist Me for My Email </h1>', unsafe_allow_html=True)
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
                col_conv, col_clear = st.columns([4, 1])
                with col_conv:
                    st.subheader("💬 Conversation")
                with col_clear:
                    if st.button("🗑️", key="clear_conversation", help="Clear conversation"):
                        st.session_state.conversation.clear()
                        st.success("✅ Conversation cleared!")
                        st.rerun()
                
                for msg in st.session_state.conversation[-3:]:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                
                if len(st.session_state.conversation) > 3:
                    st.caption(f"Showing last 3 of {len(st.session_state.conversation)} messages")
        
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
        st.subheader("🔄 Real-Time Email Processing")
        
        # Auto-refresh controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=True, help="Automatically check for new emails")
        with col2:
            refresh_interval = st.selectbox("Interval", [30, 60, 300], index=1, help="Refresh interval in seconds")
        with col3:
            if st.button("🔍 Check Now", use_container_width=True):
                email_config = st.session_state.get('email_config')
                if not email_config or not email_config.get('email_user'):
                    st.warning("Configure your email account first (see Email Account Setup below).")
                else:
                    with st.spinner("Fetching emails…"):
                        emails = self.fetch_unread_emails(email_config)
                        st.session_state.current_emails = emails
                        st.session_state.new_email_count = len(emails)
                        st.session_state.last_check = time.time()
                        if emails:
                            st.success(f"📬 Found {len(emails)} email(s)!")
                        else:
                            st.info("📭 No new emails found.")
                    st.rerun()
        
        # Connection status
        if auto_refresh:
            # Auto-refresh logic
            if 'last_check' not in st.session_state:
                st.session_state.last_check = 0

            # Use saved email credentials (from the Account Setup expander)
            # Fall back gracefully if no credentials have been configured yet.
            email_config = st.session_state.get('email_config')

            if not email_config or not email_config.get('email_user'):
                st.warning(
                    "⚠️ No email account configured. "
                    "Expand **Email Account Setup** below, enter your credentials, "
                    "and click **Save Config** to enable auto-fetch."
                )
            else:
                current_time = time.time()
                if current_time - st.session_state.last_check > refresh_interval:
                    st.session_state.last_check = current_time
                    with st.spinner("🔍 Checking for new emails..."):
                        emails = self.fetch_unread_emails(email_config)
                        st.session_state.current_emails = emails
                        st.session_state.new_email_count = len(emails)

                        if len(emails) > 0:
                            st.success(f"📬 Found {len(emails)} new email(s)!")
                            st.balloons()
                        else:
                            st.info("📭 No new emails found.")
        else:
            st.info("🔄 Auto-refresh is disabled. Click 'Check Now' to manually check.")
        
        # Email account setup
        with st.expander("🔧 Email Account Setup"):
            col1, col2 = st.columns(2)
            with col1:
                email_provider = st.selectbox(
                    "Provider",
                    ["Gmail", "Outlook", "IMAP", "Other"],
                    key="email_provider"
                )
                imap_server = st.selectbox(
                    "IMAP Server",
                    ["imap.gmail.com", "outlook.office365.com", "imap.mail.yahoo.com", "custom"],
                    key="imap_server"
                )
            with col2:
                email_address = st.text_input("Email Address", key="email_address")
                app_password = st.text_input("App Password", type="password", key="app_password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔗 Connect & Test", use_container_width=True):
                    # Test connection
                    test_config = {
                        "email_user": email_address,
                        "email_password": app_password,
                        "imap_server": imap_server
                    }
                    test_emails = self.fetch_unread_emails(test_config)
                    if test_emails is not None:
                        st.success(f"✅ Successfully connected to {email_address}")
                        st.session_state.email_config = test_config
                    else:
                        st.error("❌ Connection failed. Check credentials.")
            
            with col2:
                if st.button("💾 Save Config", use_container_width=True):
                    st.session_state.email_config = {
                        "email_user": email_address,
                        "email_password": app_password,
                        "imap_server": imap_server
                    }
                    st.success("💾 Configuration saved!")
        
        # Email Status Dashboard
        st.markdown("---")
        st.subheader("📊 Email Status Dashboard")
        
        # Initialize email tracking if not exists
        if 'email_stats' not in st.session_state:
            st.session_state.email_stats = {
                'total_fetched': 0,
                'total_processed': 0,
                'total_incoming': 0,
                'processed_ids': set(),
                'incoming_ids': set(),
                'fetched_ids': set()
            }
        
        # Update stats with current emails
        if 'current_emails' in st.session_state and st.session_state.current_emails:
            current_ids = set(email['id'] for email in st.session_state.current_emails)
            
            # Track incoming (new) emails
            new_incoming = current_ids - st.session_state.email_stats['fetched_ids']
            st.session_state.email_stats['incoming_ids'].update(new_incoming)
            st.session_state.email_stats['total_incoming'] = len(st.session_state.email_stats['incoming_ids'])
            
            # Track fetched emails
            st.session_state.email_stats['fetched_ids'].update(current_ids)
            st.session_state.email_stats['total_fetched'] = len(st.session_state.email_stats['fetched_ids'])
        
        # Display status metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "📥 Incoming", 
                st.session_state.email_stats['total_incoming'],
                delta=st.session_state.email_stats['total_incoming'] - st.session_state.email_stats.get('last_incoming', 0),
                delta_color="normal"
            )
        with col2:
            st.metric("📤 Fetched", st.session_state.email_stats['total_fetched'])
        with col3:
            st.metric("✅ Processed", st.session_state.email_stats['total_processed'])
        with col4:
            pending = st.session_state.email_stats['total_incoming'] - st.session_state.email_stats['total_processed']
            st.metric("⏳ Pending", pending, delta_color="inverse" if pending > 0 else "normal")
        
        # Store last incoming count for delta
        st.session_state.email_stats['last_incoming'] = st.session_state.email_stats['total_incoming']
        
        st.markdown("---")
        
        # Display current emails with status
        if 'current_emails' in st.session_state and st.session_state.current_emails:
            st.subheader(f"📧 Current Unread Emails ({len(st.session_state.current_emails)})")
            
            for i, email in enumerate(st.session_state.current_emails):
                with st.container():
                    # Determine email status
                    email_id = email['id']
                    is_processed = email_id in st.session_state.email_stats['processed_ids']
                    is_incoming = email_id in st.session_state.email_stats['incoming_ids']
                    is_new = i < st.session_state.get('new_email_count', len(st.session_state.current_emails))
                    
                    # Status indicators
                    status_badge = ""
                    border_color = "#28a745"  # Default green
                    
                    if is_processed:
                        status_badge = "✅ PROCESSED"
                        border_color = "#6c757d"  # Gray for processed
                    elif is_incoming and is_new:
                        status_badge = "🔥 INCOMING"
                        border_color = "#ff6b6b"  # Red for incoming
                    elif is_incoming:
                        status_badge = "📥 FETCHED"
                        border_color = "#007bff"  # Blue for fetched
                    else:
                        status_badge = "📧 UNREAD"
                        border_color = "#ffc107"  # Yellow for unread
                    
                    # Email header with status
                    col_email, col_status = st.columns([4, 1])
                    
                    with col_email:
                        # Email subject with full display
                        subject = email.get('subject', 'No Subject')
                        from_addr = email.get('from', 'No Sender')
                        received_date = email.get('received', email.get('date', 'No Date'))
                        priority_tag = 'HIGH' if 'urgent' in subject.lower() else 'Normal'
                        attach_tag = 'Yes' if email.get('has_attachments') else 'No'

                        # Status + date header
                        hdr1, hdr2 = st.columns([1, 1])
                        with hdr1:
                            st.markdown(f"**{status_badge}**")
                        with hdr2:
                            st.caption(f"🕒 {received_date}")

                        # From / Subject / Priority / Attachments
                        st.markdown(f"**📧 From:** {from_addr}")
                        st.markdown(f"**📋 Subject:** {subject}")
                        meta1, meta2 = st.columns(2)
                        with meta1:
                            st.markdown(f"**📊 Priority:** `{priority_tag}`")
                        with meta2:
                            st.markdown(f"**📎 Attachments:** `{attach_tag}`")

                        # Email body in an expander so it doesn't dominate the page
                        with st.expander("📝 Email Content", expanded=False):
                            st.text(email.get('body', 'No email content available'))

                    with col_status:
                        st.write("**Actions:**")
                        # Quick action buttons
                        if not is_processed:
                            if st.button("💬", key=f"respond_{email_id}", help="Generate AI Response"):
                                response = self.generate_auto_response(email)
                                st.session_state[f"response_{email_id}"] = response

                            if st.button("📌", key=f"pin_{email_id}", help="Pin for later"):
                                st.session_state[f"pinned_{email_id}"] = True

                            if st.button("✅", key=f"process_{email_id}", help="Mark as Processed"):
                                st.session_state.email_stats['processed_ids'].add(email_id)
                                st.session_state.email_stats['total_processed'] += 1
                                st.session_state[f"processed_{email_id}"] = True
                                st.success(f"✅ Email {email_id} marked as processed!")
                                st.rerun()
                        else:
                            st.success("✅ Processed")
                            if st.button("🔄", key=f"unprocess_{email_id}", help="Mark as Unprocessed"):
                                st.session_state.email_stats['processed_ids'].discard(email_id)
                                st.session_state.email_stats['total_processed'] -= 1
                                if f"processed_{email_id}" in st.session_state:
                                    del st.session_state[f"processed_{email_id}"]
                                st.rerun()

                        if st.button("🗑️", key=f"delete_{email_id}", help="Remove from display"):
                            # Remove from current emails
                            st.session_state.current_emails = [e for e in st.session_state.current_emails if e['id'] != email_id]
                            st.success(f"🗑️ Email {email_id} removed from display")
                            st.rerun()

                    # Show response if it exists
                    if f"response_{email_id}" in st.session_state:
                        st.success("🤖 **AI Response:**")
                        st.info(st.session_state[f"response_{email_id}"])
                    
                    # Show processed status
                    if f"processed_{email_id}" in st.session_state:
                        st.success(f"✅ Email #{email_id} marked as processed")
                    
                    st.markdown("---")
        else:
            st.info("📭 No emails to display. Configure your email account above and click 'Check Now'.")

        # Real-time status bar
        if auto_refresh:
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔄 Auto-refresh", "Active")
            with col2:
                last_check_time = st.session_state.get('last_check', 0)
                st.metric("⏰ Last Check", time.strftime('%H:%M:%S', time.localtime(last_check_time)) if last_check_time else "—")
            with col3:
                email_count = st.session_state.get('new_email_count', 0)
                st.metric("📧 Unread", email_count)

        # ---------------------------------------------------------------
        # 🧑‍⚖️ Human Review Queue (HITL)
        # ---------------------------------------------------------------
        st.markdown("---")
        st.subheader("🧑‍⚖️ Human Review Queue")
        st.caption("Drafts flagged by the guardrail system that need your approval before sending.")

        try:
            review_resp = requests.get(f"{self.api_url}/api/v1/review/pending", timeout=10)
            if review_resp.status_code == 200:
                pending = review_resp.json()
                if not pending:
                    st.success("✅ No pending reviews — all clear!")
                else:
                    st.warning(f"⚠️ {len(pending)} draft(s) awaiting review")
                    for review in pending:
                        rid = review['review_id']
                        with st.expander(
                            f"📧 {review.get('email_subject', 'No Subject')} "
                            f"| Risk: **{review['risk_level'].upper()}** "
                            f"| {review['created_at'][:19].replace('T', ' ')}",
                            expanded=True
                        ):
                            st.markdown(f"**From:** {review.get('email_from', 'N/A')}")
                            if review.get('violations'):
                                st.error("🚨 Violations detected:")
                                for v in review['violations']:
                                    st.markdown(f"- {v}")

                            # Fetch full details for the draft text
                            det_resp = requests.get(f"{self.api_url}/api/v1/review/{rid}", timeout=10)
                            if det_resp.status_code == 200:
                                detail = det_resp.json()
                                st.markdown("**Generated Draft:**")
                                edited = st.text_area(
                                    "Edit before approving (optional)",
                                    value=detail.get('original_draft', ''),
                                    height=150,
                                    key=f"edit_{rid}"
                                )

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                if st.button("✅ Approve", key=f"approve_{rid}", use_container_width=True):
                                    edited_val = st.session_state.get(f"edit_{rid}", "")
                                    original = det_resp.json().get('original_draft', '') if det_resp.status_code == 200 else ""
                                    if edited_val.strip() and edited_val.strip() != original.strip():
                                        r = requests.post(
                                            f"{self.api_url}/api/v1/review/{rid}/edit",
                                            json={"edited_draft": edited_val}, timeout=10
                                        )
                                    else:
                                        r = requests.post(f"{self.api_url}/api/v1/review/{rid}/approve", timeout=10)
                                    if r.status_code == 200:
                                        st.success("✅ Approved!")
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {r.text}")
                            with col_b:
                                reject_reason = st.text_input("Reject reason", key=f"reason_{rid}", placeholder="Optional reason…")
                            with col_c:
                                if st.button("❌ Reject", key=f"reject_{rid}", use_container_width=True):
                                    r = requests.post(
                                        f"{self.api_url}/api/v1/review/{rid}/reject",
                                        json={"reason": st.session_state.get(f"reason_{rid}", "")},
                                        timeout=10
                                    )
                                    if r.status_code == 200:
                                        st.success("❌ Rejected.")
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {r.text}")
            else:
                st.info("Could not load review queue — is the API running?")
        except requests.exceptions.RequestException:
            st.info("🔌 Review queue unavailable — start the API server to enable HITL.")
                        
    
    def render_history_tab(self):
        st.subheader("Email History")

        if st.session_state.email_history:
            # Delete options
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**Total Emails:** {len(st.session_state.email_history)}")
            with col2:
                if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                    if st.session_state.email_history:
                        st.session_state.email_history.clear()
                        st.success("✅ All email history cleared!")
                        st.rerun()
            with col3:
                if st.button("📥 Export", use_container_width=True):
                    self.export_email_history()
            
            st.markdown("---")
            
            df = pd.DataFrame(st.session_state.email_history)
            display_cols = [c for c in ['date', 'to', 'subject', 'status'] if c in df.columns]
            if display_cols:
                # Add delete column to dataframe
                df_with_delete = df[display_cols].copy()
                
                # Display with delete buttons
                for i, row in df_with_delete.iterrows():
                    col1, col2 = st.columns([10, 1])
                    with col1:
                        st.write(f"**{row.get('date', 'N/A')}** - {row.get('to', 'N/A')} - {row.get('subject', 'N/A')}")
                    with col2:
                        if st.button("🗑️", key=f"delete_{i}"):
                            st.session_state.email_history.pop(i)
                            st.success("✅ Email deleted from history!")
                            st.rerun()
                    st.markdown("---")

            # Analytics (only if we have the required columns)
            if 'sentiment_score' in df.columns and 'date' in df.columns:
                st.subheader("📊 Analytics")
                col1, col2 = st.columns(2)
                with col1:
                    st.line_chart(df.set_index('date')[['sentiment_score']])
                if 'response_time_minutes' in df.columns:
                    with col2:
                        st.bar_chart(df['response_time_minutes'].value_counts())
        else:
            st.info("No email history yet.")
    
    def export_email_history(self):
        """Export email history to CSV"""
        try:
            import io
            df = pd.DataFrame(st.session_state.email_history)
            if not df.empty:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"email_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No data to export.")
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
    
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
            # Prepare parameters with real credentials
            params = {
                "email_user": config.get("email_user"),
                "email_password": config.get("email_password"),
                "imap_server": config.get("imap_server")
            }
            
            # Call the real API to get unread emails
            response = requests.get(
                f"{self.api_url}/api/v1/email/emails/unread",
                params=params,
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