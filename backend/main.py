# backend/main.py
from .routes import process_meeting

def handle_audio_upload(audio_file):
    """Main entry function for Streamlit frontend"""
    result = process_meeting(audio_file)
    return result
