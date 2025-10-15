# backend/db_config.py
import os
from dotenv import load_dotenv
from openai import OpenAI
import openai  # for legacy compatibility

# Load environment variables from .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

# OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Legacy openai namespace
openai.api_key = api_key
