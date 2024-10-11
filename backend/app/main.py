import google.generativeai as genai
from google.cloud import texttospeech
from utils.prompts import CALIFORNIAN_ENGLISH_PROMPT
import os
import pathlib

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel('models/gemini-1.5-flash')
# response = model.generate_content("Hello World! What is the meaning of Life by Hitchhikers Guide to the Galaxy? Give me Shortest Answer Possible.")
# print(response.text)

# Create the prompt.
prompt = CALIFORNIAN_ENGLISH_PROMPT

# Load the samplesmall.mp3 file into a Python Blob object containing the audio
# file's bytes and then pass the prompt and the audio to Gemini.
gemini_response = model.generate_content([
    prompt,
    {
        "mime_type": "audio/mp3",
        "data": pathlib.Path('./media/m5_audio.mp3').read_bytes()
    }
])

# Output Gemini's response to the prompt and the inline audio.
print(gemini_response.text)


tts_client = texttospeech.TextToSpeechClient()

voice = texttospeech.VoiceSelectionParams(
    language_code="en-US", name="en-US-Casual-K", ssml_gender=texttospeech.SsmlVoiceGender.MALE
)

audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)
synthesis_input = texttospeech.SynthesisInput(text=gemini_response.text)

response = tts_client.synthesize_speech(
    input=synthesis_input, voice=voice, audio_config=audio_config
)

with open("./media/output.mp3", "wb") as out:
    # Write the response to the output file.
    out.write(response.audio_content)
    print('Audio content written to file "full_presentation_feedback.mp3"')
