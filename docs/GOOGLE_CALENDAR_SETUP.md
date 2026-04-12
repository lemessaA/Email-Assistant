# 📅 Google Calendar Integration Setup Guide

This guide walks you through setting up real Google Calendar integration for your Email Assistant.

## 🔑 Prerequisites

1. **Google Cloud Project** with Calendar API enabled
2. **OAuth2 Credentials** for desktop application
3. **Python Dependencies** for Google Calendar API

## 🛠️ Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Calendar API**:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

### 2. Create OAuth2 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Select "Desktop app" as application type
4. Give it a name (e.g., "Email Assistant Calendar")
5. Click "Create"
6. **Download the JSON file** and save as `credentials/google-calendar-credentials.json`

### 3. Install Required Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz
```

### 4. Create Credentials Directory

```bash
mkdir -p credentials
# Place your downloaded JSON file here:
# credentials/google-calendar-credentials.json
```

### 5. Update Environment Variables

Add to your `.env` file:

```bash
# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS_PATH=./credentials/google-calendar-credentials.json
GOOGLE_CALENDAR_TOKEN_PATH=./credentials/google-calendar-token.json
GOOGLE_CALENDAR_TIMEZONE=UTC
```

## 🚀 First-Time Authentication

### Automatic Authentication

The first time you use calendar tools, the system will:

1. **Open a browser window** for Google OAuth consent
2. **Ask for permission** to access your calendar
3. **Save tokens** for future use
4. **Create calendar events** automatically

### Manual Authentication Test

```python
from src.integrations.google_calendar import GoogleCalendarIntegration

# Initialize calendar service
calendar = GoogleCalendarIntegration()

# Authenticate (will open browser if needed)
if calendar.authenticate():
    print("✅ Calendar authentication successful!")
    
    # Test availability check
    slots = calendar.check_availability(duration=60)
    print(f"Found {len(slots)} available slots")
    
    # Test meeting scheduling
    result = calendar.schedule_meeting(
        attendees=["test@example.com"],
        subject="Test Meeting",
        duration=30,
        preferred_time="14:00"
    )
    print(f"Meeting scheduled: {result['success']}")
else:
    print("❌ Authentication failed")
```

## 📋 Available Calendar Tools

### 1. Check Availability
```python
calendar_tools.check_availability(
    duration=60,           # Meeting duration in minutes
    date="2024-01-15",      # Specific date (optional)
    calendar_id="primary",   # Calendar ID
    min_start_time="09:00", # Earliest start time
    max_end_time="17:00"    # Latest end time
)
```

### 2. Schedule Meeting
```python
calendar_tools.schedule_meeting(
    attendees=["user@example.com", "colleague@example.com"],
    subject="Project Review Meeting",
    duration=60,
    preferred_time="14:00",
    date="2024-01-15",
    description="Discuss project progress and next steps",
    location="Conference Room A",
    include_meet=True
)
```

### 3. Get Upcoming Events
```python
calendar_tools.get_upcoming_events(
    calendar_id="primary",
    max_results=10,
    days_ahead=7
)
```

### 4. Cancel Event
```python
calendar_tools.cancel_event(
    event_id="event_id_from_calendar",
    calendar_id="primary"
)
```

## 🔧 Advanced Configuration

### Multiple Calendars

```python
# Check different calendars
primary_slots = calendar_tools.check_availability(calendar_id="primary")
work_slots = calendar_tools.check_availability(calendar_id="work@example.com")
personal_slots = calendar_tools.check_availability(calendar_id="personal@example.com")
```

### Timezone Support

```python
# Set timezone in environment or code
calendar.calendar_service.set_timezone("America/New_York")
calendar.calendar_service.set_timezone("Europe/London")
calendar.calendar_service.set_timezone("Asia/Tokyo")
```

### Custom Event Types

```python
# Schedule with Google Meet
result = calendar_tools.schedule_meeting(
    attendees=["team@example.com"],
    subject="Team Standup",
    duration=15,
    preferred_time="09:00",
    include_meet=True,
    description="Daily team sync"
)

# Schedule in-person meeting
result = calendar_tools.schedule_meeting(
    attendees=["client@example.com"],
    subject="Client Meeting",
    duration=90,
    preferred_time="14:00",
    location="Main Conference Room",
    include_meet=False
)
```

## 🔒 Security & Permissions

### Required OAuth Scopes

The integration requests these permissions:
- `https://www.googleapis.com/auth/calendar`
- Read access to calendars
- Create/edit/delete events
- Send event invitations

### Token Storage

- **Tokens stored locally** in `credentials/google-calendar-token.json`
- **Auto-refresh** when expired
- **Secure storage** with file permissions
- **Re-authenticate** if tokens become invalid

## 🐛 Troubleshooting

### Common Issues

**1. "Credentials file not found"**
```bash
# Ensure credentials file exists
ls -la credentials/google-calendar-credentials.json

# Check file permissions
chmod 600 credentials/google-calendar-credentials.json
```

**2. "Invalid client" error**
- Verify OAuth client type is "Desktop app"
- Check client ID and secret in credentials
- Ensure Calendar API is enabled

**3. "Authentication cancelled"**
- Complete OAuth flow in browser
- Allow all requested permissions
- Check pop-up blocker settings

**4. "Insufficient permissions"**
- Verify user has calendar access
- Check if calendar is shared
- Ensure correct calendar ID

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with detailed logging
calendar = GoogleCalendarIntegration()
calendar.authenticate()
```

## 📊 Integration Examples

### Email Assistant Workflow

```python
# In your email processing workflow
if "schedule meeting" in email_content.lower():
    # Check availability
    slots = calendar_tools.check_availability(duration=60)
    
    if slots:
        # Schedule meeting
        result = calendar_tools.schedule_meeting(
            attendees=[sender_email],
            subject=email_subject,
            duration=60,
            preferred_time=slots[0]["start"]
        )
        
        # Send confirmation
        send_email(
            to=[sender_email],
            subject=f"Meeting Scheduled: {result['meeting_id']}",
            body=f"Meeting scheduled for {result['scheduled_time']}. Join here: {result['meet_link']}"
        )
```

### Automated Scheduling

```python
# Auto-schedule recurring meetings
def setup_weekly_standup():
    calendar_tools.schedule_meeting(
        attendees=["team@example.com"],
        subject="Weekly Team Standup",
        duration=30,
        preferred_time="09:00",
        description="Weekly progress update and planning"
    )
```

## 🔄 Maintenance

### Token Refresh

Tokens automatically refresh when:
- Token is expired
- API call fails with auth error
- Manual re-authentication required

### Backup Tokens

```bash
# Backup calendar tokens
cp credentials/google-calendar-token.json credentials/google-calendar-token.backup

# Restore if needed
cp credentials/google-calendar-token.backup credentials/google-calendar-token.json
```

### Clean Up

```bash
# Remove tokens to re-authenticate
rm credentials/google-calendar-token.json
```

## 📚 Additional Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [OAuth2 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Python Google API Client](https://googleapis.github.io/google-api-python-client/docs/)

---

**🎉 Your Email Assistant now has real Google Calendar integration!**
