# backend/routes.py
from .services import transcribe_audio, generate_summary
from .utils import save_text
import io

def process_meeting(audio_file) -> dict:
    """Process the uploaded meeting audio and return results"""
    audio_bytes = io.BytesIO(audio_file.read())
    audio_bytes.name = audio_file.name

    transcript = transcribe_audio(audio_bytes)
    summary = generate_summary(transcript)

    # Save outputs for reference
    transcript_path = save_text("transcript.txt", transcript)
    summary_path = save_text("summary.txt", summary)

    return {
        "transcript": transcript,
        "summary": summary,
        "files": {
            "transcript": transcript_path,
            "summary": summary_path
        }
    }
