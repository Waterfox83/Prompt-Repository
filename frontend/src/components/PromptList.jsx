import React, { useState } from 'react';
import { useToast } from './Toast';
import { HeroMissionStatement, SearchSuggestionChips } from './onboarding';
import { ToolCard, ToolHeader } from './tools';
import UpvoteButton from './UpvoteButton';

const PromptList = ({ onSearch, results, loading, onFilter, activeFilter, onEdit, user }) => {
    const [query, setQuery] = useState('');
    const [selectedPrompt, setSelectedPrompt] = useState(null);
    const [selectedTool, setSelectedTool] = useState(null);
    const [hasSearched, setHasSearched] = useState(false);
    const { addToast } = useToast();

    // Check if this appears to be a first-time user (simple heuristic)
    const isFirstTime = !localStorage.getItem('hasVisited');

    // Mark as visited
    React.useEffect(() => {
        if (!localStorage.getItem('hasVisited')) {
            localStorage.setItem('hasVisited', 'true');
        }
    }, []);

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
        setHasSearched(true);
        onSearch(query);
    };

    const handleSuggestionClick = (suggestionQuery) => {
        setQuery(suggestionQuery);
        setHasSearched(true);
        onSearch(suggestionQuery);
    };

    // Reset hasSearched when query is cleared and no filter is active
    React.useEffect(() => {
        if (!query.trim() && !activeFilter) {
            setHasSearched(false);
        }
    }, [query, activeFilter]);

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
        addToast('Prompt copied to clipboard!', 'success');
    };

    const handleToolClick = (toolName, e) => {
        e.stopPropagation(); // Prevent any parent click handlers
        setSelectedPrompt(null); // Close prompt modal if open
        setSelectedTool(toolName);
    };

    const handleUpvote = (promptId, newUpvoteCount, newIsUpvoted) => {
        // Update the upvote count in the results array
        // This provides immediate UI feedback while the parent component
        // can handle any additional state updates if needed
        console.log(`Prompt ${promptId} upvote updated: ${newUpvoteCount} upvotes, is_upvoted: ${newIsUpvoted}`);
    };

    const handleViewAllPrompts = (toolName) => {
        if (onFilter) {
            onFilter('tool', toolName);
        }
    };

    const getPromptCountForTool = (toolName) => {
        return results.filter(prompt => {
            if (Array.isArray(prompt.tool_used)) {
                return prompt.tool_used.includes(toolName);
            }
            return prompt.tool_used === toolName;
        }).length;
    };

    return (
        <div>
            {/* Show mission statement when no search/filter is active */}
            {!hasSearched && !activeFilter && !query.trim() && (
                <HeroMissionStatement isFirstTime={isFirstTime} />
            )}

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

                {/* Show search suggestions below the search box when no search/filter is active */}
                {!hasSearched && !activeFilter && !query.trim() && (
                    <div style={{ marginTop: '1rem' }}>
                        <SearchSuggestionChips
                            onSuggestionClick={handleSuggestionClick}
                            isFirstTime={isFirstTime}
                        />
                    </div>
                )}
            </div>

            {/* Show tool header when viewing tool-filtered content */}
            {activeFilter && activeFilter.type === 'tool' && (
                <ToolHeader
                    toolName={activeFilter.value}
                    promptCount={results.length}
                />
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
                                            border: '1px solid rgba(56, 189, 248, 0.2)',
                                            transition: 'all 0.2s ease',
                                            position: 'relative'
                                        }}
                                        onClick={(e) => handleToolClick(tool, e)}
                                        onMouseEnter={(e) => {
                                            e.target.style.background = 'rgba(56, 189, 248, 0.2)';
                                            e.target.style.borderColor = 'rgba(56, 189, 248, 0.4)';
                                            e.target.style.transform = 'translateY(-1px)';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.target.style.background = 'rgba(56, 189, 248, 0.1)';
                                            e.target.style.borderColor = 'rgba(56, 189, 248, 0.2)';
                                            e.target.style.transform = 'translateY(0)';
                                        }}
                                        title={`Click to learn more about ${tool}`}
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
                            <UpvoteButton
                                promptId={item.id}
                                upvotes={item.upvotes || 0}
                                isUpvoted={item.user_context?.is_upvoted || false}
                                onUpvote={handleUpvote}
                                size="medium"
                            />
                            <button
                                className="btn btn-primary"
                                onClick={() => setSelectedPrompt(item)}
                                style={{ flex: 1 }}
                            >
                                {canEdit(item) ? 'View' : 'View Prompt'}
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
                                    <span
                                        key={idx}
                                        style={{
                                            fontSize: '1.1rem',
                                            fontWeight: '600',
                                            color: '#38bdf8',
                                            cursor: 'pointer',
                                            padding: '0.2rem 0.5rem',
                                            background: 'rgba(56, 189, 248, 0.1)',
                                            borderRadius: '0.25rem',
                                            border: '1px solid rgba(56, 189, 248, 0.2)',
                                            transition: 'all 0.2s ease'
                                        }}
                                        onClick={(e) => handleToolClick(tool, e)}
                                        onMouseEnter={(e) => {
                                            e.target.style.background = 'rgba(56, 189, 248, 0.2)';
                                            e.target.style.transform = 'translateY(-1px)';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.target.style.background = 'rgba(56, 189, 248, 0.1)';
                                            e.target.style.transform = 'translateY(0)';
                                        }}
                                        title={`Click to learn more about ${tool}`}
                                    >
                                        {tool}
                                    </span>
                                ))}
                            </div>
                            {selectedPrompt.username && (
                                <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>
                                    Submitted by <span style={{ color: '#f8fafc', fontWeight: 'bold' }}>{selectedPrompt.username}</span>
                                </span>
                            )}
                        </div>

                        <div style={{ fontSize: '0.75rem', color: '#475569', marginBottom: '1rem', fontFamily: 'monospace' }}>
                            ID: {selectedPrompt.id}
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
                            <div className="flex gap-2 items-center">
                                <UpvoteButton
                                    promptId={selectedPrompt.id}
                                    upvotes={selectedPrompt.upvotes || 0}
                                    isUpvoted={selectedPrompt.user_context?.is_upvoted || false}
                                    onUpvote={handleUpvote}
                                    size="medium"
                                />
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => setSelectedPrompt(null)}
                                >
                                    Close
                                </button>
                            </div>
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

            {/* Tool Card Overlay */}
            {selectedTool && (
                <ToolCard
                    toolName={selectedTool}
                    onViewPrompts={handleViewAllPrompts}
                    onClose={() => setSelectedTool(null)}
                    promptCount={getPromptCountForTool(selectedTool)}
                />
            )}
        </div>
    );
};

export default PromptList;
