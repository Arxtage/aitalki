import React from 'react';

const Login: React.FC = () => {
    const handleLogin = () => {
        window.location.href = 'http://localhost:8000/login';
    };

    return (
        <div>
            <h1>Login Page</h1>
            <button onClick={handleLogin}>Google Login</button>
        </div>
    );
};

export default Login;
