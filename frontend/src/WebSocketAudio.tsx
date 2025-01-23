import React, { useState, useRef, useEffect } from 'react';
import Cookies from 'js-cookie';
import { useMicVAD } from '@ricky0123/vad-react';
import Bubble from './components/SpeechBubble'; // Import the Bubble component
import './Common.css';

const isProd = process.env.REACT_APP_STAGE === 'prod';
const API_URL = isProd ? 'aitalki.app' : 'localhost:8000';
const SILENCE_DURATION = 1000; // ms of silence before sending audio

const WebSocketAudio: React.FC = () => {
    // Keep state for UI updates (useState is ASYNC so not instant updates)
    const [lessonActive, setLessonActive] = useState(false);
    const [statusText, setStatusText] = useState<string | null>(null);
    const [isBubbleActive, setIsBubbleActive] = useState(false);
    
    // Refs for internal logic (Ref is for instant updates, but can not be used for UI updates)
    const lessonActiveRef = useRef(false);
    const audioChunks = useRef<Blob[]>([]);
    const socketRef = useRef<WebSocket | null>(null);
    const currentPlayingAudioRef = useRef<HTMLAudioElement | null>(null);
    const mediaRecorderRef = useRef<MediaRecorder | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const [token, setToken] = useState<string | undefined>(undefined);

    useEffect(() => {
        const retrievedToken = Cookies.get('jwt_token');
        setToken(retrievedToken);
    }, []);

    const connectWebSocket = () => {
        if (token) {
            const wsProtocol = isProd ? 'wss' : 'ws';
            const wsUrl = `${wsProtocol}://${API_URL}/api/ws?token=${token}`;
            socketRef.current = new WebSocket(wsUrl);
    
            socketRef.current.onmessage = (event) => {
                if (!lessonActiveRef.current) {
                    console.log('Ignoring teacher audio - lesson not active');
                    return;
                }

                // Stop any currently playing audio
                if (currentPlayingAudioRef.current) {
                    currentPlayingAudioRef.current.pause();
                    URL.revokeObjectURL(currentPlayingAudioRef.current.src);
                    currentPlayingAudioRef.current = null;
                    setIsBubbleActive(false);
                    setStatusText(null);
                }

                const audioBlob = new Blob([event.data], { type: 'audio/wav' });
                const url = URL.createObjectURL(audioBlob);
                const audio = new Audio(url);
                currentPlayingAudioRef.current = audio;
                
                audio.play().catch(console.error);
                console.log('Playing audio from teacher');
                setStatusText('Speaking');
                setIsBubbleActive(true);

                audio.onended = () => {
                    URL.revokeObjectURL(url);
                    currentPlayingAudioRef.current = null;
                    setIsBubbleActive(false);
                    setStatusText(null);
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
        startOnLoad: false,
        onSpeechStart: () => {
            console.log('Speech started');
            if (silenceTimeoutRef.current) {
                clearTimeout(silenceTimeoutRef.current); // Clear silence timeout
            }
            setStatusText('Listening'); // Update status to Listening
            setIsBubbleActive(true); // Activate bubble when user speaks
            if (!mediaRecorderRef.current && lessonActive) {
                startNewRecording();
            }
        },
        onSpeechEnd: () => {
            console.log('Speech ended');
            setIsBubbleActive(false); // Deactivate bubble when user stops speaking
            setStatusText(null)
            if (mediaRecorderRef.current) {
                mediaRecorderRef.current.stop();
                mediaRecorderRef.current = null;
            }
            // Start silence timeout after speech ends
            silenceTimeoutRef.current = setTimeout(() => {
                console.log("SENDING TO BACKEND")
                sendAudioToBackend();
            }, SILENCE_DURATION);
            console.log("Silence Timeout Started");
        },
        onVADMisfire: () => {
            console.log('VAD misfire');
            setIsBubbleActive(false); // Deactivate bubble when user stops speaking
            setStatusText(null);
        },
    });

    const startNewRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaStreamRef.current = stream; // Store the media stream reference
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunks.current = [];

            mediaRecorder.ondataavailable = (event) => {
                audioChunks.current.push(event.data);
            };

            mediaRecorder.onstop = () => {
                // Clean up the stream
                stream.getTracks().forEach(track => track.stop());
            }

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
    };

    const startOrEndLesson = () => {
        if (!lessonActive) {
            console.log('Start Lesson, Started Vad');
            setLessonActive(true);  // For UI updates
            lessonActiveRef.current = true;  // For internal logic
            setStatusText('Listening'); // Update status to Listening
            connectWebSocket(); // Connect WebSocket only when starting the lesson
            vad.start(); // Start VAD
        } else {
            console.log('End Lesson, Paused Vad');
            setLessonActive(false);  // For async UI updates
            lessonActiveRef.current = false;  // For instant internal logic
            vad.pause();
            if (mediaRecorderRef.current) {
                mediaRecorderRef.current.stop();
                mediaRecorderRef.current = null;
            }
            // Stop the media stream to turn off the microphone
            if (mediaStreamRef.current) {
                mediaStreamRef.current.getTracks().forEach(track => track.stop());
                mediaStreamRef.current = null; // Clear the reference
            }
            setIsBubbleActive(false); // Deactivate bubble when leaving lesson
            setStatusText(null);
            
            // Stop any playing audio
            if (currentPlayingAudioRef.current) {
                currentPlayingAudioRef.current.pause();
                URL.revokeObjectURL(currentPlayingAudioRef.current.src);
                currentPlayingAudioRef.current = null;
            }
        }
    };

    return (
        <div className="lesson-container">
            <p>{statusText}</p> {/* Display status text */}
            <div className="bubble-container"> {/* New container for the bubble */}
                <Bubble isActive={isBubbleActive} /> {/* Render the bubble */}
            </div>
            <div className="button-container">
                <button 
                    className={`button ${lessonActive ? 'recording' : ''}`}
                    onClick={startOrEndLesson}
                >
                    {lessonActive ? 'Leave Lesson' : 'Start Lesson'}
                </button>
            </div>
        </div>
    );
};

export default WebSocketAudio;
