import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from bson.objectid import ObjectId  # move import to top

load_dotenv()

# MongoDB connection (local)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/meeting_summarizer")
client = MongoClient(MONGODB_URI)
db = client['meeting_summarizer']
meetings_collection = db['meetings']

# Rest of your original functions remain unchanged
def save_meeting_summary(filename, transcript, summary, deadlines):
    try:
        meeting_doc = {
            'filename': filename,
            'transcript': transcript,
            'summary': summary,
            'deadlines': deadlines,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = meetings_collection.insert_one(meeting_doc)
        print(f"✅ Meeting saved to database with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"❌ Error saving to database: {e}")
        return None

def get_all_meetings(limit=50, skip=0):
    try:
        meetings = list(meetings_collection.find()
                       .sort('created_at', -1)
                       .skip(skip)
                       .limit(limit))
        for m in meetings:
            m['_id'] = str(m['_id'])
        return meetings
    except Exception as e:
        print(f"❌ Error fetching meetings: {e}")
        return []

def get_meeting_by_id(meeting_id):
    try:
        meeting = meetings_collection.find_one({'_id': ObjectId(meeting_id)})
        if meeting:
            meeting['_id'] = str(meeting['_id'])
        return meeting
    except Exception as e:
        print(f"❌ Error fetching meeting by ID: {e}")
        return None

def search_meetings(query):
    try:
        meetings = list(meetings_collection.find({
            '$or': [
                {'filename': {'$regex': query, '$options': 'i'}},
                {'summary': {'$regex': query, '$options': 'i'}},
                {'transcript': {'$regex': query, '$options': 'i'}}
            ]
        }).sort('created_at', -1).limit(20))
        for m in meetings:
            m['_id'] = str(m['_id'])
        return meetings
    except Exception as e:
        print(f"❌ Error searching meetings: {e}")
        return []

def delete_meeting(meeting_id):
    try:
        result = meetings_collection.delete_one({'_id': ObjectId(meeting_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"❌ Error deleting meeting: {e}")
        return False

def get_meeting_statistics():
    try:
        total_meetings = meetings_collection.count_documents({})
        total_deadlines = sum(len(m.get('deadlines', [])) for m in meetings_collection.find({}, {'deadlines': 1}))
        return {
            'total_meetings': total_meetings,
            'total_deadlines': total_deadlines,
            'average_deadlines_per_meeting': total_deadlines / total_meetings if total_meetings else 0
        }
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return {
            'total_meetings': 0,
            'total_deadlines': 0,
            'average_deadlines_per_meeting': 0
        }
