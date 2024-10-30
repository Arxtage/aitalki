import React, { useState, useRef, useEffect } from 'react';
import Cookies from 'js-cookie';

const WebSocketAudio: React.FC = () => {
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const audioChunks = useRef<Blob[]>([]);
    const socketRef = useRef<WebSocket | null>(null);
    const userRecordingRef = useRef<MediaStream | null>(null);
    const [token, setToken] = useState<string | undefined>(undefined);
    console.log("=== Entered WebSocketAudio");

    useEffect(() => {
        const retrievedToken = Cookies.get('jwt_token');
        setToken(retrievedToken);
        console.log("====== Retrieved token:", retrievedToken);
    }, []);

    useEffect(() => {
        if (token) {
            connectWebSocket();
        }
    }, [token]);  // Run only when token is set

    const connectWebSocket = () => {
        if (token) {
            console.log("=== Token exists:", token)
            const wsUrl = `ws://localhost:8000/ws?token=${token}`;  // Create wsUrl with token after it's set
            socketRef.current = new WebSocket(wsUrl);
    
            socketRef.current.onmessage = (event) => {
                const audioBlob = new Blob([event.data], { type: 'audio/wav' });
                const url = URL.createObjectURL(audioBlob);
                const audio = new Audio(url);
                audio.play().catch(error => {
                    console.error("Error playing audio:", error);
                });
            };
    
            socketRef.current.onclose = () => {
                alert("WebSocket connection closed. Please log in again.");
            };
        }
    };

    // Start recording
    const startRecording = async () => {
        console.log("=== Start Recording")
        if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
            connectWebSocket();  // Reconnect WebSocket if not connected
        }

        // Get the media stream
        const userRecording = await navigator.mediaDevices.getUserMedia({ audio: true });
        userRecordingRef.current = userRecording; // Store the media stream
        mediaRecorderRef.current = new MediaRecorder(userRecording);
        audioChunks.current = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
            audioChunks.current.push(event.data);
        };

        mediaRecorderRef.current.onstop = () => {
            const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
            socketRef.current?.send(audioBlob);  // Send the audio to backend
            console.log("=== Sending audio over socket")
            audioChunks.current = [];
        };

        mediaRecorderRef.current.start();
        setIsRecording(true);
    };

    // Stop recording
    const stopRecording = () => {
        console.log("=== Stop Recording")
        mediaRecorderRef.current?.stop();
        setIsRecording(false);
        
        // Stop the media stream to deactivate the microphone
        if (userRecordingRef.current) {
            userRecordingRef.current.getTracks().forEach(track => track.stop());
            userRecordingRef.current = null; // Clear the reference
        }
    };

    return (
        <div className="audio-test">
            <h1>WebSocket Audio Test</h1>
            <button onClick={startRecording} disabled={isRecording}>Start Recording</button>
            <button onClick={stopRecording} disabled={!isRecording}>Stop Recording</button>
        </div>
    );
};

export default WebSocketAudio;
