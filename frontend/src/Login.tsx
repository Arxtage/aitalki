import React from 'react';

const isProd = process.env.REACT_APP_STAGE === 'prod';
const API_URL = isProd
  ? 'https://aitalki.app'
  : 'http://localhost:8000';

console.log('API URL:', API_URL);

const Login: React.FC = () => {
    const handleLogin = () => {
        window.location.href = `${API_URL}/login`;
    };

    return (
        <div>
            <h1>Login Page</h1>
            <button onClick={handleLogin}>Google Login</button>
        </div>
    );
};

export default Login;
