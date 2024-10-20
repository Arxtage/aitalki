# BACKEND
import os

from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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
from app.constants import MAIN_PAGE_HTML

load_dotenv(dotenv_path='.env')

app = FastAPI()

# Serve the React static files
app.mount("/static", StaticFiles(directory="frontend/build/static", html=True), name="static")

SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
JWT_SECRET = os.environ.get('JWT_SECRET') or secrets.token_hex(32)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000, http://localhost:8000"],  # Replace with your allowed origins
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
    
@app.get("/")
async def get(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/login')
    
    token = create_token(user)  # Create token for authenticated user
    response = HTMLResponse(content=open("frontend/build/index.html").read())
    print(f'== Set the token for user!!: {token}')
    response.set_cookie(key="jwt_token", value=token, httponly=True, samesite='none')  # Set the token in a cookie
    return response

@app.get("/login")
async def login(request: Request):
    print(f'== LOGIN ENDPOINT ENTERED')
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth')
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')
    print(f'== AUTH ENDPOINT ENTERED')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse('/')

@app.get("/{full_path:path}")
async def catch_all(full_path: str, request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse('/login')

    token = create_token(user)
    response = FileResponse("frontend/build/index.html")
    response.set_cookie(key="jwt_token", value=token, httponly=True)  # Set token in a cookie
    return response

# TODO: find a better way to pack these static files. Can not mount at root (/) as breaks WS endpoint as not http.
@app.get("/manifest.json", response_class=FileResponse)
async def manifest():
    return "frontend/build/manifest.json"

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("frontend/build/favicon.ico")

@app.get("/logo192.png")
async def logo():
    return FileResponse("frontend/build/logo192.png")

@app.websocket("/ws")
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
