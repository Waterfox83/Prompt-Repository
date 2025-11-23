import React, { useState } from 'react';

const PromptForm = ({ onSave, loading }) => {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        tool_used: '',
        prompt_text: '',
        tags: ''
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log("Form submitted!", formData); // Debug log
        // Convert comma-separated tags to list
        const payload = {
            ...formData,
            tags: formData.tags.split(',').map(t => t.trim()).filter(t => t)
        };
        console.log("Payload:", payload); // Debug log
        await onSave(payload);
        // Reset form
        setFormData({ title: '', description: '', tool_used: '', prompt_text: '', tags: '' });
    };

    return (
        <div className="card">
            <h2>Add New Utility / Prompt</h2>
            <form onSubmit={handleSubmit}>
                <div className="grid grid-cols-2 mb-4">
                    <div>
                        <label>Title</label>
                        <input
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            placeholder="e.g., Code Refactor Agent"
                            required
                            disabled={loading}
                        />
                    </div>
                    <div>
                        <label>Tool Used</label>
                        <input
                            name="tool_used"
                            value={formData.tool_used}
                            onChange={handleChange}
                            placeholder="e.g., Cursor, Copilot"
                            required
                            disabled={loading}
                        />
                    </div>
                </div>

                <div className="mb-4">
                    <label>Description</label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        placeholder="What does this utility do?"
                        rows="2"
                        required
                        disabled={loading}
                    />
                </div>

                <div className="mb-4">
                    <label>Prompt / Instructions</label>
                    <textarea
                        name="prompt_text"
                        value={formData.prompt_text}
                        onChange={handleChange}
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
                        name="tags"
                        value={formData.tags}
                        onChange={handleChange}
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
                    {loading ? 'Saving...' : 'Save to Repository'}
                </button>
            </form>
        </div>
    );
};

export default PromptForm;
