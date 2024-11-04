# BACKEND
import os

from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException, logger
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
import logging

from app.services.gemini import call_gemini
from app.services.text_to_speech import text_to_speech
from app.utils.prompts import FIVE_MINUTES_LEFT_SIGNAL

LESSON_DURATION_SEC = 30 * 60 # 30 min

# Set up logging at the top of your file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path='.env')

app = FastAPI()

SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
JWT_SECRET = os.environ.get('JWT_SECRET') or secrets.token_hex(32)
STAGE = os.environ.get('STAGE')

is_prod = True if STAGE == "prod" else False
API_URL = "https://aitalki.app" if is_prod else "http://localhost:3000"
print(f'==== API_URL: {API_URL}')
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
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[API_URL],  # Only React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_token(user_info):
    expiration = datetime.utcnow() + timedelta(hours=24)  # 24-hour expiration
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
        response = RedirectResponse(url=f"{API_URL}/lesson")
        # Set the cookie on the response
        print(f' ==== Set new cookie for user: {jwt_token}')
        response.set_cookie(
            key="jwt_token",
            value=jwt_token,
            httponly=False,
            samesite="None",
            secure=True if is_prod else False  # False for local development; set True in production over HTTPS
        )
        return response
    raise HTTPException(status_code=401, detail="Authentication failed")

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, token: str):
    logger.info("== WS ENDPOINT ENTERED")
    try:
        user = verify_token(token)
        logger.info(f" === WS USER: {user}")
    except HTTPException as e:
        logger.error(f"== TOKEN NOT VERIFIED: {token}, error: {e}")
        await websocket.close(code=1008)
        return

    await websocket.accept()
    conversation_token = uuid.uuid4().hex
    lesson_duration = LESSON_DURATION_SEC
    t_end = time.time() + lesson_duration
    end_lesson_warning_sent = False

    while time.time() < t_end:
        data = await websocket.receive_bytes()

        remaining_time = t_end - time.time()
        start_gemini = time.time()

        if remaining_time <= 300 and not end_lesson_warning_sent:
            gemini_response = await call_gemini(data, conversation_token=conversation_token, time_signal=FIVE_MINUTES_LEFT_SIGNAL)
            end_lesson_warning_sent = True
        else:
            gemini_response = await call_gemini(data, conversation_token=conversation_token)
            
        gemini_duration = time.time() - start_gemini
        logger.info(f"=== Gemini API call took: {gemini_duration:.2f} seconds")

        start_tts = time.time()
        audio_response = await text_to_speech(gemini_response)
        tts_duration = time.time() - start_tts
        logger.info(f"=== Text-to-Speech took: {tts_duration:.2f} seconds")

        total_duration = gemini_duration + tts_duration
        print(f"=== Total processing time: {total_duration:.2f} seconds")

        await websocket.send_bytes(audio_response)
