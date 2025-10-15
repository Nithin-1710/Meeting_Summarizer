# backend/routes.py
from .services import transcribe_audio, generate_summary, extract_deadlines_with_gpt
from .utils import save_text, get_calendar_service, add_calendar_reminder
from .database import save_meeting_summary, get_all_meetings, get_meeting_by_id, search_meetings, delete_meeting
import io

def process_meeting(audio_file) -> dict:
    """Process the uploaded meeting audio and return results"""
    audio_bytes = io.BytesIO(audio_file.read())
    audio_bytes.name = audio_file.name
    filename = audio_file.name

    transcript = transcribe_audio(audio_bytes)
    summary = generate_summary(transcript)
    
    # Extract deadlines using GPT (uses db_config.client internally)
    deadlines = extract_deadlines_with_gpt(transcript)

    # Save to MongoDB
    meeting_id = save_meeting_summary(filename, transcript, summary, deadlines)

    # Save outputs for reference
    transcript_path = save_text("transcript.txt", transcript)
    summary_path = save_text("summary.txt", summary)

    return {
        "meeting_id": meeting_id,
        "transcript": transcript,
        "summary": summary,
        "deadlines": deadlines,
        "files": {
            "transcript": transcript_path,
            "summary": summary_path
        }
    }


def add_reminders_to_calendar(deadlines) -> dict:
    """Add extracted deadlines to Google Calendar"""
    try:
        service = get_calendar_service()
        
        if service is None:
            return {
                'success': False,
                'message': 'Failed to authenticate with Google Calendar.'
            }
        
        added_events = []
        failed_events = []
        
        for deadline in deadlines:
            print(f"Processing deadline: {deadline}")
            
            event_id = add_calendar_reminder(
                service,
                event_title=deadline.get('title'),
                deadline_date=deadline.get('date'),
                description=deadline.get('description', '')
            )
            
            if event_id:
                added_events.append({
                    'title': deadline.get('title'),
                    'event_id': event_id
                })
                print(f"✅ Successfully added: {deadline.get('title')}")
            else:
                failed_events.append(deadline.get('title'))
                print(f"❌ Failed to add: {deadline.get('title')}")
        
        return {
            'success': True,
            'added': added_events,
            'failed': failed_events,
            'message': f'Added {len(added_events)} reminders to Google Calendar'
        }
    
    except Exception as e:
        print(f"Error in add_reminders_to_calendar: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'message': str(e)
        }
