"""
Google Calendar Integration Module

This module provides real Google Calendar API integration for the Email Assistant.
It handles authentication, availability checking, and meeting scheduling.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz

# Configure logging
logger = logging.getLogger(__name__)

class GoogleCalendarIntegration:
    """
    Real Google Calendar API integration for email assistant
    """
    
    def __init__(self, credentials_path: str = None, token_path: str = None):
        """
        Initialize Google Calendar integration
        
        Args:
            credentials_path: Path to Google API credentials JSON file
            token_path: Path to store OAuth tokens
        """
        self.credentials_path = credentials_path or "./credentials/google-calendar-credentials.json"
        self.token_path = token_path or "./credentials/google-calendar-token.json"
        self.service = None
        self.timezone = "UTC"
        
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API using OAuth2
        
        Returns:
            bool: True if authentication successful
        """
        try:
            creds = None
            
            # Load existing token if available
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_path):
                        raise FileNotFoundError(f"Google Calendar credentials not found at {self.credentials_path}")
                    
                    # Define OAuth scope for calendar access
                    SCOPES = ['https://www.googleapis.com/auth/calendar']
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Build calendar service
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Google Calendar authentication failed: {str(e)}")
            return False
    
    def check_availability(
        self, 
        duration: int = 60, 
        date: Optional[str] = None,
        calendar_id: str = "primary",
        min_start_time: str = "09:00",
        max_end_time: str = "17:00"
    ) -> List[Dict[str, Any]]:
        """
        Check calendar availability for scheduling
        
        Args:
            duration: Meeting duration in minutes
            date: Date to check (YYYY-MM-DD format), defaults to today
            calendar_id: Calendar ID to check
            min_start_time: Earliest start time (HH:MM format)
            max_end_time: Latest end time (HH:MM format)
            
        Returns:
            List of available time slots
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Parse date or use today
            if date:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                target_date = datetime.now().date()
            
            # Create timezone-aware datetime objects
            tz = pytz.timezone(self.timezone)
            start_datetime = tz.localize(datetime.combine(target_date, datetime.strptime(min_start_time, "%H:%M").time()))
            end_datetime = tz.localize(datetime.combine(target_date, datetime.strptime(max_end_time, "%H:%M").time()))
            
            # Convert to ISO format for API
            start_time = start_datetime.isoformat()
            end_time = end_datetime.isoformat()
            
            # Get free/busy information
            body = {
                "timeMin": start_time,
                "timeMax": end_time,
                "items": [{"id": calendar_id}]
            }
            
            events_result = self.service.freebusy().query(body=body).execute()
            busy_times = events_result.get('calendars', {}).get(calendar_id, {}).get('busy', [])
            
            # Generate available time slots
            available_slots = []
            current_time = start_datetime
            duration_delta = timedelta(minutes=duration)
            
            while current_time + duration_delta <= end_datetime:
                slot_end = current_time + duration_delta
                
                # Check if slot conflicts with any busy time
                is_available = True
                for busy in busy_times:
                    busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                    busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                    
                    # Convert to same timezone for comparison
                    busy_start = busy_start.astimezone(tz)
                    busy_end = busy_end.astimezone(tz)
                    
                    # Check for overlap
                    if not (slot_end <= busy_start or current_time >= busy_end):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append({
                        "start": current_time.strftime("%H:%M"),
                        "end": slot_end.strftime("%H:%M"),
                        "available": True,
                        "date": target_date.strftime("%Y-%m-%d"),
                        "timezone": self.timezone
                    })
                
                # Move to next slot (30-minute increments)
                current_time += timedelta(minutes=30)
            
            logger.info(f"Found {len(available_slots)} available slots for {target_date}")
            return available_slots
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return []
    
    def schedule_meeting(
        self,
        attendees: List[str],
        subject: str,
        duration: int,
        preferred_time: str,
        date: str = None,
        calendar_id: str = "primary",
        description: str = "",
        location: str = "",
        include_meet: bool = True
    ) -> Dict[str, Any]:
        """
        Schedule a meeting with attendees
        
        Args:
            attendees: List of attendee email addresses
            subject: Meeting subject/title
            duration: Meeting duration in minutes
            preferred_time: Preferred time slot (HH:MM format)
            date: Meeting date (YYYY-MM-DD format), defaults to today
            calendar_id: Calendar ID to create event in
            description: Meeting description
            location: Meeting location
            include_meet: Whether to include Google Meet link
            
        Returns:
            Dictionary with meeting details
        """
        if not self.service:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            # Parse date and time
            if date:
                meeting_date = datetime.strptime(date, "%Y-%m-%d").date()
            else:
                meeting_date = datetime.now().date()
            
            meeting_time = datetime.strptime(preferred_time, "%H:%M").time()
            
            # Create timezone-aware datetime
            tz = pytz.timezone(self.timezone)
            start_datetime = tz.localize(datetime.combine(meeting_date, meeting_time))
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Prepare event data
            event_data = {
                'summary': subject,
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': self.timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': self.timezone,
                },
                'attendees': [{'email': email} for email in attendees],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 10},  # 10 minutes before
                    ],
                },
            }
            
            # Add location if provided
            if location:
                event_data['location'] = location
            
            # Add Google Meet link if requested
            if include_meet:
                event_data['conferenceData'] = {
                    'createRequest': {
                        'requestId': f"meeting_{datetime.now().timestamp()}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            
            # Create the event
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data,
                conferenceDataVersion=1 if include_meet else 0,
                sendUpdates='all'  # Send invitations to all attendees
            ).execute()
            
            # Extract meeting details
            meeting_id = event['id']
            meeting_link = event.get('hangoutLink', '')
            calendar_link = event.get('htmlLink', '')
            
            result = {
                "success": True,
                "meeting_id": meeting_id,
                "scheduled_time": start_datetime.isoformat(),
                "calendar_link": calendar_link,
                "meet_link": meeting_link,
                "attendees": attendees,
                "subject": subject,
                "duration": duration,
                "location": location,
                "timezone": self.timezone
            }
            
            logger.info(f"Meeting scheduled successfully: {meeting_id}")
            return result
            
        except HttpError as e:
            error_msg = f"Google Calendar API error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error scheduling meeting: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def get_upcoming_events(
        self, 
        calendar_id: str = "primary",
        max_results: int = 10,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming events from calendar
        
        Args:
            calendar_id: Calendar ID to fetch events from
            max_results: Maximum number of events to return
            days_ahead: Number of days ahead to look for events
            
        Returns:
            List of upcoming events
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Calculate time range
            now = datetime.now(pytz.timezone(self.timezone))
            end_time = now + timedelta(days=days_ahead)
            
            # Fetch events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now.isoformat(),
                timeMax=end_time.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Format events
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    "id": event['id'],
                    "summary": event.get('summary', 'No Title'),
                    "description": event.get('description', ''),
                    "start": start,
                    "end": end,
                    "location": event.get('location', ''),
                    "attendees": [att.get('email', '') for att in event.get('attendees', [])],
                    "meet_link": event.get('hangoutLink', ''),
                    "html_link": event.get('htmlLink', '')
                })
            
            logger.info(f"Retrieved {len(formatted_events)} upcoming events")
            return formatted_events
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting upcoming events: {str(e)}")
            return []
    
    def cancel_event(self, event_id: str, calendar_id: str = "primary") -> Dict[str, Any]:
        """
        Cancel/delete an event
        
        Args:
            event_id: ID of the event to cancel
            calendar_id: Calendar ID containing the event
            
        Returns:
            Dictionary with cancellation result
        """
        if not self.service:
            if not self.authenticate():
                return {"success": False, "error": "Authentication failed"}
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Event {event_id} cancelled successfully")
            return {"success": True, "event_id": event_id}
            
        except HttpError as e:
            error_msg = f"Google Calendar API error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error cancelling event: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def set_timezone(self, timezone: str):
        """Set timezone for calendar operations"""
        self.timezone = timezone
        logger.info(f"Calendar timezone set to {timezone}")
