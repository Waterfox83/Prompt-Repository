import React, { useState, useEffect } from 'react';
import PromptForm from './components/PromptForm';
import PromptList from './components/PromptList';
import Login from './components/Login';
import AboutModal from './components/AboutModal';
import { DashboardLayout, TopBar, MainCanvas, Sidebar } from './components/dashboard';

import { API_URL } from './config';

import { ToastProvider, useToast } from './components/Toast';

function AppContent() {
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('browse');
  const [allPrompts, setAllPrompts] = useState([]); // Store all prompts for client-side filtering
  const [displayedPrompts, setDisplayedPrompts] = useState([]); // What is currently shown
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [activeFilter, setActiveFilter] = useState(null);
  const [showAbout, setShowAbout] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState(null); // State for editing prompt
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const { addToast } = useToast();

  // Check auth on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/me`, {
        credentials: 'include', // Send cookies
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
        handleBrowse(); // Fetch prompts if logged in
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      setUser(null);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSave = async (data, promptId = null) => {
    console.log("handleSave called with:", data, "promptId:", promptId); // Debug log
    console.log("API URL:", API_URL); // Debug log
    setLoading(true);
    try {
      const isUpdate = !!promptId;
      const url = isUpdate ? `${API_URL}/prompts/${promptId}` : `${API_URL}/prompts`;
      const method = isUpdate ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Send cookies
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const result = await response.json();
        addToast(isUpdate ? 'Prompt updated successfully!' : 'Prompt saved successfully!', 'success');

        // Track in localStorage if new
        if (!isUpdate && result.id) {
          const myPrompts = JSON.parse(localStorage.getItem('myPrompts') || '[]');
          myPrompts.push(result.id);
          localStorage.setItem('myPrompts', JSON.stringify(myPrompts));
        }

        setActiveTab('browse');
        handleBrowse(); // Refresh list
      } else {
        addToast(isUpdate ? 'Failed to update prompt.' : 'Failed to save prompt.', 'error');
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
      setActiveFilter(null);
      return;
    }
    setSearchLoading(true);
    setActiveFilter(null); // Clear filter on search
    try {
      console.log("Fetching search results from:", `${API_URL}/search?q=${encodeURIComponent(query)}`); // Debug log
      const response = await fetch(`${API_URL}/search?q=${encodeURIComponent(query)}`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        setDisplayedPrompts(data.results);
      } else {
        addToast('Failed to search prompts.', 'error');
      }
    } catch (error) {
      console.error('Error searching prompts:', error);
      addToast('Error searching prompts. Is the backend running?', 'error');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleBrowse = async () => {
    try {
      const response = await fetch(`${API_URL}/prompts`, {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        // Sort by date descending (newest first)
        const sorted = data.results.sort((a, b) => {
          return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        });
        setAllPrompts(sorted);
        setDisplayedPrompts(sorted);
        setActiveFilter(null);
      } else {
        addToast('Failed to fetch prompts.', 'error');
      }
    } catch (error) {
      console.error('Error fetching prompts:', error);
      addToast('Error fetching prompts.', 'error');
    }
  };

  const [favoritesRefreshTrigger, setFavoritesRefreshTrigger] = useState(0);

  const handleFavoriteToggle = async (promptId, isFavorited) => {
    // Update the local state immediately for better UX
    const updatePromptInList = (prompts) => {
      return prompts.map(prompt => {
        if (prompt.id === promptId) {
          return {
            ...prompt,
            user_context: {
              ...prompt.user_context,
              is_favorited: isFavorited
            }
          };
        }
        return prompt;
      });
    };

    // Update both allPrompts and displayedPrompts
    setAllPrompts(prev => updatePromptInList(prev));
    setDisplayedPrompts(prev => updatePromptInList(prev));

    // If we're currently viewing favorites, refresh the favorites view
    if (activeFilter && activeFilter.type === 'favorites') {
      // Small delay to ensure backend is updated
      setTimeout(() => {
        handleFilter('favorites', 'Favorites');
      }, 100);
    }

    // Trigger favorites count refresh
    setFavoritesRefreshTrigger(prev => prev + 1);
  };

  const handleFilter = async (type, value) => {
    if (type === 'clear') {
      // Clear filter - same as clearFilter function
      setDisplayedPrompts(allPrompts);
      setActiveFilter(null);
      return;
    }
    
    setActiveFilter({ type, value });
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
    } else if (type === 'my-prompts') {
      // Filter prompts owned by the current user
      const filtered = allPrompts.filter(p => {
        if (!user || !user.email) return false;
        return p.owner_email && p.owner_email === user.email;
      });
      setDisplayedPrompts(filtered);
    } else if (type === 'favorites') {
      // Fetch user's favorites and filter prompts
      console.log('Fetching favorites for user:', user?.email);
      try {
        const response = await fetch(`${API_URL}/users/me/favorites`, {
          credentials: 'include',
        });
        console.log('Favorites response status:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('Favorites data:', data);
          setDisplayedPrompts(data.favorites);
        } else {
          const errorText = await response.text();
          console.error('Favorites API error:', response.status, errorText);
          addToast('Failed to load favorites', 'error');
          setDisplayedPrompts([]);
        }
      } catch (error) {
        console.error('Error loading favorites:', error);
        addToast('Error loading favorites', 'error');
        setDisplayedPrompts([]);
      }
    }
  };

  const clearFilter = () => {
    setDisplayedPrompts(allPrompts);
    setActiveFilter(null);
  };

  const handleLogout = () => {
    setUser(null);
    setActiveTab('browse');
    setAllPrompts([]);
    setDisplayedPrompts([]);
    setActiveFilter(null);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'browse') {
      setEditingPrompt(null);
    }
  };

  const handleMobileSidebarToggle = () => {
    setIsMobileSidebarOpen(!isMobileSidebarOpen);
  };

  // Generate context actions for top bar
  const getContextActions = () => {
    const actions = [];
    
    if (activeTab === 'browse') {
      actions.push({
        label: 'Add New',
        icon: '+',
        variant: 'primary',
        onClick: () => setActiveTab('add')
      });
      
      if (activeFilter) {
        actions.push({
          label: 'Clear Filter',
          variant: 'secondary',
          onClick: clearFilter
        });
      }
    }
    
    return actions;
  };

  // Load browse results on mount - REMOVED, called in checkAuth
  // React.useEffect(() => {
  //   handleBrowse();
  // }, []);

  if (authLoading) {
    return <div style={{ display: 'flex', justifyContent: 'center', marginTop: '4rem' }}>Loading...</div>;
  }

  if (!user) {
    return <Login />;
  }

  return (
    <DashboardLayout
      isMobileSidebarOpen={isMobileSidebarOpen}
      sidebar={
        <Sidebar
          activeTab={activeTab}
          onTabChange={handleTabChange}
          activeFilter={activeFilter}
          onFilter={handleFilter}
          user={user}
          onMobileToggle={handleMobileSidebarToggle}
          favoritesRefreshTrigger={favoritesRefreshTrigger}
          onLogout={handleLogout}
        />
      }
      topBar={
        <TopBar
          user={user}
          onLogout={handleLogout}
          contextActions={getContextActions()}
          onMobileMenuToggle={handleMobileSidebarToggle}
        />
      }
      mainContent={
        <MainCanvas context={activeTab}>
          {/* About Button - positioned absolutely */}
          <button
            onClick={() => setShowAbout(true)}
            style={{
              position: 'absolute',
              top: '1rem',
              right: '1rem',
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '0.9rem',
              textDecoration: 'underline',
              zIndex: 10
            }}
          >
            About
          </button>

          {activeTab === 'add' && (
            <PromptForm 
              onSave={handleSave} 
              loading={loading}
              onCancel={() => setActiveTab('browse')}
            />
          )}

          {activeTab === 'browse' && (
            <PromptList
              onSearch={handleSearch}
              results={displayedPrompts}
              loading={searchLoading}
              onFilter={handleFilter}
              activeFilter={activeFilter}
              onEdit={(prompt) => {
                setActiveTab('edit');
                setEditingPrompt(prompt);
              }}
              user={user}
              onFavoriteToggle={handleFavoriteToggle}
            />
          )}

          {activeTab === 'edit' && (
            <PromptForm
              onSave={(data) => handleSave(data, editingPrompt?.id)}
              loading={loading}
              initialData={editingPrompt}
              onCancel={() => {
                setActiveTab('browse');
                setEditingPrompt(null);
              }}
            />
          )}

          {showAbout && <AboutModal onClose={() => setShowAbout(false)} />}
        </MainCanvas>
      }
    />
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
