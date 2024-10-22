// src/Lesson.tsx
import React from 'react';
import WebSocketAudio from './WebSocketAudio';

const Lesson: React.FC = () => {
    return (
        <div>
            <h1>Lesson Page</h1>
            <WebSocketAudio />
        </div>
    );
};

export default Lesson;

