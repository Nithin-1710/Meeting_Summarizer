# backend/utils.py
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def save_text(filename: str, content: str, folder="outputs"):
    """Save text output (transcript or summary) to a file"""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def get_calendar_service():
    """Authenticate and return Google Calendar service using OAuth"""
    import pickle
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = None
    
    # Load existing credentials if available
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, create new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8501)
        
        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('calendar', 'v3', credentials=creds)

def extract_deadline_date(deadline_str):
    """
    Parse deadline string and return datetime object
    Handles formats like: "2025-01-15", "January 15", "15th Jan", etc.
    """
    try:
        # Try ISO format first
        return datetime.fromisoformat(deadline_str)
    except:
        pass
    
    try:
        # Try common date formats
        for fmt in ['%Y-%m-%d', '%B %d', '%d %B', '%d %b', '%b %d', '%d/%m/%Y']:
            try:
                parsed = datetime.strptime(deadline_str.strip(), fmt)
                # If no year provided, assume current or next year
                if parsed.year == 1900:
                    now = datetime.now()
                    parsed = parsed.replace(year=now.year)
                    if parsed < now:
                        parsed = parsed.replace(year=now.year + 1)
                return parsed
            except ValueError:
                continue
    except:
        pass
    
    return None

def add_calendar_reminder(service, event_title, deadline_date, description=""):
    """
    Add an event to Google Calendar
    
    Args:
        service: Google Calendar service object
        event_title: Title of the event/deadline
        deadline_date: datetime object or string in ISO format
        description: Optional event description
    
    Returns:
        Event ID if successful, None otherwise
    """
    try:
        # Parse date if string
        if isinstance(deadline_date, str):
            deadline_date = extract_deadline_date(deadline_date)
        
        if not deadline_date:
            return None
        
        # Create event object
        event = {
            'summary': f'Deadline: {event_title}',
            'description': description,
            'start': {
                'dateTime': deadline_date.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': (deadline_date + timedelta(hours=1)).isoformat(),
                'timeZone': 'UTC',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},  # 1 hour before
                ],
            },
        }
        
        # Insert event into primary calendar
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event.get('id')
    
    except Exception as e:
        print(f"Error adding calendar event: {str(e)}")
        return None