# backend/routes.py
from .services import transcribe_audio, generate_summary, extract_deadlines_with_gpt
from .utils import save_text, get_calendar_service, add_calendar_reminder
from .config import client
import io

# ... rest stays the same

def process_meeting(audio_file) -> dict:
    """Process the uploaded meeting audio and return results"""
    audio_bytes = io.BytesIO(audio_file.read())
    audio_bytes.name = audio_file.name
    audio_bytes.seek(0)
    # Step 1: Transcription
    transcript = transcribe_audio(audio_bytes)
    if not transcript or transcript.lower().startswith("transcription failed"):
        raise ValueError("Transcription failed. Please ensure the audio is a supported format like .mp3, .wav, or .m4a and try again.")

    # Step 2: Summarization
    summary = generate_summary(transcript)
    if not summary or summary.lower().startswith("summary generation failed"):
        raise RuntimeError("Summary generation failed. Please retry in a moment.")
    
    # Extract deadlines using GPT
    deadlines = extract_deadlines_with_gpt(transcript, client)

    # Save outputs for reference
    transcript_path = save_text("transcript.txt", transcript)
    summary_path = save_text("summary.txt", summary)

    return {
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
        added_events = []
        failed_events = []
        
        for deadline in deadlines:
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
            else:
                failed_events.append(deadline.get('title'))
        
        return {
            'success': True,
            'added': added_events,
            'failed': failed_events,
            'message': f'Added {len(added_events)} reminders to Google Calendar'
        }
    
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }