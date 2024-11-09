// src/Navbar.tsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import './Navbar.css';

const Navbar: React.FC = () => {
    const navigate = useNavigate();
    const { userName, isAuthenticated, logout } = useAuth();

    return (
        <nav className="Navbar">
            <Link to="/" className="Navbar-brand">
                <img src={`${process.env.PUBLIC_URL}/aitalki.png`} alt="Logo" className="Navbar-logo" />
            </Link>
            <div className="Navbar-auth">
                {isAuthenticated ? (
                    <>
                        <span className="Navbar-username">{userName}</span>
                        <button className="button" onClick={logout}>
                            Log Out
                        </button>
                    </>
                ) : (
                    <button className="button" onClick={() => navigate('/login')}>
                        Log In
                    </button>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
