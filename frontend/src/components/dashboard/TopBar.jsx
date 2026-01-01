import React from 'react';
import './TopBar.css';

const TopBar = ({ user, onLogout, contextActions = [], onMobileMenuToggle }) => {
  return (
    <div className="topbar">
      {/* Mobile Menu Button */}
      <button
        className="mobile-menu-btn"
        onClick={onMobileMenuToggle}
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
        </svg>
      </button>

      {/* App Title */}
      <div className="topbar-title">
        <h1>PROMPT REPOSITORY</h1>
      </div>

      {/* Context Actions */}
      <div className="topbar-actions">
        {/* Context-aware action buttons */}
        {contextActions.map((action, index) => (
          <button
            key={index}
            className={`topbar-action-btn ${action.variant || 'secondary'}`}
            onClick={action.onClick}
            disabled={action.disabled}
          >
            {action.icon && <span className="action-icon">{action.icon}</span>}
            {action.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default TopBar;