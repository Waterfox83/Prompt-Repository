import React, { useState } from 'react';
import { useFavorites } from '../../hooks/useFavorites';
import './Sidebar.css';

const Sidebar = ({ 
  activeTab, 
  onTabChange, 
  activeFilter, 
  onFilter, 
  user,
  onMobileToggle,
  favoritesRefreshTrigger,
  onLogout
}) => {
  const [isToolsExpanded, setIsToolsExpanded] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const { favoritesCount, refetch: refetchFavorites } = useFavorites(user);

  // Refetch favorites count when refresh trigger changes
  React.useEffect(() => {
    if (favoritesRefreshTrigger > 0) {
      refetchFavorites();
    }
  }, [favoritesRefreshTrigger, refetchFavorites]);

  const handleLogout = async () => {
    try {
      await fetch('/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
      if (onLogout) onLogout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
    setShowUserMenu(false);
  };

  const navigationItems = [
    {
      id: 'browse',
      label: 'Home',
      onClick: () => {
        onTabChange('browse');
        // Clear any active filters to return to true home state
        // We'll pass a special 'clear' type to indicate filter clearing
        onFilter('clear', null);
      }
    },
    {
      id: 'my-prompts',
      label: 'My Prompts',
      onClick: () => {
        onTabChange('browse');
        if (user && user.email) {
          onFilter('my-prompts', 'My Prompts');
        }
      }
    },
    {
      id: 'favorites',
      label: 'Favorites',
      count: favoritesCount,
      onClick: () => {
        onTabChange('browse');
        onFilter('favorites', 'Favorites');
      }
    }
  ];

  // Placeholder tools - will be enhanced in later tasks
  const tools = [
    { id: 'chatgpt', name: 'ChatGPT' },
    { id: 'claude', name: 'Claude' },
    { id: 'copilot', name: 'GitHub Copilot' },
    { id: 'midjourney', name: 'Midjourney' }
  ];

  return (
    <nav className="sidebar">
      {/* Sidebar Header with User Menu */}
      <div className="sidebar-header">
        {/* User Profile Dropdown */}
        <div className="user-menu-container">
          <button
            className="user-menu-trigger"
            onClick={() => setShowUserMenu(!showUserMenu)}
          >
            <div className="user-avatar">
              {user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <span className="user-email">{user?.email || 'User'}</span>
            <svg 
              className={`dropdown-arrow ${showUserMenu ? 'open' : ''}`}
              width="16" 
              height="16" 
              viewBox="0 0 16 16" 
              fill="currentColor"
            >
              <path d="M4.427 9.573L8 6l3.573 3.573a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708z"/>
            </svg>
          </button>

          {showUserMenu && (
            <div className="user-menu-dropdown">
              <div className="user-menu-header">
                <div className="user-info">
                  <div className="user-name">{user?.email || 'User'}</div>
                </div>
              </div>
              <div className="user-menu-divider"></div>
              <button className="user-menu-item" onClick={() => setShowUserMenu(false)}>
                <span>Preferences</span>
              </button>
              <button className="user-menu-item" onClick={() => setShowUserMenu(false)}>
                <span>Help & Support</span>
              </button>
              <div className="user-menu-divider"></div>
              <button className="user-menu-item logout" onClick={handleLogout}>
                <span>Sign Out</span>
              </button>
            </div>
          )}
        </div>

        <button 
          className="mobile-close-btn"
          onClick={onMobileToggle}
        >
          ×
        </button>
      </div>

      {/* Main Navigation */}
      <div className="sidebar-section">
        <ul className="nav-list">
          {navigationItems.map((item) => (
            <li key={item.id}>
              <button
                className={`nav-item ${
                  (item.id === 'browse' && activeTab === 'browse' && !activeFilter) ||
                   (item.id === 'my-prompts' && activeFilter?.type === 'my-prompts') ||
                   (item.id === 'favorites' && activeFilter?.type === 'favorites') 
                    ? 'active' : ''
                }`}
                onClick={item.onClick}
              >
                <span className="nav-icon"></span>
                <span className="nav-label">{item.label}</span>
                {item.count !== undefined && item.count > 0 && (
                  <span className="nav-count">{item.count}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {/* AI Tools Directory */}
      <div className="sidebar-section">
        <button
          className="section-header"
          onClick={() => setIsToolsExpanded(!isToolsExpanded)}
        >
          <span className="section-title">AI Toolbox</span>
          <span className={`expand-icon ${isToolsExpanded ? 'expanded' : ''}`}>
            ▶
          </span>
        </button>
        
        {isToolsExpanded && (
          <ul className="tools-list">
            {tools.map((tool) => (
              <li key={tool.id}>
                <button
                  className={`tool-item ${
                    activeFilter?.type === 'tool' && activeFilter?.value === tool.name 
                      ? 'active' : ''
                  }`}
                  onClick={() => {
                    onTabChange('browse');
                    onFilter('tool', tool.name);
                  }}
                >
                  <span className="tool-icon"></span>
                  <span className="tool-name">{tool.name}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer Links */}
      <div className="sidebar-footer">
        <button className="footer-link">
          <span>How to Contribute</span>
        </button>
      </div>
    </nav>
  );
};

export default Sidebar;