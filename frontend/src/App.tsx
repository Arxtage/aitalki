import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './Home';
import Lesson from './Lesson';
import Login from './Login'; // Import the Login component
import Navbar from './Navbar'; // Import the Navbar
import './App.css';

const App: React.FC = () => {
    return (
        <Router>
            <div className="App">
                <Navbar /> {/* Add the Navbar component */}
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/lesson" element={<Lesson />} />
                    <Route path="/login" element={<Login />} /> {/* Add route for Login Page */}
                </Routes>
            </div>
        </Router>
    );
};

export default App;
