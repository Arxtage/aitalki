import React, { useState, useRef } from 'react';
import Cookies from 'js-cookie';

const WebSocketAudio: React.FC = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunks = useRef<Blob[]>([]);
    const socketRef = useRef<WebSocket | null>(null);

    // Retrieve the token from cookies
    const token = Cookies.get('jwt_token');  // Get the token from the cookie
    const wsUrl = `ws://localhost:8000/ws?token=${token}`;

    // WebSocket connection setup
    const connectWebSocket = () => {
        socketRef.current = new WebSocket(wsUrl);

        socketRef.current.onmessage = (event) => {
            const audioBlob = new Blob([event.data], { type: 'audio/wav' });
            const url = URL.createObjectURL(audioBlob);
            setAudioUrl(url);
        };

        socketRef.current.onclose = () => {
            alert("WebSocket connection closed. Please log in again.");
        };
    };

    // Start recording
    const startRecording = async () => {
        if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
            connectWebSocket();  // Reconnect WebSocket if not connected
        }

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorderRef.current = new MediaRecorder(stream);
        audioChunks.current = [];
        
        mediaRecorderRef.current.ondataavailable = (event) => {
            audioChunks.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
            socketRef.current?.send(audioBlob);  // Send the audio to backend
            audioChunks.current = [];
        };

        mediaRecorderRef.current.start();
        setIsRecording(true);
    };

    // Stop recording
    const stopRecording = () => {
        mediaRecorderRef.current?.stop();
        setIsRecording(false);
    };

    return (
        <div className="audio-test">
            <h1>WebSocket Audio Test</h1>
            <button onClick={startRecording} disabled={isRecording}>Start Recording</button>
            <button onClick={stopRecording} disabled={!isRecording}>Stop Recording</button>
            {audioUrl && <audio controls src={audioUrl} />}
        </div>
    );
};

export default WebSocketAudio;
