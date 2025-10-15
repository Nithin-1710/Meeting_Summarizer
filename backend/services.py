# backend/services.py
from io import BytesIO
from .db_config import client  # Corrected import
import json


def transcribe_audio(file: BytesIO) -> str:
    """Transcribe meeting audio using OpenAI Whisper."""
    file.seek(0)  # ensure pointer at start
    print(f"DEBUG: Sending file {file.name}, size={len(file.getbuffer())} bytes")
    
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=file
    )
    
    # Debug: print raw response
    print(f"DEBUG: Whisper API raw response: {transcript}")
    
    # Parse text
    if isinstance(transcript, dict):
        text = transcript.get('text')
    else:
        text = getattr(transcript, 'text', None)
    
    if not text:
        raise RuntimeError(
            "Transcription returned no text. Confirm audio format. "
            "Check Whisper raw response in logs."
        )
    return text


def generate_summary(transcript: str) -> str:
    """Summarize transcript and extract action items."""
    prompt = f"""
    Summarize the following meeting transcript into:
    1. Key decisions
    2. Action items (with responsible persons if mentioned)
    3. Next steps

    Transcript:
    {transcript}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    content = response.choices[0].message.content.strip()
    if not content:
        raise RuntimeError("Empty summary returned.")
    return content


def extract_deadlines_with_gpt(meeting_transcript):
    """
    Use GPT to extract deadlines from meeting transcript.
    Returns list of dictionaries with deadline info.
    """
    extraction_prompt = f"""
    Analyze the following meeting transcript and extract all deadlines, tasks with due dates, 
    and important dates mentioned. 

    Return ONLY a valid JSON array, nothing else. No markdown, no extra text.

    For each deadline found, provide:
    1. Task/Deadline title
    2. Due date (YYYY-MM-DD if possible, or natural language)
    3. Brief description/context

    Example format:
    [
        {{
            "title": "Submit project proposal",
            "date": "2025-01-20",
            "description": "Project proposal for client meeting"
        }},
        {{
            "title": "Code review",
            "date": "2025-01-15",
            "description": "Review PR #123"
        }}
    ]

    If no deadlines are found, return: []

    Meeting Transcript:
    {meeting_transcript}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting deadlines and important dates from meeting transcripts. Always respond with ONLY valid JSON, no other text or markdown."
                },
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ],
            temperature=0.3,
        )

        # Parse the JSON response
        response_text = response.choices[0].message.content.strip()

        # Debug: print the raw response
        print(f"DEBUG: Raw GPT response: {response_text}")

        # Remove code block markers if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        response_text = response_text.strip()
        
        deadlines = json.loads(response_text)
        print(f"DEBUG: Successfully parsed deadlines: {deadlines}")
        
        return deadlines

    except json.JSONDecodeError as e:
        print(f"Failed to parse GPT response as JSON: {e}")
        print(f"Response was: {response_text}")
        return []
    except Exception as e:
        print(f"Error extracting deadlines with GPT: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
