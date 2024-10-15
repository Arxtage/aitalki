from google.cloud import texttospeech

def text_to_speech(text: str):
    """
    Convert text to speech using Google Cloud TTS.
    
    TODO:
    - Implement Google Cloud TTS API call
    - Handle voice selection and audio configuration
    - Return audio data
    
    Args:
        text (str): Text to be converted to speech
    
    Returns:
        bytes: Audio data of the synthesized speech
    """
    pass

    tts_client = texttospeech.TextToSpeechClient()

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Casual-K", ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.9
    )
    synthesis_input = texttospeech.SynthesisInput(text=text)

    response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    return response.audio_content