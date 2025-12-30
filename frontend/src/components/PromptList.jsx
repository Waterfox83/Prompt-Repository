import React, { useState } from 'react';
import { useToast } from './Toast';

const PromptList = ({ onSearch, results, loading, onFilter, activeFilter, onClearFilter, onEdit, user }) => {
    const [query, setQuery] = useState('');
    const [selectedPrompt, setSelectedPrompt] = useState(null);
    const { addToast } = useToast();

    // Check if prompt was created by current user
    const canEdit = (prompt) => {
        if (!user || !prompt) return false;
        // Check if owner_email matches
        if (prompt.owner_email && prompt.owner_email === user.email) return true;

        // Fallback for session-created prompts (optional, but good for UX if backend sync is slow)
        // But for security, we should rely on backend data. 
        // Let's stick to owner_email check as primary.
        return false;
    };

    const handleSearch = (e) => {
        e.preventDefault();
        console.log("Search button clicked, query:", query); // Debug log
        onSearch(query);
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        addToast('Prompt copied to clipboard!', 'success');
    };

    return (
        <div>
            <div className="card mb-4">
                <h2 style={{ marginTop: 0 }}>Search Repository</h2>
                <form onSubmit={handleSearch} className="flex gap-2">
                    <input
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Search by meaning (e.g., 'help me debug python code')..."
                        style={{ flex: 1 }}
                    />
                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ minWidth: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                    >
                        {loading ? (
                            <>
                                <span className="spinner" style={{
                                    width: '16px',
                                    height: '16px',
                                    border: '2px solid rgba(255,255,255,0.3)',
                                    borderTop: '2px solid white',
                                    borderRadius: '50%',
                                    marginRight: '8px',
                                    animation: 'spin 1s linear infinite'
                                }}></span>
                                Searching...
                            </>
                        ) : 'Search'}
                    </button>
                    <style>{`
                        @keyframes spin {
                            0% { transform: rotate(0deg); }
                            100% { transform: rotate(360deg); }
                        }
                    `}</style>
                </form>
            </div>

            {activeFilter && (
                <div style={{
                    marginBottom: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    background: 'rgba(56, 189, 248, 0.1)',
                    padding: '0.5rem 1rem',
                    borderRadius: '0.5rem',
                    border: '1px solid rgba(56, 189, 248, 0.2)',
                    color: '#e2e8f0'
                }}>
                    {activeFilter.type === 'my-prompts' ? (
                        <span><span style={{ color: '#38bdf8', fontWeight: 'bold' }}>My prompts</span></span>
                    ) : (
                        <span>Filtered by <strong>{activeFilter.type}</strong>: <span style={{ color: '#38bdf8', fontWeight: 'bold' }}>{activeFilter.value}</span></span>
                    )}
                    <button
                        onClick={onClearFilter}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#94a3b8',
                            cursor: 'pointer',
                            fontSize: '1.2rem',
                            padding: '0 0.5rem',
                            marginLeft: 'auto'
                        }}
                        title="Clear filter"
                    >
                        &times;
                    </button>
                </div>
            )}

            <div className="grid">
                {results.map((item) => (
                    <div key={item.id} className="card prompt-card">
                        <div className="mb-2">
                            <h3 style={{ margin: '0 0 0.5rem 0', color: '#60a5fa' }}>{item.title}</h3>

                            {/* Tools */}
                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.5rem' }}>
                                {(Array.isArray(item.tool_used) ? item.tool_used : [item.tool_used]).map((tool, idx) => (
                                    <span
                                        key={idx}
                                        className="tool-badge"
                                        style={{
                                            fontSize: '0.85rem',
                                            fontWeight: '600',
                                            color: '#38bdf8',
                                            cursor: 'pointer',
                                            display: 'inline-block',
                                            padding: '0.1rem 0.4rem',
                                            background: 'rgba(56, 189, 248, 0.1)',
                                            borderRadius: '0.25rem',
                                            border: '1px solid rgba(56, 189, 248, 0.2)'
                                        }}
                                        onClick={() => onFilter && onFilter('tool', tool)}
                                        title={`Filter by ${tool}`}
                                    >
                                        {tool}
                                    </span>
                                ))}
                            </div>

                            {/* Username */}
                            {item.username && (
                                <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.5rem' }}>
                                    by <span
                                        style={{ color: '#e2e8f0', fontWeight: '500', cursor: 'pointer', textDecoration: 'underline' }}
                                        onClick={() => onFilter && onFilter('username', item.username)}
                                        title={`Filter by user ${item.username}`}
                                    >
                                        {item.username}
                                    </span>
                                </div>
                            )}
                        </div>

                        <div className="card-description">
                            <p style={{ margin: 0 }}>{item.description}</p>
                        </div>

                        <div className="mb-4" style={{ marginTop: 'auto' }}>
                            {item.tags && item.tags.map((tag, idx) => (
                                <span
                                    key={idx}
                                    className="tag"
                                    style={{ cursor: 'pointer' }}
                                    onClick={() => onFilter && onFilter('tag', tag)}
                                    title="Filter by tag"
                                >
                                    #{tag}
                                </span>
                            ))}
                        </div>

                        <div className="flex gap-2">
                            {!canEdit(item) && (
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => copyToClipboard(item.prompt_text || "Prompt text not available")}
                                    style={{ flex: 1 }}
                                >
                                    Copy Prompt
                                </button>
                            )}
                            <button
                                className="btn btn-primary"
                                onClick={() => setSelectedPrompt(item)}
                                style={{ flex: 1 }}
                            >
                                View Prompt
                            </button>
                            {canEdit(item) && (
                                <button
                                    className="btn"
                                    onClick={() => onEdit && onEdit(item)}
                                    style={{
                                        flex: 1,
                                        background: '#059669',
                                        color: 'white'
                                    }}
                                    title="You can edit this because you are the owner"
                                >
                                    Edit
                                </button>
                            )}
                        </div>
                    </div>
                ))}

                {results.length === 0 && (
                    <div style={{ textAlign: 'center', color: '#64748b', padding: '2rem', gridColumn: '1 / -1' }}>
                        No results found. Try searching or add a new prompt!
                    </div>
                )}
            </div>

            {/* Modal */}
            {selectedPrompt && (
                <div className="modal-overlay" onClick={() => setSelectedPrompt(null)}>
                    <div className="modal-content" onClick={e => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setSelectedPrompt(null)}>&times;</button>

                        <h2 style={{ marginTop: 0, color: '#60a5fa', marginBottom: '0.5rem' }}>{selectedPrompt.title}</h2>
                        <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '1rem' }}>
                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                {(Array.isArray(selectedPrompt.tool_used) ? selectedPrompt.tool_used : [selectedPrompt.tool_used]).map((tool, idx) => (
                                    <span key={idx} style={{ fontSize: '1.1rem', fontWeight: '600', color: '#38bdf8' }}>
                                        {tool}{idx < (Array.isArray(selectedPrompt.tool_used) ? selectedPrompt.tool_used.length : 1) - 1 ? ', ' : ''}
                                    </span>
                                ))}
                            </div>
                            {selectedPrompt.username && (
                                <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                                    Submitted by <span style={{ color: '#f8fafc', fontWeight: 'bold' }}>{selectedPrompt.username}</span>
                                </span>
                            )}
                        </div>

                        <p style={{ color: '#cbd5e1' }}>{selectedPrompt.description}</p>

                        <div className="mb-4">
                            {selectedPrompt.tags && selectedPrompt.tags.map((tag, idx) => (
                                <span key={idx} className="tag">#{tag}</span>
                            ))}
                        </div>

                        <h3>Prompt:</h3>
                        <div className="prompt-text-block">
                            {selectedPrompt.prompt_text || "No prompt text available."}
                        </div>

                        <div className="mt-4 flex justify-between">
                            <button
                                className="btn btn-secondary"
                                onClick={() => setSelectedPrompt(null)}
                            >
                                Close
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={() => copyToClipboard(selectedPrompt.prompt_text || "")}
                            >
                                Copy to Clipboard
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PromptList;
