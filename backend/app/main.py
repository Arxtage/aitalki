# BACKEND

from fastapi import FastAPI, WebSocket
import uuid
import time
from backend.app.services.capture_input import capture_audio_bytes, close_audio
from backend.app.services.gemini import call_gemini
from backend.app.services.text_to_speech import text_to_speech
from backend.app.utils.play_audio import play_audio
from backend.app.utils.prompts import FIVE_MINUTES_LEFT_SIGNAL

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}


# New WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    conversation_token = uuid.uuid4().hex  # Generate a random token for the session
    lesson_duration = 15 * 60  # 15 minutes
    t_end = time.time() + lesson_duration
    end_lesson_warning_sent = False

    while time.time() < t_end:
        data = await websocket.receive_bytes()  # Receive bytes from the client

        remaining_time = t_end - time.time()
        if remaining_time <= 300 and not end_lesson_warning_sent:  # Less than or equal to 5 mins
            # Send a message to the LLM that 5 minutes are left
            gemini_response = await call_gemini(data, conversation_token=conversation_token, time_signal=FIVE_MINUTES_LEFT_SIGNAL)
            end_lesson_warning_sent = True  # Set the flag to True after sending the warning
        else:
            # Call Gemini without the time signal
            gemini_response = await call_gemini(data, conversation_token=conversation_token)

        # Convert response to speech
        audio_response = await text_to_speech(gemini_response)

        await websocket.send_bytes(audio_response)  # Send the audio response back to the client
