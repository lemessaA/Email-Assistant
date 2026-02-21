from langchain.tools import tool
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup

class EmailTools:
    
    @tool
    def send_email(
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> str:
        """Send an email to recipients"""
        try:
            # Implementation using SMTP
            msg = MIMEMultipart()
            msg['From'] = "assistant@company.com"
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            msg.attach(MIMEText(body, 'html'))
            
            # Add attachments if any
            if attachments:
                # Attachment handling code
                pass
            
            # Send email
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login("username", "password")
                server.send_message(msg)
            
            return f"Email sent successfully to {to}"
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    @tool
    def draft_email(
        recipient: str,
        subject: str,
        key_points: List[str],
        tone: str = "professional"
    ) -> str:
        """Draft an email with specified tone and key points"""
        tone_map = {
            "professional": "Write in a formal, business-appropriate tone.",
            "casual": "Write in a friendly, informal tone.",
            "urgent": "Write with urgency and importance.",
            "apologetic": "Write with empathy and apology."
        }
        
        prompt = f"""
        {tone_map.get(tone, tone_map['professional'])}
        
        Draft an email with these key points:
        {chr(10).join(f'- {point}' for point in key_points)}
        
        Recipient: {recipient}
        Subject: {subject}
        """
        
        return prompt
    
    @tool
    def get_unread_emails(
        limit: int = 10,
        folder: str = "inbox",
        imap_server: str = "imap.gmail.com",
        username: str = "your-email@gmail.com",
        password: str = "your-app-password"
    ) -> List[Dict[str, Any]]:
        """Retrieve unread emails from specified folder using real IMAP"""
        try:
            import imaplib
            import email
            from email.header import decode_header
            
            # Connect to IMAP server
            with imaplib.IMAP4_SSL(imap_server) as imap:
                # Login
                imap.login(username, password)
                
                # Select the folder
                status, messages = imap.select(folder)
                if status != 'OK':
                    raise Exception(f"Failed to select folder: {folder}")
                
                # Search for unread emails
                status, email_ids = imap.search(None, '(UNSEEN)')
                if status != 'OK':
                    raise Exception("Failed to search for unread emails")
                
                emails = []
                email_id_list = email_ids[0].split()[:limit]  # Limit results
                
                for email_id in email_id_list:
                    try:
                        # Fetch email
                        status, msg_data = imap.fetch(email_id, '(RFC822)')
                        if status != 'OK':
                            continue
                            
                        # Parse email
                        raw_email = msg_data[0][1]
                        msg = email.message_from_bytes(raw_email)
                        
                        # Extract email details
                        subject = decode_header(msg.get('Subject', ''))[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode('utf-8', errors='ignore')
                        
                        from_addr = msg.get('From', '')
                        to_addr = msg.get('To', '')
                        date = msg.get('Date', '')
                        
                        # Extract body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    try:
                                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        break
                                    except:
                                        pass
                                elif part.get_content_type() == "text/html":
                                    try:
                                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                                        # Remove HTML tags for plain text
                                        import re
                                        body = re.sub('<[^<]+?>', '', body)
                                        break
                                    except:
                                        pass
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                            except:
                                body = str(msg.get_payload())
                        
                        emails.append({
                            "id": email_id.decode('utf-8'),
                            "subject": subject,
                            "from": from_addr,
                            "to": to_addr,
                            "body": body[:500] + "..." if len(body) > 500 else body,
                            "received": date,
                            "has_attachments": any(part.get_filename() for part in msg.walk() if part.get_filename())
                        })
                        
                    except Exception as e:
                        # Skip problematic emails but continue processing others
                        continue
                
                return emails
                
        except Exception as e:
            # If IMAP fails, return empty list with error info
            print(f"IMAP Error: {str(e)}")
            return []
    
    @tool
    def search_emails(
        query: str,
        limit: int = 20,
        date_range: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Search emails by query with optional date range"""
        # Implementation using email search
        return []

class SearchTools:
    
    @tool
    def web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for information"""
        # Implementation using Serper API or similar
        try:
            response = requests.get(
                f"https://api.serper.dev/search",
                params={"q": query},
                headers={"X-API-KEY": "your-api-key"}
            )
            data = response.json()
            return data.get("organic", [])[:max_results]
        except:
            # Fallback or error handling
            return []
    
    @tool
    def internal_knowledge_search(
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search internal knowledge base/documents"""
        # Implementation using vector store
        # This would connect to ChromaDB/FAISS
        return []

class CalendarTools:
    
    @tool
    def check_availability(
        duration: int = 60,  # minutes
        date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Check calendar availability for scheduling"""
        # Implementation using Google Calendar API
        return [
            {"start": "09:00", "end": "10:00", "available": True},
            {"start": "14:00", "end": "15:00", "available": True}
        ]
    
    @tool
    def schedule_meeting(
        attendees: List[str],
        subject: str,
        duration: int,
        preferred_times: List[str]
    ) -> Dict[str, Any]:
        """Schedule a meeting with attendees"""
        # Implementation using calendar API
        return {
            "success": True,
            "meeting_id": "meet_123",
            "scheduled_time": "2024-01-15T10:00:00",
            "calendar_link": "https://calendar.link/meeting"
        }

class FileTools:
    
    @tool
    def read_attachment(file_path: str) -> str:
        """Read and extract text from email attachments"""
        # Support for PDF, DOCX, TXT, etc.
        if file_path.endswith('.pdf'):
            return self._read_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self._read_docx(file_path)
        else:
            with open(file_path, 'r') as f:
                return f.read()
    
    @tool
    def save_draft(
        content: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Save email draft to database"""
        # Implementation for saving drafts
        return "Draft saved successfully"