# app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from backend.main import handle_audio_upload
import io

st.set_page_config(page_title="Meeting Summarizer", page_icon="🎙️")
st.title(" Meeting Summarizer")

audio = st.file_uploader("Upload meeting audio", type=["mp3", "wav", "m4a"])

if audio:
    with st.spinner("Processing your meeting..."):
        result = handle_audio_upload(audio)

    st.subheader(" Transcript")
    st.write(result["transcript"])

    st.subheader(" Summary & Action Items")
    st.write(result["summary"])
