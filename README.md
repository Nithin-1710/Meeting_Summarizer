# Meeting Summariser 📝🤖

**Meeting Summariser** is a Python-based AI tool that automates meeting documentation. It transcribes meeting audio, generates AI summaries, extracts actionable deadlines, and optionally integrates with Google Calendar.  

---

## **Key Features**

- **Audio Transcription**: Converts meeting audio (MP3, WAV) into text using OpenAI Whisper.  
- **AI Summarization**: Summarizes key decisions, action items, and next steps using GPT models.  
- **Deadline Extraction**: Detects tasks and due dates from transcripts using GPT-based parsing.  
- **Data Persistence**: Stores meeting data in MongoDB for easy retrieval.  
- **Calendar Integration**: Automatically adds deadlines to Google Calendar.  
- **Frontend**: Simple Streamlit UI for uploading audio and viewing results.  

---

## **Tech Stack**

- **Backend**: Python, Flask, OpenAI API, PyMongo  
- **Frontend**: Streamlit  
- **Database**: MongoDB (Local/Community Server)  
- **External APIs**: Google Calendar API  

---

## **Project Highlights**

- Fully modular backend separating services, database, and utility logic.  
- Robust error handling for API responses and database operations.  
- Optimized for ease of integration into larger projects or enterprise pipelines.  

---

## **Screenshots**  

*(Optional: show the functionality without overwhelming detail)*  

### Transcript & Summary
![Transcript Screenshot](transcript.png)  

### Deadlines Added
![Deadlines Screenshot](deadlines.png)  

---

## **Setup (Optional for Review)**  

- Requires Python 3.10+ and a virtual environment  
- Install dependencies:  
```bash
pip install -r requirements.txt
