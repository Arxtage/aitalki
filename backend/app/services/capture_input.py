# FRONTEND

import pyaudio
import webrtcvad
import collections
import pathlib
import io
from pydub import AudioSegment

# Initialize PyAudio
p = pyaudio.PyAudio()

# Configure audio stream (Mono, 16kHz, 16-bit)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK_DURATION_MS = 30  # Each chunk will be 30ms of audio
CHUNK_SIZE = int(RATE * CHUNK_DURATION_MS / 1000)  # Number of frames per chunk
FRAME_DURATION_MS = 10  # Frame duration for VAD

# Initialize WebRTC VAD
vad = webrtcvad.Vad()
vad.set_mode(1)  # 0-3, 0: Least aggressive, 3: Most aggressive

# Recording parameters
padding_duration_ms = 1000  # Silence padding to add before stopping
num_padding_chunks = int(padding_duration_ms / CHUNK_DURATION_MS)

def capture_audio_bytes():
    """
    Capture audio from the microphone based on voice activity.
    
    Returns:
        bytes: Captured audio data in MP3 format
    """
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                    frames_per_buffer=CHUNK_SIZE)

    print("Listening...")

    frames = collections.deque(maxlen=num_padding_chunks)  # Store recent frames
    triggered = False
    voiced_frames = []

    while True:
        chunk = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        is_speech = vad.is_speech(chunk, RATE)

        if is_speech:
            if not triggered:
                print("Voice detected, capturing audio bytes...")
                triggered = True
            voiced_frames.extend(frames)
            voiced_frames.append(chunk)
            frames.clear()  # Reset recent frames
        else:
            if triggered:
                print("Silence detected, waiting for more speech or stopping...")
                frames.append(chunk)
                if len(frames) == num_padding_chunks:
                    print("Stopping capture.")
                    break
            else:
                frames.append(chunk)

    # Stop recording
    stream.stop_stream()
    stream.close()

    # Convert frames to MP3 format in memory
    audio_bytes = b''.join(voiced_frames)
    
    # Create an AudioSegment from the raw audio data
    audio_segment = AudioSegment(
        data=audio_bytes,
        sample_width=p.get_sample_size(FORMAT),
        frame_rate=RATE,
        channels=CHANNELS
    )

    # Save the audio segment to a BytesIO object in MP3 format
    mp3_io = io.BytesIO()
    audio_segment.export(mp3_io, format="mp3")
    mp3_io.seek(0)  # Move to the beginning of the BytesIO buffer
    return mp3_io.read()  # Return the MP3 data as bytes

# Close PyAudio instance
def close_audio():
    p.terminate()

def capture_audio_file():
    """
    Capture audio from file.
    
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
