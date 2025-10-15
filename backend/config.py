# backend/config.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import openai  # ensure legacy namespace is configured for modules using it

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Get the API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Also set API key on the legacy `openai` namespace used in parts of the codebase
openai.api_key = api_key