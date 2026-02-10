# Import tool decorator from LangChain for creating AI tools
from langchain.tools import tool
# Import type hints for better code documentation and IDE support
from typing import List, Dict, Any, Optional
# Import datetime for timestamp operations
from datetime import datetime

# Import actual email functionality libraries
import smtplib  # For SMTP email sending
from email.mime.text import MIMEText  # For creating email text content
from email.mime.multipart import MIMEMultipart  # For creating multipart emails with attachments
from email.mime.base import MIMEBase  # For email attachment handling
from email import encoders  # For encoding email attachments
import requests  # For making HTTP requests to external APIs
from bs4 import BeautifulSoup  # For parsing HTML content
import os  # For file operations
import logging  # For proper error logging
import json  # For JSON data handling

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailTools:
    """Collection of email-related tools for the email assistant"""
    
@tool  # Decorator to register this method as a LangChain tool
def send_email(
    to: List[str],  # List of recipient email addresses
    subject: str,  # Email subject line
    body: str,  # Email body content
    cc: Optional[List[str]] = None,  # Optional CC recipients list
    bcc: Optional[List[str]] = None,  # Optional BCC recipients list
    attachments: Optional[List[str]] = None,  # Optional list of attachment file paths
    smtp_server: str = "smtp.gmail.com",  # SMTP server address
    smtp_port: int = 587,  # SMTP server port
    username: str = "your-email@gmail.com",  # SMTP username (should come from config)
    password: str = "your-app-password"  # SMTP password (should come from config)
    ) -> str:
        """Send an email to recipients"""
        try:
            # Create a multipart email message object
            msg = MIMEMultipart()  # Create multipart message for attachments
            msg['From'] = username  # Set sender email address
            msg['To'] = ', '.join(to)  # Set primary recipients as comma-separated string
            msg['Subject'] = subject  # Set email subject line
            
            # Add CC recipients if provided
            if cc:
                msg['Cc'] = ', '.join(cc)  # Set CC recipients as comma-separated string
            
            # Attach email body as HTML content
            msg.attach(MIMEText(body, 'html'))  # Attach HTML body
            
            # Add attachments if any are provided
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):  # Check if attachment file exists
                        with open(file_path, "rb") as attachment:  # Open file in binary mode
                            part = MIMEBase('application', 'octet-stream')  # Create attachment part
                            part.set_payload(attachment.read())  # Set file content
                            encoders.encode_base64(part)  # Encode attachment in base64
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(file_path)}'  # Set filename header
                            )
                            msg.attach(part)  # Attach file to message
                    else:
                        logger.warning(f"Attachment file not found: {file_path}")
            
            # Send email using SMTP server with TLS encryption
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Start TLS encryption for secure connection
                server.login(username, password)  # Authenticate with email credentials
                server.send_message(msg)  # Send the email message
            
            logger.info(f"Email sent successfully to {to}")  # Log successful sending
            return f"Email sent successfully to {to}"  # Return success message
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")  # Log error with details
        return f"Error sending email: {str(e)}"  # Return error message
    
@tool  # Decorator to register this method as a LangChain tool
def draft_email(
        recipient: str,  # Email recipient address
        subject: str,  # Email subject line
        key_points: List[str],  # List of key points to include in email
        tone: str = "professional"  # Email tone: professional, casual, urgent, apologetic
    ) -> str:
        """Draft an email with specified tone and key points"""
        # Mapping of tone types to their descriptions
        tone_map = {
            "professional": "Write in a formal, business-appropriate tone.",
            "casual": "Write in a friendly, informal tone.",
            "urgent": "Write with urgency and importance.",
            "apologetic": "Write with empathy and apology."
        }
        
        # Create a comprehensive prompt for email generation
        prompt = f"""
        {tone_map.get(tone, tone_map['professional'])}  # Get tone description, default to professional
        
        Draft an email with these key points:
        {chr(10).join(f'- {point}' for point in key_points)}  # Format key points as bullet list
        
        Recipient: {recipient}  # Add recipient to prompt
        Subject: {subject}  # Add subject to prompt
        
        Guidelines:
        - Be clear and concise
        - Address all key points mentioned
        - Maintain the specified tone throughout
        - Include appropriate greeting and closing
        - Proofread before sending
        """
        
        return prompt  # Return the generated prompt
    
@tool  # Decorator to register this method as a LangChain tool
def get_unread_emails(
        limit: int = 10,  # Maximum number of emails to retrieve
        folder: str = "inbox",  # Email folder to check (inbox, sent, drafts, etc.)
        imap_server: str = "imap.gmail.com",  # IMAP server address
        username: str = "your-email@gmail.com",  # IMAP username (should come from config)
        password: str = "your-app-password"  # IMAP password (should come from config)
    ) -> List[Dict[str, Any]]:
        """Retrieve unread emails from specified folder"""
        try:
            import imaplib  # Import IMAP library for email retrieval
            import email  # Import email library for parsing
            
            # Connect to IMAP server with SSL
            with imaplib.IMAP4_SSL(imap_server) as imap:
                imap.login(username, password)  # Authenticate with IMAP server
                
                # Select the specified folder
                status, messages = imap.select(folder)
                if status != 'OK':
                    raise Exception(f"Failed to select folder: {folder}")
                
                # Search for unread emails
                status, email_ids = imap.search(None, '(UNSEEN)')  # Find all unread emails
                if status != 'OK':
                    raise Exception("Failed to search for unread emails")
                
                # Fetch email details
                emails = []
                for email_id in email_ids[0].split()[:limit]:  # Limit results
                    status, msg_data = imap.fetch(email_id, '(RFC822)')  # Fetch full email
                    if status == 'OK':
                        # Parse the email message
                        raw_email = msg_data[0][1]
                        email_message = email.message_from_bytes(raw_email)
                        
                        # Extract email information
                        email_info = {
                            "id": email_id.decode(),
                            "subject": email_message.get('Subject', 'No Subject'),
                            "from": email_message.get('From', 'Unknown Sender'),
                            "body": self._extract_email_body(email_message),
                            "received": email_message.get('Date', datetime.now().isoformat()),
                            "unread": True
                        }
                        emails.append(email_info)
                
                imap.close()  # Close the folder
                imap.logout()  # Logout from IMAP server
                
                logger.info(f"Retrieved {len(emails)} unread emails from {folder}")
                return emails  # Return list of email information
                
        except Exception as e:
            logger.error(f"Error retrieving unread emails: {str(e)}")
        return []  # Return empty list on error  
def _extract_email_body(self, email_message) -> str:
        """Extract email body from email message, handling both plain text and HTML"""
        try:
            if email_message.is_multipart():
                # Handle multipart messages
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode()
                    elif part.get_content_type() == "text/html":
                        # Parse HTML content and extract text
                        html_content = part.get_payload(decode=True).decode()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        return soup.get_text()
            else:
                # Handle single-part messages
                return email_message.get_payload(decode=True).decode()
        except Exception as e:
            logger.warning(f"Error extracting email body: {str(e)}")
            return ""  # Return empty string on error

class SearchTools:
    """Collection of search-related tools for finding information"""
    
def web_search(
        query: str, 
        max_results: int = 5,
        search_api_key: str = "your-search-api-key", # API key for search service
        search_engine: str = "serper"  # Search engine to use (serper, google, bing)
        ) -> List[Dict[str, Any]]:
        """Search web for information using real search API"""
        try:
            # Make HTTP request to search API
            headers = {
                "X-API-KEY": search_api_key,  # API authentication header
                "Content-Type": "application/json"
            }
            
            # Prepare search request payload
            payload = {
                "q": query,  # Search query
                "num": max_results  # Number of results requested
            }
            
            # Execute search request
            response = requests.post(
                f"https://api.{search_engine}.dev/search",  # Search API endpoint
                json=payload,  # Send JSON payload
                headers=headers,  # Include authentication headers
                timeout=10  # Set request timeout
            )
            
            # Parse search results
            if response.status_code == 200:
                data = response.json()  # Parse JSON response
                results = data.get("organic", [])[:max_results]  # Get organic results, limit by max_results
                
                # Format results for consistency
                formatted_results = []
                for i, result in enumerate(results, 1):
                    formatted_results.append({
                        "position": i,
                        "title": result.get("title", ""),
                        "url": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": search_engine
                    })
                
                logger.info(f"Web search completed: {len(formatted_results)} results for query: {query}")
                return formatted_results
            else:
                logger.error(f"Search API error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Web search request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in web search: {str(e)}")
            return []
    
def internal_knowledge_search(
        query: str,
        max_results: int = 5,
        knowledge_base_path: str = "./data/knowledge_base"  # Path to knowledge base files
    ) -> List[Dict[str, Any]]:
        """Search internal knowledge base/documents"""
        try:
            # In a real implementation, you would:
            # 1. Load documents from knowledge base
            # 2. Create vector embeddings
            # 3. Perform similarity search
            # 4. Return relevant documents
            
            # For now, implement simple file-based search
            results = []
            if os.path.exists(knowledge_base_path):
                # Search through knowledge base files
                for filename in os.listdir(knowledge_base_path):
                    if filename.endswith('.txt') or filename.endswith('.md'):
                        file_path = os.path.join(knowledge_base_path, filename)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as file:
                                content = file.read().lower()
                                # Simple keyword matching
                                if query.lower() in content:
                                    results.append({
                                        "file": filename,
                                        "path": file_path,
                                        "content_preview": content[:200] + "..." if len(content) > 200 else content,
                                        "relevance_score": 0.8  # Mock relevance score
                                    })
                        except Exception as e:
                            logger.warning(f"Error reading knowledge base file {filename}: {str(e)}")
            
            # Sort by relevance score and limit results
            results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            limited_results = results[:max_results]
            
            logger.info(f"Internal knowledge search: {len(limited_results)} results for query: {query}")
            return limited_results
            
        except Exception as e:
            logger.error(f"Error searching internal knowledge base: {str(e)}")
            return []

class CalendarTools:
    """Collection of calendar-related tools for scheduling and time management"""
    
@tool  # Decorator to register this method as a LangChain tool
def check_availability(
        duration: int = 60,  # Meeting duration in minutes
        date: Optional[str] = None,  # Optional specific date to check
        calendar_api_key: str = "your-calendar-api-key",  # Calendar API key
        calendar_provider: str = "google"  # Calendar provider (google, outlook, apple)
    ) -> List[Dict[str, Any]]:
        """Check calendar availability for scheduling"""
        try:
            # In a real implementation, you would:
            # 1. Connect to calendar API (Google Calendar, Outlook, etc.)
            # 2. Authenticate with API key
            # 3. Query availability for specified date and duration
            # 4. Return available time slots
            
            # For now, return mock availability data
            current_date = date or datetime.now().strftime("%Y-%m-%d")
            
            # Generate mock time slots
            time_slots = []
            for hour in range(9, 18):  # 9 AM to 5 PM
                if hour not in [12, 13]:  # Skip lunch break
                    end_time = hour + 1 if hour + 1 <= 17 else 17
                    time_slots.append({
                        "start": f"{hour:02d}:00",
                        "end": f"{end_time:02d}:00",
                        "available": True,
                        "date": current_date
                    })
            
            logger.info(f"Calendar availability checked for {current_date}: {len(time_slots)} slots")
            return time_slots
            
        except Exception as e:
            logger.error(f"Error checking calendar availability: {str(e)}")
            return []
    
def schedule_meeting(
        attendees: List[str],  # List of meeting participant emails
        subject: str,  # Meeting subject/title
        duration: int,  # Meeting duration in minutes
        preferred_times: List[str],  # List of preferred time slots
        calendar_api_key: str = "your-calendar-api-key",  # Calendar API key
        calendar_provider: str = "google"  # Calendar provider (google, outlook, apple)
    ) -> Dict[str, Any]:
        """Schedule a meeting with attendees"""
        try:
            # In a real implementation, you would:
            # 1. Find the best available time slot
            # 2. Create calendar event
            # 3. Send invitations to all attendees
            # 4. Return meeting details and calendar links
            
            # For now, simulate meeting scheduling
            meeting_id = f"meet_{datetime.now().timestamp()}"
            scheduled_time = preferred_times[0] if preferred_times else datetime.now().strftime("%Y-%m-%dT%H:%M")
            
            # Create calendar invite links (mock)
            calendar_link = f"https://calendar.{calendar_provider}.com/event/{meeting_id}"
            
            # Log the meeting scheduling
            logger.info(f"Meeting scheduled: {subject} with {len(attendees)} attendees")
            
            return {
                "success": True,  # Meeting scheduling status
                "meeting_id": meeting_id,  # Unique meeting identifier
                "scheduled_time": scheduled_time,  # Actual scheduled time
                "calendar_link": calendar_link,  # Link to calendar event
                "attendees": attendees,  # List of meeting participants
                "duration": duration,  # Meeting duration
                "subject": subject  # Meeting subject
            }
            
        except Exception as e:
            logger.error(f"Error scheduling meeting: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "meeting_id": None
            }

class FileTools:
    """Collection of file handling tools for email attachments and documents"""
    
def read_attachment(
        self, 
        file_path: str,  # Path to the attachment file
        extract_text: bool = True  # Whether to extract text content
    ) -> str:
        """Read and extract text from email attachments"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Attachment file not found: {file_path}")
            
            # Determine file type and extract content accordingly
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._read_pdf(file_path)  # Extract text from PDF files
            elif file_extension == '.docx':
                return self._read_docx(file_path)  # Extract text from Word documents
            elif file_extension in ['.txt', '.md', '.csv']:
                # Read plain text files directly
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            else:
                # For other file types, attempt binary read with encoding
                with open(file_path, 'rb') as file:
                    try:
                        return file.read().decode('utf-8')
                    except UnicodeDecodeError:
                        return f"[Binary file: {file_extension} - {os.path.getsize(file_path)} bytes]"
                        
        except Exception as e:
            logger.error(f"Error reading attachment {file_path}: {str(e)}")
            return f"Error reading file: {str(e)}"
    
def _read_pdf(file_path: str) -> str:
        """Extract text from PDF file using available libraries"""
        try:
            # Try to import PDF reading library
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                # Fallback to basic PDF text extraction
                logger.warning("PyPDF2 not available, using basic PDF reading")
                return f"[PDF file: {os.path.basename(file_path)} - {os.path.getsize(file_path)} bytes]"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
            return f"Error reading PDF: {str(e)}"
    
def _read_docx(file_path: str) -> str:
        """Extract text from DOCX file using available libraries"""
        try:
            # Try to import DOCX reading library
            try:
                import docx
                doc = docx.Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                # Fallback if python-docx not available
                logger.warning("python-docx not available, using basic DOCX reading")
                return f"[DOCX file: {os.path.basename(file_path)} - {os.path.getsize(file_path)} bytes]"
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            return f"Error reading DOCX: {str(e)}"

@tool  # Decorator to register this method as a LangChain tool
def save_draft(
        self,
        content: str,  # Email draft content
        metadata: Dict[str, Any],  # Additional metadata (recipients, subject, etc.)
        save_path: str = "./data/drafts",  # Path to save drafts
    ) -> str:
        """Save email draft to persistent storage"""
        try:
            # Create drafts directory if it doesn't exist
            os.makedirs(save_path, exist_ok=True)
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"draft_{timestamp}.json"
            file_path = os.path.join(save_path, filename)
            
            # Prepare draft data for storage
            draft_data = {
                "content": content,
                "metadata": metadata,
                "created_at": datetime.now().isoformat(),
                "draft_id": f"draft_{timestamp}"
            }
            
            # Save draft to JSON file
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(draft_data, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Draft saved: {filename}")
            return f"Draft saved successfully to {filename}"

        except Exception as e:
            logger.error(f"Error saving draft: {str(e)}")
            return f"Error saving draft: {str(e)}"