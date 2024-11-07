import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Home from './Home';
import Lesson from './Lesson';
import Login from './Login';
import Navbar from './Navbar';
import Footer from './Footer';
import ProtectedRoute from './components/ProtectedRoute';
import './App.css';

const App: React.FC = () => {
    return (
        <Router>
            <div className="App">
                <Navbar />
                <div className="content">
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route 
                            path="/lesson" 
                            element={
                                <ProtectedRoute>
                                    <Lesson />
                                </ProtectedRoute>
                            } 
                        />
                        <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                </div>
                <Footer />
            </div>
        </Router>
    );
};

export default App;
