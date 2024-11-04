import React from 'react';
import './Common.css';

const isProd = process.env.REACT_APP_STAGE === 'prod';
const API_URL = isProd
  ? 'https://aitalki.app'
  : 'http://localhost:8000';

const Login: React.FC = () => {
    const handleLogin = () => {
        window.location.href = `${API_URL}/api/login`;
    };

    return (
        <div className="container">
            <h1>Login</h1>
            <button 
                className="button"
                onClick={handleLogin}
            >
                Google Login
            </button>
        </div>
    );
};

export default Login;
