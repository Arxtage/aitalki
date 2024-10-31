# BACKEND
import os

from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
import uuid
import time
from pydantic import BaseModel
from dotenv import load_dotenv
import secrets
import jwt
from datetime import datetime, timedelta
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.applications import Starlette
from starlette.responses import RedirectResponse

from app.services.gemini import call_gemini
from app.services.text_to_speech import text_to_speech
from app.utils.prompts import FIVE_MINUTES_LEFT_SIGNAL

load_dotenv(dotenv_path='.env')

app = FastAPI()

SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
JWT_SECRET = os.environ.get('JWT_SECRET') or secrets.token_hex(32)
STAGE = os.environ.get('STAGE')

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
        # 'redirect_url': 'http://localhost:8000/api/auth'
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_token(user_info):
    expiration = datetime.utcnow() + timedelta(hours=2)  # 2-hour expiration
    payload = {
        'sub': user_info['email'],
        'name': user_info['name'],
        'exp': expiration
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/user")
async def get_user(request: Request):
    user = request.session.get('user')
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = create_token(user)
    return {"user": user, "token": token}

@app.get("/api/login")
async def login(request: Request):
    print(f'== Entered Login')
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/api/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
        jwt_token = create_token(dict(user))
        response = RedirectResponse(url="http://localhost:3000/lesson")
        # Set the cookie on the response
        print(f' ==== Set new cookie for user: {jwt_token}')
        response.set_cookie(
            key="jwt_token",
            value=jwt_token,
            httponly=False,
            samesite="None",
            secure=False  # False for local development; set True in production over HTTPS
        )
        return response
    raise HTTPException(status_code=401, detail="Authentication failed")

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    print(f'== WS ENDPOINT ENTERED')
    try:
        user = verify_token(token)  # Verify the token
        print(f' === WS USER: {user}')
    except HTTPException as e:
        print(f"== TOKEN NOT VERIFIED: {token}")
        await websocket.close(code=1008)  # Close with error code
        return

    await websocket.accept()
    conversation_token = uuid.uuid4().hex
    lesson_duration = 15 * 60  # 15 minutes
    t_end = time.time() + lesson_duration
    end_lesson_warning_sent = False

    while time.time() < t_end:
        data = await websocket.receive_bytes()

        remaining_time = t_end - time.time()
        if remaining_time <= 300 and not end_lesson_warning_sent:
            gemini_response = await call_gemini(data, conversation_token=conversation_token, time_signal=FIVE_MINUTES_LEFT_SIGNAL)
            end_lesson_warning_sent = True
        else:
            gemini_response = await call_gemini(data, conversation_token=conversation_token)

        audio_response = await text_to_speech(gemini_response)
        await websocket.send_bytes(audio_response)
