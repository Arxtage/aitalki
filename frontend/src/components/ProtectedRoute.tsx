import React from 'react';
import { Navigate } from 'react-router-dom';
import Cookies from 'js-cookie';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
    const jwt_token = Cookies.get('jwt_token');

    if (!jwt_token) {
        // Redirect to login if there's no token
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
