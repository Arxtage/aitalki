import io
import tempfile
from playsound import playsound

def play_audio(audio_data):
    """
    Play audio data using playsound.
    
    Args:
        audio_data (bytes): Audio data to be played.
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
        temp_audio.write(audio_data)
        temp_audio_path = temp_audio.name

    # Play the audio
    playsound(temp_audio_path)

    # The temporary file will be automatically deleted when the function exits

