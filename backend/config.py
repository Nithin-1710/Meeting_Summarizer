# backend/config.py
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# Get the API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")
