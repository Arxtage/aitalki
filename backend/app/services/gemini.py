# BACKEND

import os
import google.generativeai as genai
import logging

from app.utils.prompts import CALIFORNIAN_ENGLISH_SYSTEM_PROMPT, SIMPLE_CALIFORNIAN_ENGLISH_SYSTEM_PROMPT
from app.utils.strip_markdown import strip_markdown
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Store chat sessions
chat_sessions = {}

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = CALIFORNIAN_ENGLISH_SYSTEM_PROMPT

# File to log conversation history
LOG_FILE_PATH = 'conversation_history.txt'

def log_conversation(conversation_token: str, message: str):
    """Append the conversation message to a log file."""
    with open(LOG_FILE_PATH, 'a') as log_file:
        logger.info(f'== Logging to file:')
        log_file.write(f"Conversation Token: {conversation_token}\n")
        log_file.write(f"{message}\n")
        log_file.write("-" * 40 + "\n")  # Separator for readability

async def call_gemini(input_data: bytes | str, conversation_token: str, time_signal: str = None):
    """
    Call Gemini API with audio data or text and conversation context.
    
    Args:
        input_data (bytes or str): Audio data or text to be sent to Gemini
        conversation_token (str): Token to identify the conversation
        time_signal (str, optional): Signal to indicate time left in the lesson
    
    Returns:
        str: Gemini's response
    """
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    # Get or create a chat session for this conversation
    if conversation_token not in chat_sessions:
        chat_sessions[conversation_token] = model.start_chat(history=[])
        include_system_prompt = True  # First message, include system prompt
    else:
        include_system_prompt = False  # Not the first message, do not include system prompt

    chat: genai.ChatSession = chat_sessions[conversation_token]

    # Prepare the message to send
    message_to_send = []
    if time_signal:
        message_to_send.append(time_signal)  # Add the time signal if provided

    # Determine the type of input and send the message accordingly
    if isinstance(input_data, bytes):
        if include_system_prompt:
            message_to_send.append(SYSTEM_PROMPT)
            message_to_send.append("User audio:")
            message_to_send.append({
                "mime_type": "audio/mp3",
                "data": input_data
            })
        else:
            message_to_send.append("User audio:")
            message_to_send.append({
                "mime_type": "audio/mp3",
                "data": input_data
            })
    elif isinstance(input_data, str):
        if include_system_prompt:
            message_to_send.append(SYSTEM_PROMPT)  # Include system prompt for text
            message_to_send.append("User: " + input_data)
        else:
            message_to_send.append(input_data)  # Only include user message for text
    else:
        raise ValueError("input_data must be either bytes (audio) or str (text)")

    logger.info("=== Sending User Message")
    
    # Log the user message
    log_conversation(conversation_token, f"User: {input_data if isinstance(input_data, str) else 'Audio data sent'}")

    gemini_response = await chat.send_message_async(message_to_send) # TODO: Add stream=True

    # Ensure the response is fully resolved before accessing its attributes
    await gemini_response.resolve()  # Wait for the response to complete

    logger.info(f'==== Chat History Length: {len(chat.history)}')
    # Process and return the response
    logger.info(f"=== Teacher Response: {gemini_response.text}")
    
    # Log the teacher's response
    log_conversation(conversation_token, f"Teacher: {gemini_response.text}")

    gemini_response_text = strip_markdown(gemini_response.text)
    return gemini_response_text

# TODO: Implement a function to clear chat sessions when they're no longer needed
