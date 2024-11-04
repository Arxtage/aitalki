// src/Home.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import './Common.css';

const Home: React.FC = () => {
    const navigate = useNavigate();

    const handleStartLesson = () => {
        const jwt_token = Cookies.get('jwt_token');
        if (!jwt_token) {
            navigate('/login');
        } else {
            navigate('/lesson');
        }
    };

    return (
        <div className="container">
            <h1>Become fluent in English with aitalki</h1>
            <div className="button-container">
                <button 
                    className="button"
                    onClick={handleStartLesson}
                >
                    Start Lesson
                </button>
            </div>
        </div>
    );
};

export default Home;
