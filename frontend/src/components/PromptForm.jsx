import React, { useState } from 'react';
import { useToast } from './Toast';

const PromptForm = ({ onSave, loading }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [selectedTools, setSelectedTools] = useState([]);
    const [toolInput, setToolInput] = useState('');
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [promptText, setPromptText] = useState('');
    const [tags, setTags] = useState('');
    const [username, setUsername] = useState('');
    const { addToast } = useToast();

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
        // Reset form
        setTitle('');
        setDescription('');
        setSelectedTools([]);
        setToolInput('');
        setPromptText('');
        setTags('');
        setUsername('');
    };

    return (
        <div className="card">
            <h2>Add New Prompt</h2>
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

                <div className="mb-4">
                    <label>Tags (comma separated)</label>
                    <input
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                        placeholder="coding, debug, python"
                        disabled={loading}
                    />
                </div>

                <button
                    type="submit"
                    className="btn btn-primary"
                    style={{ width: '100%', opacity: loading ? 0.7 : 1, cursor: loading ? 'not-allowed' : 'pointer' }}
                    disabled={loading}
                >
                    {loading ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <div className="spinner"></div>
                            Saving...
                        </div>
                    ) : 'Save to Repository'}
                </button>
            </form>
        </div>
    );
};

export default PromptForm;
