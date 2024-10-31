// src/Home.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Common.css';

const Home: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="container">
            <h1>aitalki</h1>
            <p>Welcome to the Home Page!</p>
            <div className="button-container">
                <button 
                    className="button"
                    onClick={() => navigate('/lesson')}
                >
                    Start Lesson
                </button>
                <button 
                    className="button"
                    onClick={() => navigate('/login')}
                >
                    Login
                </button>
            </div>
        </div>
    );
};

export default Home;
