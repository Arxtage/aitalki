import uuid

from dotenv import load_dotenv
from services.audio_capture import capture_audio, capture_text
from services.gemini import call_gemini
from services.text_to_speech import text_to_speech
from utils.play_audio import play_audio


load_dotenv()

def main(conversation_token: str):

    for _ in range(5):
        # Capture input
        # data = capture_audio()
        data = capture_text()

        # Call Gemini
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
