# BACKEND

import uuid
import time
import os
import sys

from dotenv import load_dotenv

# Add the parent directory of local_backend and backend to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.capture_input import capture_audio_bytes, capture_text, close_audio
from backend.app.services.gemini import call_gemini
from backend.app.services.text_to_speech import text_to_speech
from backend.app.utils.play_audio import play_audio
from backend.app.utils.prompts import FIVE_MINUTES_LEFT_SIGNAL


load_dotenv()

def main(conversation_token: str):
    lesson_duration = 15 * 60  # 30 mins
    t_end = time.time() + lesson_duration
    end_lesson_warning_sent = False

    while time.time() < t_end:
        # Capture input
        data = capture_audio_bytes()  # Use the new audio capture function
        # data = capture_text()  # Uncomment this line if you want to capture text input instead

        remaining_time = t_end - time.time()
        if remaining_time <= 300 and not end_lesson_warning_sent:  # Less than or equal to 5 mins
            # Send a message to the LLM that 5 minutes are left
            gemini_response = call_gemini(data, conversation_token=conversation_token, time_signal=FIVE_MINUTES_LEFT_SIGNAL)
            end_lesson_warning_sent = True  # Set the flag to True after sending the warning
        else:
            # Call Gemini without the time signal
            gemini_response = call_gemini(data, conversation_token=conversation_token)

        # Convert response to speech
        audio_response = text_to_speech(gemini_response)

        # Play audio response (implement this function)
        play_audio(audio_response)

        # with open("./media/output.mp3", "wb") as out:
        #     # Write the response to the output file.
        #     out.write(audio_response)
        #     print('Audio content written to file "output.mp3"')
    
    close_audio()

if __name__ == "__main__":
    # main(conversation_token='1')
    main(conversation_token=uuid.uuid4().hex) # random token on each run
