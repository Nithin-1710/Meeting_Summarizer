# backend/services.py
import openai
from io import BytesIO
from backend import config  # this sets openai.api_key


def transcribe_audio(file: BytesIO) -> str:
    """Transcribe meeting audio using OpenAI Whisper"""
    try:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=file
        )
        return transcript.text
    except Exception as e:
        return f"Transcription failed: {str(e)}"


def generate_summary(transcript: str) -> str:
    """Summarize transcript and extract action items"""
    prompt = f"""
    Summarize the following meeting transcript into:
    1. Key decisions
    2. Action items (with responsible persons if mentioned)
    3. Next steps

    Transcript:
    {transcript}
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary generation failed: {str(e)}"

def extract_deadlines_with_gpt(meeting_transcript, client):
    """
    Use GPT to extract deadlines from meeting transcript
    Returns list of tuples: (deadline_title, deadline_date, description)
    """
    extraction_prompt = """
    Analyze the following meeting transcript and extract all deadlines, tasks with due dates, 
    and important dates mentioned. 
    
    For each deadline found, provide:
    1. Task/Deadline title
    2. Due date (in YYYY-MM-DD format if possible, or natural language if exact date unclear)
    3. Brief description/context
    
    Format your response as a JSON array like this:
    [
        {
            "title": "Submit project proposal",
            "date": "2025-01-20",
            "description": "Project proposal for client meeting"
        },
        {
            "title": "Code review",
            "date": "2025-01-15",
            "description": "Review PR #123"
        }
    ]
    
    If no deadlines are found, return an empty array: []
    
    Meeting Transcript:
    {transcript}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # or "gpt-3.5-turbo" depending on your config
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting deadlines and important dates from meeting transcripts. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": extraction_prompt.format(transcript=meeting_transcript)
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent extraction
        )
        
        # Parse the JSON response
        import json
        deadlines_json = response.choices[0].message.content
        deadlines = json.loads(deadlines_json)
        
        return deadlines
    
    except json.JSONDecodeError:
        print("Failed to parse GPT response as JSON")
        return []
    except Exception as e:
        print(f"Error extracting deadlines with GPT: {str(e)}")
        return []