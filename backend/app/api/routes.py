# BACKEND

from fastapi import FastAPI, File, UploadFile
from backend.app.services.capture_input import capture_audio
from backend.app.services.gemini import call_gemini
from backend.app.services.text_to_speech import text_to_speech

app = FastAPI()

@app.post("/chat")
async def chat(audio: UploadFile = File(...)):
    """
    Handle chat requests via FastAPI.
    
    TODO:
    - Implement FastAPI route for chat functionality
    - Process incoming audio file
    - Return audio response
    
    Args:
        audio (UploadFile): Uploaded audio file
    
    Returns:
        dict: Response containing audio data and metadata
    """
    pass

