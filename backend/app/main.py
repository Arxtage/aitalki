# BACKEND
import os
from constants import MAIN_PAGE_HTML
from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from authlib.integrations.starlette_client import OAuth, OAuthError
import uuid
import time
from pydantic import BaseModel
from dotenv import load_dotenv
import secrets
from starlette.middleware.sessions import SessionMiddleware
from starlette.applications import Starlette
from starlette.responses import RedirectResponse

from backend.app.services.capture_input import capture_audio_bytes, close_audio
from backend.app.services.gemini import call_gemini
from backend.app.services.text_to_speech import text_to_speech
from backend.app.utils.play_audio import play_audio
from backend.app.utils.prompts import FIVE_MINUTES_LEFT_SIGNAL

load_dotenv()

app = FastAPI()

SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# TODO: Check the Security
# TODO: Remove localhost from allowed js in Google Cloud after deploying
# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.environ['GOOGLE_AUTH_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_AUTH_CLIENT_SECRET'],
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': 'http://localhost:8000/auth'
    }
)

class User(BaseModel):
    email: str
    name: str

def get_current_user(request: Request) -> User:
    user_info = request.session.get('user')
    if user_info:
        return User(email=user_info['email'], name=user_info['name'])
    raise HTTPException(status_code=401, detail="Not authenticated")

@app.get("/")
async def get(current_user: User = Depends(get_current_user)):
    return HTMLResponse(MAIN_PAGE_HTML)

@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse('/')

# New WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: User = Depends(get_current_user)):
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
