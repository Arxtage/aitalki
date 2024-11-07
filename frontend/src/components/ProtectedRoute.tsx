import React from 'react';
import { Navigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { jwtDecode } from 'jwt-decode';
import {DecodedToken} from '../hooks/useAuth'

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const jwt_token = Cookies.get('jwt_token');

    if (!jwt_token) {
        // Redirect to login if there's no token
        return <Navigate to="/login" replace />;
    }

    // Optionally, you can decode the token and check its expiration
    const decodedToken = jwtDecode<DecodedToken>(jwt_token);
    console.log("== TOKEN Expirtion Date", decodedToken.exp)
    console.log("== DATE NOW", Date.now())
    if (decodedToken.exp * 1000 < Date.now()) {
        // Token is expired
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
