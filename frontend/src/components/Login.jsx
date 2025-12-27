import React, { useState } from 'react';
import { useToast } from './Toast';

const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

function Login() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState('IDLE'); // IDLE, VERIFYING, SENT
    const { addToast } = useToast();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email }),
            });

            const data = await response.json();

            if (response.ok) {
                if (data.status === 'verification_required') {
                    setStatus('VERIFYING');
                    addToast('Verification required. Check your email.', 'info');
                } else {
                    setStatus('SENT');
                    addToast('Magic link sent! Check your email.', 'success');
                }
            } else {
                addToast(data.detail || 'Failed to send magic link.', 'error');
            }
        } catch (error) {
            console.error('Login error:', error);
            addToast('Network error. Please try again.', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleRetry = () => {
        setStatus('IDLE');
        setEmail('');
    };

    const handleVerified = () => {
        // User claims they verified, try login again
        handleSubmit({ preventDefault: () => { } });
    };

    if (status === 'VERIFYING') {
        return (
            <div className="login-container" style={{ maxWidth: '500px', margin: '4rem auto', padding: '2rem', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '1rem' }}>✉️ Verification Required (Step 1 of 2)</h2>
                <p>It looks like this is your first time logging in! To keep our data secure, we need you to verify your email address with our system.</p>

                <ol style={{ textAlign: 'left', margin: '1.5rem 0', paddingLeft: '1.5rem' }}>
                    <li style={{ marginBottom: '0.5rem' }}>Check your inbox for an email from <strong>Amazon Web Services</strong> (no-reply-aws@amazon.com).</li>
                    <li style={{ marginBottom: '0.5rem' }}>Click the link inside that email that says <strong>"Verify Email Address"</strong>.</li>
                    <li>Once done, return to this page and click "I've Verified My Email" below.</li>
                </ol>

                <p style={{ fontSize: '0.9rem', color: '#666' }}>Check your Junk/Spam folder if you don't see it within 1 minute.</p>

                <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem', flexDirection: 'column' }}>
                    <button
                        className="btn btn-primary"
                        onClick={handleVerified}
                        disabled={loading}
                        style={{ width: '100%', padding: '0.75rem' }}
                    >
                        {loading ? 'Checking...' : "I've Verified My Email"}
                    </button>
                    <button
                        className="btn btn-secondary"
                        onClick={handleRetry}
                        style={{ width: '100%', padding: '0.75rem' }}
                    >
                        Back to Login
                    </button>
                </div>
            </div>
        );
    }

    if (status === 'SENT') {
        return (
            <div className="login-container" style={{ maxWidth: '400px', margin: '4rem auto', textAlign: 'center' }}>
                <h2>🚀 Magic Link Sent! (Step 2 of 2)</h2>
                <p>Your identity is confirmed. We have sent a private login link to your email.</p>
                <div style={{ margin: '2rem 0', padding: '1rem', background: '#f8f9fa', borderRadius: '4px', textAlign: 'left', color: '#333' }}>
                    <p style={{ margin: '0.5rem 0' }}><strong>From:</strong> Prompt Repo Bot</p>
                    <p style={{ margin: '0.5rem 0' }}><strong>Expires in:</strong> 15 minutes</p>
                </div>
                <p>Close this window and click the link in your email to enter the repository.</p>
                <button className="btn btn-secondary" onClick={handleRetry} style={{ marginTop: '1rem' }}>
                    Try another email
                </button>
            </div>
        );
    }

    return (
        <div className="login-container" style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem', border: '1px solid #eee', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
            <h2 style={{ marginBottom: '0.5rem', textAlign: 'center' }}>Sign in to Prompt Repository</h2>
            <p style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#666' }}>Enter your @pega.com email to receive a login link.</p>

            <form onSubmit={handleSubmit}>
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                    <label htmlFor="email" style={{ display: 'block', marginBottom: '0.5rem' }}>Work Email</label>
                    <input
                        type="email"
                        id="email"
                        className="form-control"
                        placeholder="you@pega.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        style={{ width: '100%', padding: '0.75rem', borderRadius: '4px', border: '1px solid #ccc' }}
                    />
                </div>
                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                    style={{ width: '100%', padding: '0.75rem', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', cursor: loading ? 'not-allowed' : 'pointer' }}
                >
                    {loading ? 'Sending...' : 'Send Magic Link'}
                </button>
            </form>
            <p style={{ marginTop: '1.5rem', fontSize: '0.8rem', color: '#888', textAlign: 'center' }}>
                First-time users will need to complete a one-time identity verification with our email provider (AWS) before receiving the login link.
            </p>
        </div>
    );
}

export default Login;
