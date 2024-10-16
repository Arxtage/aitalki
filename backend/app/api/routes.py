# BACKEND

from fastapi import FastAPI, File, UploadFile
from services.capture_input import capture_audio
from services.gemini import call_gemini
from services.text_to_speech import text_to_speech

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

