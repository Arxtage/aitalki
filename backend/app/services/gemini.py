import os
import google.generativeai as genai

from utils.prompts import CALIFORNIAN_ENGLISH_PROMPT
from utils.strip_markdown import strip_markdown

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def call_gemini(audio_data: bytes, conversation_token: str):
    """
    Call Gemini API with audio data and conversation context.
    
    TODO:
    - Implement Gemini API call
    - Handle conversation context using the token
    - Process and return the response
    
    Args:
        audio_data (bytes): Audio data to be sent to Gemini
        conversation_token (str): Token to identify the conversation
    
    Returns:
        str: Gemini's response
    """
    model = genai.GenerativeModel('models/gemini-1.5-pro') # TODO: do not reinitialize model for each call
    prompt = CALIFORNIAN_ENGLISH_PROMPT

    gemini_response = model.generate_content([
        prompt,
        {
            "mime_type": "audio/mp3",
            # "data": pathlib.Path('./media/m5_audio.mp3').read_bytes()
            "data": audio_data
        }
    ])

    # Output Gemini's response to the prompt and the inline audio.
    print(gemini_response.text)
    gemini_response_text = strip_markdown(gemini_response.text)
    print(gemini_response_text)
    return gemini_response_text
