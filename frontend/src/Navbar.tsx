// src/Navbar.tsx
import React from 'react';
import './Navbar.css'; // Import the CSS for styling

const Navbar: React.FC = () => {
    return (
        <nav className="Navbar">
            <img src={`${process.env.PUBLIC_URL}/logo_aitalki.png`} alt="Logo" className="Navbar-logo" />
            <h1 className="Navbar-title">aitalki</h1>
        </nav>
    );
};

export default Navbar;

