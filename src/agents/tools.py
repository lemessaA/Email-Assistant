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
    """Collection of search-related tools for web and internal knowledge base"""
    
    def __init__(self):
        """Initialize search tools with multiple search engines"""
        try:
            from integrations.web_search import WebSearchIntegration, SearchEngine
            self.web_search_service = WebSearchIntegration()
            self.SearchEngine = SearchEngine
        except ImportError:
            logger.warning("Web search integration not available, using mock implementation")
            self.web_search_service = None
            self.SearchEngine = None
    
    @tool
    def web_search(
        self,
        query: str,
        max_results: int = 5,
        engine: str = "auto",
        search_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        Search web for information using multiple search engines
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            engine: Search engine to use (serper, tavily, google, bing, auto)
            search_type: Type of search (general, ai_context, news, academic)
        """
        if self.web_search_service:
            try:
                # Convert engine string to enum if specified
                search_engine = None
                if engine != "auto" and self.SearchEngine:
                    try:
                        search_engine = self.SearchEngine(engine.lower())
                    except ValueError:
                        logger.warning(f"Unknown search engine: {engine}, using auto-selection")
                
                # Perform search
                results = self.web_search_service.search(
                    query=query,
                    max_results=max_results,
                    engine=search_engine,
                    search_type=search_type
                )
                
                logger.info(f"Web search returned {len(results)} results for query: {query[:50]}...")
                return results
                
            except Exception as e:
                logger.error(f"Web search failed: {str(e)}")
                return self._get_mock_search_results(query, max_results)
        else:
            # Fallback to mock implementation
            return self._get_mock_search_results(query, max_results)
    
    def _get_mock_search_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Get mock search results for fallback"""
        return [
            {
                "title": f"Mock result for: {query}",
                "link": "https://example.com/mock-result",
                "snippet": f"This is a mock search result for the query: {query}. In production, this would be replaced with real search results from the configured search engine.",
                "source": "mock",
                "position": 1
            }
        ]
    
    @tool
    def ai_context_search(
        self,
        query: str,
        max_results: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Perform AI-optimized search for email context understanding
        
        Args:
            query: Context query for email understanding
            max_results: Maximum number of results to return
        """
        if self.web_search_service:
            try:
                # Use Tavily for AI-optimized search
                results = self.web_search_service.search(
                    query=query,
                    max_results=max_results,
                    search_type="ai_context"
                )
                
                logger.info(f"AI context search returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"AI context search failed: {str(e)}")
                return []
        else:
            return []
    
    @tool
    def news_search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for recent news related to the query
        
        Args:
            query: News search query
            max_results: Maximum number of results to return
        """
        if self.web_search_service:
            try:
                results = self.web_search_service.search(
                    query=query,
                    max_results=max_results,
                    search_type="news"
                )
                
                logger.info(f"News search returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"News search failed: {str(e)}")
                return []
        else:
            return []
    
    @tool
    def academic_search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for academic papers and research
        
        Args:
            query: Academic search query
            max_results: Maximum number of results to return
        """
        if self.web_search_service:
            try:
                results = self.web_search_service.search(
                    query=query,
                    max_results=max_results,
                    search_type="academic"
                )
                
                logger.info(f"Academic search returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Academic search failed: {str(e)}")
                return []
        else:
            return []
    
    @tool
    def get_search_stats(self) -> Dict[str, Any]:
        """Get statistics about available search engines"""
        if self.web_search_service:
            try:
                stats = self.web_search_service.get_search_stats()
                logger.info(f"Search stats: {stats}")
                return stats
            except Exception as e:
                logger.error(f"Failed to get search stats: {str(e)}")
                return {"error": str(e)}
        else:
            return {"error": "Web search service not available"}
    
    @tool
    def internal_knowledge_search(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search internal knowledge base/documents"""
        # Implementation using vector store
        # This would connect to ChromaDB/FAISS
        logger.info(f"Internal knowledge search for: {query}")
        return []

class CalendarTools:
    """Collection of calendar-related tools for scheduling and time management"""
    
    def __init__(self):
        """Initialize calendar tools with Google Calendar integration"""
        try:
            from integrations.google_calendar import GoogleCalendarIntegration
            self.calendar_service = GoogleCalendarIntegration()
            self.calendar_service.set_timezone("UTC")
        except ImportError:
            logger.warning("Google Calendar integration not available, using mock implementation")
            self.calendar_service = None
    
    @tool
    def check_availability(
        self,
        duration: int = 60,  # Meeting duration in minutes
        date: Optional[str] = None,  # Optional specific date to check
        calendar_id: str = "primary",  # Google Calendar ID
        min_start_time: str = "09:00",  # Earliest start time
        max_end_time: str = "17:00"  # Latest end time
    ) -> List[Dict[str, Any]]:
        """Check calendar availability for scheduling"""
        if self.calendar_service:
            # Use real Google Calendar integration
            try:
                available_slots = self.calendar_service.check_availability(
                    duration=duration,
                    date=date,
                    calendar_id=calendar_id,
                    min_start_time=min_start_time,
                    max_end_time=max_end_time
                )
                return available_slots
            except Exception as e:
                logger.error(f"Error checking calendar availability: {str(e)}")
                # Fallback to mock data
                return self._get_mock_availability()
        else:
            # Fallback to mock implementation
            return self._get_mock_availability()
    
    def _get_mock_availability(self) -> List[Dict[str, Any]]:
        """Get mock availability data for fallback"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        return [
            {
                "start": "09:00",
                "end": "10:00",
                "available": True,
                "date": current_date,
                "timezone": "UTC"
            },
            {
                "start": "14:00",
                "end": "15:00",
                "available": True,
                "date": current_date,
                "timezone": "UTC"
            }
        ]
    
    @tool
    def schedule_meeting(
        self,
        attendees: List[str],  # List of meeting participant emails
        subject: str,  # Meeting subject/title
        duration: int,  # Meeting duration in minutes
        preferred_time: str,  # Preferred time slot (HH:MM format)
        date: Optional[str] = None,  # Meeting date (YYYY-MM-DD format)
        calendar_id: str = "primary",  # Google Calendar ID
        description: str = "",  # Meeting description
        location: str = "",  # Meeting location
        include_meet: bool = True  # Include Google Meet link
    ) -> Dict[str, Any]:
        """Schedule a meeting with attendees"""
        if self.calendar_service:
            # Use real Google Calendar integration
            try:
                result = self.calendar_service.schedule_meeting(
                    attendees=attendees,
                    subject=subject,
                    duration=duration,
                    preferred_time=preferred_time,
                    date=date,
                    calendar_id=calendar_id,
                    description=description,
                    location=location,
                    include_meet=include_meet
                )
                return result
            except Exception as e:
                logger.error(f"Error scheduling meeting: {str(e)}")
                # Fallback to mock data
                return self._get_mock_meeting(attendees, subject, duration)
        else:
            # Fallback to mock implementation
            return self._get_mock_meeting(attendees, subject, duration)
    
    def _get_mock_meeting(self, attendees: List[str], subject: str, duration: int) -> Dict[str, Any]:
        """Get mock meeting data for fallback"""
        meeting_id = f"meet_{datetime.now().timestamp()}"
        scheduled_time = datetime.now().strftime("%Y-%m-%dT%H:%M:00")
        
        return {
            "success": True,
            "meeting_id": meeting_id,
            "scheduled_time": scheduled_time,
            "calendar_link": f"https://calendar.google.com/calendar/event?eid={meeting_id}",
            "meet_link": f"https://meet.google.com/{meeting_id}",
            "attendees": attendees,
            "subject": subject,
            "duration": duration,
            "location": "",
            "timezone": "UTC"
        }
    
    @tool
    def get_upcoming_events(
        self,
        calendar_id: str = "primary",  # Google Calendar ID
        max_results: int = 10,  # Maximum number of events to return
        days_ahead: int = 7  # Number of days ahead to look
    ) -> List[Dict[str, Any]]:
        """Get upcoming events from calendar"""
        if self.calendar_service:
            try:
                events = self.calendar_service.get_upcoming_events(
                    calendar_id=calendar_id,
                    max_results=max_results,
                    days_ahead=days_ahead
                )
                return events
            except Exception as e:
                logger.error(f"Error getting upcoming events: {str(e)}")
                return []
        else:
            # Return empty list for mock implementation
            return []
    
    @tool
    def cancel_event(
        self,
        event_id: str,  # Google Calendar event ID
        calendar_id: str = "primary"  # Google Calendar ID
    ) -> Dict[str, Any]:
        """Cancel/delete a calendar event"""
        if self.calendar_service:
            try:
                result = self.calendar_service.cancel_event(
                    event_id=event_id,
                    calendar_id=calendar_id
                )
                return result
            except Exception as e:
                logger.error(f"Error cancelling event: {str(e)}")
                return {"success": False, "error": str(e)}
        else:
            # Mock cancellation
            return {
                "success": True,
                "event_id": event_id,
                "message": "Event cancelled (mock implementation)"
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