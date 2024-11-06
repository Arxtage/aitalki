import React from 'react';
import './SpeechBubble.css'; // Import the CSS for the bubble

const Bubble: React.FC<{ isActive: boolean }> = ({ isActive }) => {
    return (
        <div className={`bubble ${isActive ? 'active' : ''}`}></div>
    );
};

export default Bubble;
