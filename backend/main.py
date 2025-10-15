from flask import Flask, request, jsonify
from flask_cors import CORS
from .routes import process_meeting, add_reminders_to_calendar
import os
import traceback

app = Flask(__name__)
CORS(app)

# ... rest of your code stays the same

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    """Handle audio file upload and processing"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        result = process_meeting(audio_file)
        return jsonify({'success': True, 'summary': result['summary'], 'deadlines': result['deadlines']}), 200

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except RuntimeError as e:
        return jsonify({'success': False, 'error': str(e)}), 502
    except Exception as e:
        # Log full traceback to server console for debugging
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/add-to-calendar', methods=['POST'])
def add_to_calendar():
    """Add deadlines to Google Calendar"""
    try:
        data = request.json
        deadlines = data.get('deadlines', [])
        
        if not deadlines:
            return jsonify({'error': 'No deadlines provided'}), 400
        
        result = add_reminders_to_calendar(deadlines)
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)

# Streamlit helper to call Flask logic directly
def handle_audio_upload(uploaded_file):
    """Used by Streamlit `frontend/app.py` to process uploads without HTTP.
    Accepts a file-like object with `.read()` and `.name` and returns
    the result dict from `process_meeting`.
    """
    if not uploaded_file:
        raise ValueError('No audio file provided')
    return process_meeting(uploaded_file)