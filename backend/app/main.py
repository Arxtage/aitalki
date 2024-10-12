import google.generativeai as genai
from google.cloud import texttospeech
from utils.prompts import CALIFORNIAN_ENGLISH_PROMPT
from utils.strip_markdown import strip_markdown
import os
import pathlib

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('models/gemini-1.5-pro')

prompt = CALIFORNIAN_ENGLISH_PROMPT

gemini_response = model.generate_content([
    prompt,
    {
        "mime_type": "audio/mp3",
        "data": pathlib.Path('./media/m5_audio.mp3').read_bytes()
    }
])

# Output Gemini's response to the prompt and the inline audio.
print(gemini_response.text)
gemini_response_text = strip_markdown(gemini_response.text)
print(gemini_response_text)


tts_client = texttospeech.TextToSpeechClient()

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", name="en-US-Casual-K", ssml_gender=texttospeech.SsmlVoiceGender.MALE
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)
synthesis_input = texttospeech.SynthesisInput(text=gemini_response_text)

response = tts_client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

with open("./media/output.mp3", "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "output.mp3"')
