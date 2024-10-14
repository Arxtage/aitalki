import uuid
import time

from dotenv import load_dotenv
from services.capture_input import capture_audio, capture_text
from services.gemini import call_gemini
from services.text_to_speech import text_to_speech
from utils.play_audio import play_audio
from utils.prompts import FIVE_MINUTES_LEFT_SIGNAL


load_dotenv()

def main(conversation_token: str):
    lesson_duration = 30 * 60  # 30 mins
    t_end = time.time() + lesson_duration
    end_lesson_warning_sent = False

    while time.time() < t_end:
        # Capture input
        # data = capture_audio()
        data = capture_text()

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

        with open("./media/output.mp3", "wb") as out:
            # Write the response to the output file.
            out.write(audio_response)
            print('Audio content written to file "output.mp3"')


if __name__ == "__main__":
    # main(conversation_token='1')
    main(conversation_token=uuid.uuid4().hex) # random token on each run
