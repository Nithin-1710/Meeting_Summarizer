import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from backend.main import handle_audio_upload
from backend.routes import add_reminders_to_calendar

st.set_page_config(page_title="Meeting Summarizer", page_icon="🎙️")
st.title("🎙️ Meeting Summarizer")

audio = st.file_uploader("Upload meeting audio", type=["mp3", "wav", "m4a"])

if audio:
    try:
        with st.spinner("Processing your meeting..."):
            result = handle_audio_upload(audio)
        
        st.subheader("📋 Summary & Action Items")
        st.write(result["summary"])
        
        deadlines = result.get("deadlines", [])
        if deadlines:
            st.subheader("📅 Extracted Deadlines")
            for i, deadline in enumerate(deadlines):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{deadline.get('title')}** - Due: {deadline.get('date')}")
                    st.caption(deadline.get('description', ''))
            
            # Add button to save to Google Calendar
            if st.button("📅 Add All Deadlines to Google Calendar"):
                with st.spinner("Adding reminders to your Google Calendar..."):
                    calendar_result = add_reminders_to_calendar(deadlines)
                    if calendar_result['success']:
                        st.success(f"✅ {calendar_result['message']}")
                        if calendar_result.get('added'):
                            st.write("Added:")
                            for event in calendar_result['added']:
                                st.write(f"  • {event['title']}")
                        if calendar_result.get('failed'):
                            st.warning(f"Failed to add: {', '.join(calendar_result['failed'])}")
                    else:
                        st.error(f"❌ Error: {calendar_result['message']}")
        else:
            st.info("No deadlines found in this meeting.")
    
    except Exception as e:
        st.error(f"❌ Error processing the audio: {str(e)}")
