import React, { useState } from 'react';

const PromptList = ({ onSearch, results }) => {
    const [query, setQuery] = useState('');

    const handleSearch = (e) => {
        e.preventDefault();
        onSearch(query);
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        alert('Prompt copied to clipboard!');
    };

    return (
        <div>
            <div className="card mb-4">
                <h2>Search Repository</h2>
                <form onSubmit={handleSearch} className="flex gap-2">
                    <input
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search by meaning (e.g., 'help me debug python code')..."
                        style={{ flex: 1 }}
                    />
                    <button type="submit" className="btn btn-primary">Search</button>
                </form>
            </div>

            <div className="grid">
                {results.map((item) => (
                    <div key={item.id} className="card">
                        <div className="flex justify-between items-center mb-4">
                            <h3 style={{ margin: 0, color: '#60a5fa' }}>{item.title}</h3>
                            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{item.tool_used}</span>
                        </div>
                        <p style={{ color: '#cbd5e1', marginBottom: '1rem' }}>{item.description}</p>

                        <div className="mb-4">
                            {item.tags && item.tags.map((tag, idx) => (
                                <span key={idx} className="tag">#{tag}</span>
                            ))}
                        </div>

                        <button
                            className="btn btn-secondary"
                            onClick={() => copyToClipboard(item.prompt_text || "Prompt text not available in search result (mock)")}
                            style={{ width: '100%' }}
                        >
                            Copy Prompt
                        </button>
                    </div>
                ))}

                {results.length === 0 && (
                    <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem' }}>
                        No results found. Try searching or add a new prompt!
                    </div>
                )}
            </div>
        </div>
    );
};

export default PromptList;
