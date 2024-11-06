import React, { useState, useRef, useEffect } from 'react';
import Cookies from 'js-cookie';
import { useMicVAD } from '@ricky0123/vad-react';
import Bubble from './components/SpeechBubble'; // Import the Bubble component
import './Common.css';

const isProd = process.env.REACT_APP_STAGE === 'prod';
const API_URL = isProd ? 'aitalki.app' : 'localhost:8000';
const SILENCE_DURATION = 5000; // 5 seconds of silence before sending audio

const WebSocketAudio: React.FC = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [statusText, setStatusText] = useState('Start Recording');
    const [isBubbleActive, setIsBubbleActive] = useState(false); // State for bubble
    const audioChunks = useRef<Blob[]>([]);
    const socketRef = useRef<WebSocket | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const [token, setToken] = useState<string | undefined>(undefined);
    const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        const retrievedToken = Cookies.get('jwt_token');
        setToken(retrievedToken);
    }, []);

    useEffect(() => {
        if (token) {
            connectWebSocket();
        }
    }, [token]);

    const connectWebSocket = () => {
        if (token) {
            const wsProtocol = isProd ? 'wss' : 'ws';
            const wsUrl = `${wsProtocol}://${API_URL}/api/ws?token=${token}`;
            socketRef.current = new WebSocket(wsUrl);
    
            socketRef.current.onmessage = (event) => {
                const audioBlob = new Blob([event.data], { type: 'audio/wav' });
                const url = URL.createObjectURL(audioBlob);
                const audio = new Audio(url);
                audio.play().catch(console.error);
                console.log('Playing audio from teacher');
                setStatusText('Speaking'); // Update status to Speaking when audio is playing
                setIsBubbleActive(true); // Activate bubble when teacher speaks

                audio.onended = () => {
                    setIsBubbleActive(false); // Deactivate bubble when audio ends
                };
            };
    
            socketRef.current.onclose = () => {
                alert("WebSocket connection closed. Please log in again.");
            };
        }
    };

    const vad = useMicVAD({
        ortConfig(ort) {
            ort.env.wasm.wasmPaths = "/";
        },
        workletURL: '/vad.worklet.bundle.min.js',
        modelURL: '/silero_vad.onnx',
        onSpeechStart: () => {
            console.log('Speech started');
            setStatusText('Listening'); // Update status to Listening
            setIsBubbleActive(true); // Activate bubble when user speaks
            if (!mediaRecorderRef.current && isRecording) {
                startNewRecording();
            }
            if (silenceTimeoutRef.current) {
                clearTimeout(silenceTimeoutRef.current); // Clear silence timeout
            }
        },
        onSpeechEnd: () => {
            console.log('Speech ended');
            setIsBubbleActive(false); // Deactivate bubble when user stops speaking
            if (mediaRecorderRef.current) {
                mediaRecorderRef.current.stop();
                mediaRecorderRef.current = null;
            }
            // Start silence timeout after speech ends
            silenceTimeoutRef.current = setTimeout(() => {
                sendAudioToBackend();
            }, SILENCE_DURATION);
            console.log("Silence Timeout Started");
        },
        onVADMisfire: () => {
            console.log('VAD misfire');
        },
    });

    const startNewRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunks.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.current.push(event.data);
            };

            mediaRecorder.onstop = () => {
                // Clean up the stream
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
        } catch (error) {
            console.error('Error starting recording:', error);
        }
    };

    const sendAudioToBackend = () => {
        if (audioChunks.current.length > 0) {
            const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
            socketRef.current?.send(audioBlob);
            audioChunks.current = [];
        }
        setStatusText('Start Recording'); // Reset status text
        setIsRecording(false); // Stop recording
    };

    const toggleRecording = () => {
        if (!isRecording) {
            console.log('Toggle it is: !isRecording, Started Vad');
            setIsRecording(true);
            setStatusText('Listening'); // Update status to Listening
            vad.start();
        } else {
            console.log('Toggle it isRecording, Paused Vad');
            setIsRecording(false);
            vad.pause();
            if (mediaRecorderRef.current) {
                mediaRecorderRef.current.stop();
                mediaRecorderRef.current = null;
            }
        }
    };

    return (
        <div className="container">
            <h1>Lesson</h1>
            <p>{statusText}</p> {/* Display status text */}
            <div className="bubble-container"> {/* New container for the bubble */}
                <Bubble isActive={isBubbleActive} /> {/* Render the bubble */}
            </div>
            <div className="button-container">
                <button 
                    className={`button ${isRecording ? 'recording' : ''}`}
                    onClick={toggleRecording}
                >
                    {isRecording ? 'Stop Recording' : 'Start Recording'}
                </button>
            </div>
            {vad.loading && <p>Loading voice detection...</p>}
        </div>
    );
};

export default WebSocketAudio;
