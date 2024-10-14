import pathlib

def capture_audio():
    """
    Capture audio from the microphone or file.
    
    TODO:
    - Implement audio capture from microphone
    - Add option to read audio from file
    - Handle sent audio data (for future API implementation)
    
    Returns:
        bytes: Audio data
    """
    return pathlib.Path('./media/1min20sec_conversation.mp3').read_bytes()

def capture_text():
    text = input("User: ")
    return text
