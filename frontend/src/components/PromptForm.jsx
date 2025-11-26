import React, { useState } from 'react';
import { useToast } from './Toast';

const PromptForm = ({ onSave, loading, initialData = null, onCancel = null }) => {
    const [title, setTitle] = useState(initialData?.title || '');
    const [description, setDescription] = useState(initialData?.description || '');
    const [generating, setGenerating] = useState(false); // New state for AI generation
    const [selectedTools, setSelectedTools] = useState(initialData?.tool_used || []);
    const [toolInput, setToolInput] = useState('');
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [promptText, setPromptText] = useState(initialData?.prompt_text || '');
    const [tags, setTags] = useState(initialData?.tags ? initialData.tags.join(', ') : '');
    const [username, setUsername] = useState(initialData?.username || '');
    const { addToast } = useToast();
    
    const isEditing = !!initialData;

    const PREDEFINED_TOOLS = [
        "ChatGPT", "Claude", "Gemini", "Llama 3", "Mistral",
        "Copilot", "Midjourney", "DALL-E 3", "Stable Diffusion",
        "NotebookLM", "AgentSpace", "GitHub Copilot", "Cline", "Cursor"
    ];

    const handleAddTool = (tool) => {
        if (tool && !selectedTools.includes(tool)) {
            setSelectedTools([...selectedTools, tool]);
        }
        setToolInput('');
        // Keep suggestions open for multiple selection
        // setShowSuggestions(false); 
    };

    const handleRemoveTool = (toolToRemove) => {
        setSelectedTools(selectedTools.filter(tool => tool !== toolToRemove));
    };

    const handleToolKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (toolInput.trim()) {
                handleAddTool(toolInput.trim());
            }
        }
    };

    const filteredTools = PREDEFINED_TOOLS.filter(tool =>
        tool.toLowerCase().includes(toolInput.toLowerCase()) &&
        !selectedTools.includes(tool)
    );

    const handleGenerate = async () => {
        if (!title.trim() || !promptText.trim()) {
            addToast("Please provide a Title and Prompt Text to generate details.", "error");
            return;
        }

        setGenerating(true);
        try {
            const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');
            const response = await fetch(`${API_URL}/generate-details`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: title,
                    prompt_text: promptText
                }),
            });

            if (response.ok) {
                const data = await response.json();
                if (data.description) setDescription(data.description);
                if (data.tags && Array.isArray(data.tags)) setTags(data.tags.join(', '));
                addToast("Details generated successfully!", "success");
            } else {
                addToast("Failed to generate details.", "error");
            }
        } catch (error) {
            console.error("Error generating details:", error);
            addToast("Error connecting to AI service.", "error");
        } finally {
            setGenerating(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const tagsList = tags.split(',').map(tag => tag.trim()).filter(tag => tag);

        // Ensure at least one tool is selected or allow empty?
        // Let's require at least one tool or use "Other" if empty?
        // For now, if empty, we can just send empty list or validation error.
        // Let's assume user must select at least one.
        if (selectedTools.length === 0) {
            addToast("Please select or add at least one tool.", "error");
            return;
        }

        await onSave({
            title,
            description,
            tool_used: selectedTools, // Send list
            prompt_text: promptText,
            tags: tagsList,
            username: username.trim() || null
        });
        
        // Reset form only if not editing
        if (!isEditing) {
            setTitle('');
            setDescription('');
            setSelectedTools([]);
            setToolInput('');
            setPromptText('');
            setTags('');
            setUsername('');
        }
    };

    return (
        <div className="card">
            <h2>{isEditing ? 'Edit Prompt' : 'Add New Prompt'}</h2>
            {!isEditing && (
                <div style={{
                    background: 'rgba(34, 197, 94, 0.1)',
                    border: '1px solid rgba(34, 197, 94, 0.3)',
                    borderRadius: '0.5rem',
                    padding: '0.75rem 1rem',
                    marginBottom: '1.5rem',
                    color: '#86efac',
                    fontSize: '0.9rem'
                }}>
                    💡 <strong>Tip:</strong> You can edit any prompt you create during this session. Once you close your browser, the edit option will no longer be available.
                </div>
            )}
            <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-2 mb-4">
                    <div>
                        <label>Title</label>
                        <input
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            required
                            placeholder="e.g., Python Fibonacci Generator"
                            disabled={loading}
                        />
                    </div>
                    <div>
                        <label>Tools Used</label>
                        <div className="custom-select-container">
                            <div className="flex flex-wrap gap-2 mb-2">
                                {selectedTools.map((tool, idx) => (
                                    <span key={idx} className="tool-badge-removable" style={{
                                        background: 'rgba(56, 189, 248, 0.1)',
                                        border: '1px solid rgba(56, 189, 248, 0.2)',
                                        color: '#38bdf8',
                                        padding: '0.2rem 0.5rem',
                                        borderRadius: '0.25rem',
                                        fontSize: '0.85rem',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem'
                                    }}>
                                        {tool}
                                        <button
                                            type="button"
                                            onClick={() => handleRemoveTool(tool)}
                                            style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', padding: 0, fontSize: '1rem', lineHeight: 1 }}
                                        >
                                            &times;
                                        </button>
                                    </span>
                                ))}
                            </div>
                            <input
                                value={toolInput}
                                onChange={(e) => {
                                    setToolInput(e.target.value);
                                    setShowSuggestions(true);
                                }}
                                onKeyDown={handleToolKeyDown}
                                onFocus={() => setShowSuggestions(true)}
                                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                                placeholder="Type to search or add custom..."
                                disabled={loading}
                                autoComplete="off"
                            />
                            {showSuggestions && filteredTools.length > 0 && (
                                <ul className="suggestions-list">
                                    {filteredTools.map(tool => (
                                        <li
                                            key={tool}
                                            className="suggestion-item"
                                            onClick={() => handleAddTool(tool)}
                                        >
                                            {tool}
                                        </li>
                                    ))}
                                </ul>
                            )}
                            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                                Type and press Enter for custom tools, or select from list.
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mb-4">
                    <label>Your Name (Optional)</label>
                    <input
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="e.g., Alice"
                        disabled={loading}
                    />
                </div>

                <div className="mb-4">
                    <label>Prompt / Instructions</label>
                    <textarea
                        value={promptText}
                        onChange={(e) => setPromptText(e.target.value)}
                        placeholder="Paste the full prompt here..."
                        rows="6"
                        required
                        style={{ fontFamily: 'monospace' }}
                        disabled={loading}
                    />
                </div>

                <div className="mb-4" style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                        type="button"
                        onClick={handleGenerate}
                        className="btn btn-secondary"
                        disabled={loading || generating}
                        style={{ fontSize: '0.9rem', padding: '0.4rem 0.8rem' }}
                    >
                        {generating ? 'Generating...' : '✨ Generate Tags & Description with AI'}
                    </button>
                </div>

                <div className="mb-4">
                    <label>Description</label>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="What does this utility do?"
                        rows="2"
                        required
                        disabled={loading}
                    />
                </div>

                <div className="mb-4">
                    <label>Tags (comma separated)</label>
                    <input
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                        placeholder="coding, debug, python"
                        disabled={loading}
                    />
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                    {isEditing && onCancel && (
                        <button
                            type="button"
                            onClick={onCancel}
                            className="btn btn-secondary"
                            style={{ flex: 1 }}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                    )}
                    <button
                        type="submit"
                        className="btn btn-primary"
                        style={{ flex: 1, opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
                        disabled={loading}
                    >
                        {loading ? (
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <div className="spinner"></div>
                                {isEditing ? 'Updating...' : 'Saving...'}
                            </div>
                        ) : (isEditing ? 'Update Prompt' : 'Save to Repository')}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default PromptForm;
