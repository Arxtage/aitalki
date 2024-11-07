import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import { jwtDecode } from "jwt-decode";

const isProd = process.env.REACT_APP_STAGE === 'prod';
const API_URL = isProd ? 'https://aitalki.app' : 'http://localhost:8000';

export interface DecodedToken {
    name: string;
    sub: string;
    exp: number;
}

export const useAuth = () => {
    const [userName, setUserName] = useState<string | null>(null);

    useEffect(() => {
        const token = Cookies.get('jwt_token');
        if (token) {
            try {
                const decoded = jwtDecode(token) as DecodedToken;
                setUserName(decoded.name);
            } catch (error) {
                console.error('Error decoding token:', error);
            }
        }
    }, []);

    const logout = () => {
        Cookies.remove('jwt_token'); // Remove the token from cookies
        setUserName(null); // Clear the user name from state
        window.location.href = '/login'; // Redirect to login page
    };

    return { userName, isAuthenticated: !!userName, logout };
};
