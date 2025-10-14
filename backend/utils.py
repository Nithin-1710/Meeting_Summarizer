# backend/utils.py
import os

def save_text(filename: str, content: str, folder="outputs"):
    """Save text output (transcript or summary) to a file"""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
