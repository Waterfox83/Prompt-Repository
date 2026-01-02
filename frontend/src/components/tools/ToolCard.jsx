import React, { useEffect, useRef } from 'react';
import toolMetadataService from '../../services/ToolMetadataService';
import './ToolCard.css';

const ToolCard = ({ toolName, onViewPrompts, onClose, promptCount = 0 }) => {
  const modalRef = useRef(null);
  const closeButtonRef = useRef(null);

  // Get tool information from metadata service
  const tool = toolMetadataService.getToolByDisplayName(toolName) || 
               toolMetadataService.createFallbackTool(toolName);

  // Focus management for accessibility
  useEffect(() => {
    if (closeButtonRef.current) {
      closeButtonRef.current.focus();
    }

    // Handle escape key
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    // Trap focus within modal
    const handleTabKey = (e) => {
      if (e.key === 'Tab') {
        const focusableElements = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements && focusableElements.length > 0) {
          const firstElement = focusableElements[0];
          const lastElement = focusableElements[focusableElements.length - 1];

          if (e.shiftKey) {
            if (document.activeElement === firstElement) {
              e.preventDefault();
              lastElement.focus();
            }
          } else {
            if (document.activeElement === lastElement) {
              e.preventDefault();
              firstElement.focus();
            }
          }
        }
      }
    };

    document.addEventListener('keydown', handleEscape);
    document.addEventListener('keydown', handleTabKey);

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.removeEventListener('keydown', handleTabKey);
    };
  }, [onClose]);

  const handleViewAllPrompts = () => {
    onViewPrompts(toolName);
    onClose();
  };

  const handleVisitWebsite = () => {
    if (tool.accessUrl && tool.accessUrl !== '#') {
      window.open(tool.accessUrl, '_blank', 'noopener,noreferrer');
    }
  };

  const categoryInfo = toolMetadataService.getCategoryInfo(tool.category);

  return (
    <div 
      className="tool-card-overlay" 
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="tool-card-title"
    >
      <div 
        className="tool-card-content" 
        onClick={e => e.stopPropagation()}
        ref={modalRef}
      >
        <button 
          className="tool-card-close" 
          onClick={onClose}
          ref={closeButtonRef}
          aria-label="Close tool information"
        >
          &times;
        </button>

        <div className="tool-card-header">
          <div className="tool-card-icon">◽️</div>
          <div className="tool-card-title-section">
            <h2 id="tool-card-title" className="tool-card-title">{tool.displayName}</h2>
            {categoryInfo && (
              <div className="tool-card-category">
                <span className="category-icon">{categoryInfo.icon}</span>
                <span className="category-name">{categoryInfo.name}</span>
              </div>
            )}
          </div>
        </div>

        <div className="tool-card-description">
          <p>{tool.detailedDescription || tool.description}</p>
        </div>

        {tool.useCases && tool.useCases.length > 0 && (
          <div className="tool-card-use-cases">
            <h3>Use Cases</h3>
            <ul className="use-cases-list">
              {tool.useCases.map((useCase, index) => (
                <li key={index} className="use-case-item">
                  {useCase}
                </li>
              ))}
            </ul>
          </div>
        )}

        {promptCount > 0 && (
          <div className="tool-card-stats">
            <div className="stat-item">
              <span className="stat-number">{promptCount}</span>
              <span className="stat-label">prompt{promptCount !== 1 ? 's' : ''} available</span>
            </div>
          </div>
        )}

        <div className="tool-card-actions">
          {promptCount > 0 && (
            <button 
              className="btn btn-primary tool-card-action"
              onClick={handleViewAllPrompts}
            >
              View All Prompts ({promptCount})
            </button>
          )}
          
          {tool.accessUrl && tool.accessUrl !== '#' && (
            <button 
              className="btn btn-secondary tool-card-action"
              onClick={handleVisitWebsite}
            >
              Visit Official Website
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ToolCard;