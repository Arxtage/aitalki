// src/Navbar.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar: React.FC = () => {
    return (
        <nav className="Navbar">
            <Link to="/" className="Navbar-brand">
                <img src={`${process.env.PUBLIC_URL}/logo_aitalki.png`} alt="Logo" className="Navbar-logo" />
                <h1 className="Navbar-title">aitalki</h1>
            </Link>
        </nav>
    );
};

export default Navbar;

