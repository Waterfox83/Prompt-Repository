import React, { useState } from 'react';
import PromptForm from './components/PromptForm';
import PromptList from './components/PromptList';

const API_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [searchResults, setSearchResults] = useState([]);
  const [browseResults, setBrowseResults] = useState([]);
  const [loading, setLoading] = useState(false);

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
        alert('Prompt saved successfully!');
        setActiveTab('browse');
        handleBrowse(); // Refresh list
      } else {
        alert('Failed to save prompt.');
      }
    } catch (error) {
      console.error('Error saving prompt:', error);
      alert('Error saving prompt. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query) => {
    try {
      const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
      } else {
        alert('Failed to search prompts.');
      }
    } catch (error) {
      console.error('Error searching prompts:', error);
      alert('Error searching prompts. Is the backend running?');
    }
  };

  const handleBrowse = async () => {
    try {
      const response = await fetch(`${API_URL}/prompts`);
      if (response.ok) {
        const data = await response.json();
        setBrowseResults(data.results);
      } else {
        alert('Failed to fetch prompts.');
      }
    } catch (error) {
      console.error('Error fetching prompts:', error);
    }
  };

  // Load browse results when tab changes to browse
  React.useEffect(() => {
    if (activeTab === 'browse') {
      handleBrowse();
    }
  }, [activeTab]);

  return (
    <div className="container">
      <h1>AI Prompt Repository</h1>

      <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem', gap: '1rem' }}>
        <button
          className={`btn ${activeTab === 'search' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('search')}
        >
          Search
        </button>
        <button
          className={`btn ${activeTab === 'browse' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('browse')}
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

      {activeTab === 'search' && (
        <PromptList onSearch={handleSearch} results={searchResults} />
      )}

      {activeTab === 'browse' && (
        <div>
          <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>All Prompts</h2>
          <PromptList onSearch={() => { }} results={browseResults} />
        </div>
      )}
    </div>
  );
}

export default App;
