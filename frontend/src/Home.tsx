// src/Home.tsx
import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import './Common.css';
import './Home.css'; // Updated CSS file for landing page styles

const Home: React.FC = () => {
    const { isAuthenticated } = useAuth();
    const location = useLocation();
    const [showPopup, setShowPopup] = useState(false);

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        if (params.get('apply_for_beta') === 'true') {
            setShowPopup(true);
        }
    }, [location]);

    return (
        <div className="landing-container">
            {showPopup && (
                <div className="popup">
                    <p>🚧 We're in <strong>Beta</strong> now! Want in? Sign up for early access! 🚀</p>
                    <button className="button" onClick={() => window.open('https://forms.gle/J9TtD6fDiaiFk6Dq6', '_blank')}>
                        Sign Up for Beta
                    </button>
                    <button className="button" onClick={() => setShowPopup(false)}>Close</button>
                </div>
            )}
            <section className="hero-section">
                <h1>Become fluent in English with aitalki</h1>
                <p>Stop paying for italki, chat with your personalized AI language tutor at a fraction of the cost.</p>
                {isAuthenticated ? (
                    <button className="button" onClick={() => window.location.href = '/lesson'}>
                        Start Lesson
                    </button>
                ) : (
                    <button className="button" onClick={() => window.open('https://forms.gle/J9TtD6fDiaiFk6Dq6', '_blank')}>
                        Apply for Beta
                    </button>
                )}
            </section>

            <section className="features-section">
                <h2>Features</h2>
                <ul>
                    <li>👩‍🏫 Lessons Just for You: Tailored to your style and goals!</li>
                    <li>🌍 Accent of Your Dreams: Pick your vibe – 🇺🇸 American or 🇬🇧 British!</li>
                    <li>⚡️ Real-Time Fixes: Instant pronunciation & grammar coaching.</li>
                    <li>📈 Your Progress, Tracked: Watch yourself level up!</li>
                </ul>
            </section>

            <section className="pricing-section">
                <h2>Pricing</h2>
                <p>Pay as you go at a fraction of italki lessons cost.</p>
            </section>

            <section className="cta-section">
                <h2>Join Beta!</h2>
                <p>Sign up for beta and be the first to experience aitalki.</p>
                <button className="button" onClick={() => window.open('https://forms.gle/J9TtD6fDiaiFk6Dq6', '_blank')}>
                    Sign Up for Beta Now
                </button>
            </section>
        </div>
    );
};

export default Home;
