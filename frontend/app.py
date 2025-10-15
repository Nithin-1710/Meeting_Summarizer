import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from backend.main import handle_audio_upload
from backend.routes import add_reminders_to_calendar
from backend.database import get_all_meetings, get_meeting_by_id, delete_meeting, search_meetings, get_meeting_statistics

# Page configuration
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4F46E5;
        color: white;
        border-radius: 10px;
        padding: 0.75rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #4338CA;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }
    .deadline-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: white;
    }
    .summary-box {
        background: #F9FAFB;
        padding: 2rem;
        border-radius: 12px;
        border-left: 4px solid #4F46E5;
        margin: 1rem 0;
    }
    .meeting-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s;
    }
    .meeting-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #4F46E5;
    }
    h1 {
        color: #1F2937;
        font-size: 3rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    .subtitle {
        text-align: center;
        color: #6B7280;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.title("📂 Navigation")
    page = st.radio("Go to", ["Upload New Meeting", "Meeting History", "Statistics"])
    
    st.markdown("---")
    st.markdown("### 🔍 Quick Search")
    search_query = st.text_input("Search meetings", placeholder="Enter keywords...")

# Main content based on selected page
if page == "Upload New Meeting":
    # Header
    st.markdown("# Meeting Summarizer")
    st.markdown('<p class="subtitle">Upload your meeting audio and get an AI-powered summary with automatic deadline tracking</p>', unsafe_allow_html=True)

    # Create columns for better layout
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # File uploader
        audio = st.file_uploader(
            "Choose an audio file",
            type=["mp3", "wav", "m4a"],
            help="Supported formats: MP3, WAV, M4A"
        )

    if audio:
        try:
            with st.spinner("🔄 Processing your meeting... This may take a moment."):
                result = handle_audio_upload(audio)
            
            # Success message
            st.success("✅ Meeting processed and saved to database!")
            
            # Summary Section
            st.markdown("---")
            st.markdown("## 📋 Summary & Action Items")
            st.markdown(f'<div class="summary-box">{result["summary"]}</div>', unsafe_allow_html=True)
            
            # Deadlines Section
            deadlines = result.get("deadlines", [])
            if deadlines:
                st.markdown("---")
                st.markdown("## 📅 Extracted Deadlines")
                st.markdown(f"Found **{len(deadlines)}** deadline(s) in this meeting")
                
                for i, deadline in enumerate(deadlines):
                    st.markdown(f"""
                        <div class="deadline-card">
                            <h3 style="margin: 0; font-size: 1.3rem;">📌 {deadline.get('title')}</h3>
                            <p style="margin: 0.5rem 0; font-size: 1.1rem; opacity: 0.9;">
                                🗓️ Due: <strong>{deadline.get('date')}</strong>
                            </p>
                            <p style="margin: 0; opacity: 0.8;">{deadline.get('description', 'No additional details')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("")
                
                # Calendar button
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("📅 Add All Deadlines to Google Calendar"):
                        with st.spinner("🔄 Adding reminders to your Google Calendar..."):
                            calendar_result = add_reminders_to_calendar(deadlines)
                        
                        if calendar_result['success']:
                            st.success(f"✅ {calendar_result['message']}")
                            if calendar_result.get('added'):
                                st.markdown("**Successfully added:**")
                                for event in calendar_result['added']:
                                    st.write(f"  ✓ {event['title']}")
                        else:
                            st.error(f"❌ Error: {calendar_result['message']}")
            else:
                st.info("ℹ️ No deadlines found in this meeting.")
        
        except Exception as e:
            st.error(f"❌ Error processing the audio: {str(e)}")

elif page == "Meeting History":
    st.markdown("# 📚 Meeting History")
    st.markdown("View and manage your previous meeting summaries")
    
    # Search functionality
    if search_query:
        meetings = search_meetings(search_query)
        st.info(f"🔍 Found {len(meetings)} meeting(s) matching '{search_query}'")
    else:
        meetings = get_all_meetings(limit=20)
    
    if meetings:
        for meeting in meetings:
            with st.container():
                st.markdown(f"""
                    <div class="meeting-card">
                        <h3>📄 {meeting.get('filename', 'Unknown')}</h3>
                        <p style="color: #6B7280; font-size: 0.9rem;">
                            📅 {meeting.get('created_at', '').strftime('%B %d, %Y at %I:%M %p') if meeting.get('created_at') else 'Unknown date'}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    if st.button(f"View Summary", key=f"view_{meeting['_id']}"):
                        st.session_state[f"show_{meeting['_id']}"] = not st.session_state.get(f"show_{meeting['_id']}", False)
                
                with col2:
                    deadlines_count = len(meeting.get('deadlines', []))
                    st.metric("Deadlines", deadlines_count)
                
                with col3:
                    if st.button(f" Delete", key=f"delete_{meeting['_id']}"):
                        if delete_meeting(meeting['_id']):
                            st.success("Deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete")
                
                # Show summary if toggled
                if st.session_state.get(f"show_{meeting['_id']}", False):
                    st.markdown("**Summary:**")
                    st.markdown(f'<div class="summary-box">{meeting.get("summary", "No summary available")}</div>', unsafe_allow_html=True)
                    
                    if meeting.get('deadlines'):
                        st.markdown("**Deadlines:**")
                        for deadline in meeting['deadlines']:
                            st.write(f"• **{deadline.get('title')}** - Due: {deadline.get('date')}")
                
                st.markdown("---")
    else:
        st.info("📭 No meetings found. Upload your first meeting to get started!")

elif page == "Statistics":
    st.markdown("# 📊 Statistics")
    st.markdown("Overview of your meeting summaries")
    
    stats = get_meeting_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Meetings", stats['total_meetings'])
    
    with col2:
        st.metric("Total Deadlines", stats['total_deadlines'])
    
    with col3:
        st.metric("Avg Deadlines/Meeting", f"{stats['average_deadlines_per_meeting']:.1f}")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6B7280; padding: 2rem;">
        <p>Built with using Streamlit, OpenAI & MongoDB</p>
    </div>
""", unsafe_allow_html=True)