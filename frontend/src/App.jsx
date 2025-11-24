import React, { useState } from 'react';
import PromptForm from './components/PromptForm';
import PromptList from './components/PromptList';

const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

import { ToastProvider, useToast } from './components/Toast';

function AppContent() {
  const [activeTab, setActiveTab] = useState('browse');
  const [allPrompts, setAllPrompts] = useState([]); // Store all prompts for client-side filtering
  const [displayedPrompts, setDisplayedPrompts] = useState([]); // What is currently shown
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();

  const handleSave = async (data) => {
    console.log("handleSave called with:", data); // Debug log
    console.log("API URL:", API_URL); // Debug log
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/prompts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        addToast('Prompt saved successfully!', 'success');
        setActiveTab('browse');
        handleBrowse(); // Refresh list
      } else {
        addToast('Failed to save prompt.', 'error');
      }
    } catch (error) {
      console.error('Error saving prompt:', error);
      addToast('Error saving prompt. Is the backend running?', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    console.log("handleSearch called with query:", query); // Debug log
    if (!query.trim()) {
      console.log("Query empty, resetting to all prompts"); // Debug log
      setDisplayedPrompts(allPrompts); // Reset if empty
      return;
    }
    try {
      console.log("Fetching search results from:", `${API_URL}/search?q=${encodeURIComponent(query)}`); // Debug log
      const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setDisplayedPrompts(data.results);
      } else {
        addToast('Failed to search prompts.', 'error');
      }
    } catch (error) {
      console.error('Error searching prompts:', error);
      addToast('Error searching prompts. Is the backend running?', 'error');
    }
  };

  const handleBrowse = async () => {
    try {
      const response = await fetch(`${API_URL}/prompts`);
      if (response.ok) {
        const data = await response.json();
        // Sort by date descending (newest first)
        const sorted = data.results.sort((a, b) => {
          return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        });
        setAllPrompts(sorted);
        setDisplayedPrompts(sorted);
      } else {
        addToast('Failed to fetch prompts.', 'error');
      }
    } catch (error) {
      console.error('Error fetching prompts:', error);
      addToast('Error fetching prompts.', 'error');
    }
  };

  const handleFilter = (type, value) => {
    if (type === 'tag') {
      const filtered = allPrompts.filter(p => p.tags && p.tags.includes(value));
      setDisplayedPrompts(filtered);
    } else if (type === 'tool') {
      // Handle both array (new) and string (old) for backward compatibility
      const filtered = allPrompts.filter(p => {
        if (Array.isArray(p.tool_used)) {
          return p.tool_used.includes(value);
        }
        return p.tool_used === value;
      });
      setDisplayedPrompts(filtered);
    } else if (type === 'username') {
      const filtered = allPrompts.filter(p => p.username === value);
      setDisplayedPrompts(filtered);
    }
  };

  // Load browse results on mount
  React.useEffect(() => {
    handleBrowse();
  }, []);

  return (
    <div className="container">
      <h1>Prompt Repository</h1>

      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem', gap: '1rem' }}>
        <button
          className={`btn ${activeTab === 'browse' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => {
            setActiveTab('browse');
            setDisplayedPrompts(allPrompts); // Reset filters
          }}
        >
          Browse All
        </button>
        <button
          className={`btn ${activeTab === 'add' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('add')}
        >
          Add New
        </button>
      </div>

      {activeTab === 'add' && (
        <PromptForm onSave={handleSave} loading={loading} />
      )}

      {activeTab === 'browse' && (
        <div>
          <PromptList
            onSearch={handleSearch}
            results={displayedPrompts}
            onFilter={handleFilter}
          />
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}

export default App;
