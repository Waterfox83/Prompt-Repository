import React from 'react';

const AboutModal = ({ onClose }) => {
    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '800px' }}>
                <button className="modal-close" onClick={onClose}>&times;</button>

                <h2 style={{ color: '#60a5fa', borderBottom: '1px solid #334155', paddingBottom: '1rem' }}>About Prompt Repository</h2>

                <div style={{ color: '#e2e8f0', lineHeight: '1.6' }}>
                    <section className="mb-4">
                        <h3 style={{ color: '#38bdf8', fontSize: '1.2rem', marginBottom: '0.5rem' }}>🚀 Use Case</h3>
                        <p>
                            The <strong>AI Prompt Repository</strong> is a centralized knowledge base for Pega engineers to share, discover, and reuse high-quality AI prompts.
                            Instead of reinventing the wheel, you can find prompts that have already proven effective for tasks like coding, debugging, SQL generation, and documentation.
                        </p>
                    </section>

                    <section className="mb-4">
                        <h3 style={{ color: '#38bdf8', fontSize: '1.2rem', marginBottom: '0.5rem' }}>📖 How to Use</h3>
                        <ul style={{ paddingLeft: '1.5rem', margin: 0 }}>
                            <li><strong>Browse:</strong> View all shared prompts sorted by recency.</li>
                            <li><strong>Search:</strong> Use natural language to find prompts (e.g., "help me write a python script"). The semantic search understands intent, not just keywords.</li>
                            <li><strong>Filter:</strong> Click on tags, tools, or usernames to narrow down the list. Use "My Prompts" to see your contributions.</li>
                            <li><strong>Contribute:</strong> Click "Add New" to share your own prompts. The system will automatically generate tags and a description for you!</li>
                        </ul>
                    </section>

                    <section className="mb-4">
                        <h3 style={{ color: '#38bdf8', fontSize: '1.2rem', marginBottom: '0.5rem' }}>🛠️ Tech Stack</h3>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                            <div>
                                <strong>Frontend:</strong>
                                <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem', color: '#94a3b8' }}>
                                    <li>React + Vite</li>
                                    <li>Node.js (Build Env)</li>
                                    <li>Glassmorphism UI</li>
                                </ul>
                            </div>
                            <div>
                                <strong>Backend:</strong>
                                <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem', color: '#94a3b8' }}>
                                    <li>Python (FastAPI)</li>
                                    <li>AWS Lambda (Serverless)</li>
                                </ul>
                            </div>
                            <div>
                                <strong>Data & Search:</strong>
                                <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem', color: '#94a3b8' }}>
                                    <li>AWS S3 (Data Storage in JSON format)</li>
                                    <li>NumPy (Vector Search)</li>
                                    <li>Gemini API (Embeddings)</li>
                                </ul>
                            </div>
                            <div>
                                <strong>Infrastructure:</strong>
                                <ul style={{ marginTop: '0.25rem', paddingLeft: '1.5rem', color: '#94a3b8' }}>
                                    <li>AWS Lambda Function (Backend)</li>
                                    <li>AWS S3 (Frontend)</li>
                                    <li>AWS CloudFront (CDN)</li>
                                    <li>AWS SES (Email)</li>
                                </ul>
                            </div>
                        </div>
                    </section>

                    <section>
                        <h3 style={{ color: '#38bdf8', fontSize: '1.2rem', marginBottom: '0.5rem' }}>🔒 Security Implementation</h3>
                        <p>
                            Security is a core priority. The application implements a passwordless <strong>Magic Link</strong> authentication flow:
                        </p>
                        <ul style={{ paddingLeft: '1.5rem', margin: '0.5rem 0' }}>
                            <li><strong>Domain Restriction:</strong> Only users with <code>@pega.com</code> or <code>@in.pega.com</code> emails can log in.</li>
                            <li><strong>Secure Tokens:</strong> Authentication uses signed JWTs (JSON Web Tokens) with short expiration times for login links.</li>
                            <li><strong>Session Security:</strong> Sessions are managed via <code>HttpOnly</code> and <code>Secure</code> cookies, preventing XSS attacks and ensuring data is only transmitted over HTTPS.</li>
                            <li><strong>Least Privilege:</strong> The backend operates with strictly scoped AWS IAM roles, accessing only the necessary S3 buckets and SES identities.</li>
                        </ul>
                    </section>
                </div>

                <div className="mt-4" style={{ textAlign: 'right', borderTop: '1px solid #334155', paddingTop: '1rem' }}>
                    <button className="btn btn-primary" onClick={onClose}>Close</button>
                </div>
            </div>
        </div>
    );
};

export default AboutModal;
