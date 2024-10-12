from dotenv import load_dotenv
from services.audio_capture import capture_audio
from services.gemini import call_gemini
from services.text_to_speech import text_to_speech
from utils.conversation_manager import ConversationManager


load_dotenv()

def main():
    conversation_manager = ConversationManager()
    
    for _ in range(1):
        # Capture audio
        audio_data = capture_audio()
        
        # Get conversation token
        conversation_token = conversation_manager.get_or_create_token()
        
        # Call Gemini
        gemini_response = call_gemini(audio_data, conversation_token)
        
        # Convert response to speech
        audio_response = text_to_speech(gemini_response)
        
        # Play audio response (implement this function)
        # play_audio(audio_response)

        with open("./media/output.mp3", "wb") as out:
        # Write the response to the output file.
            out.write(audio_response)
            print('Audio content written to file "output.mp3"')
        
        # Update conversation state
        conversation_manager.update_conversation(conversation_token, gemini_response)

if __name__ == "__main__":
    main()
