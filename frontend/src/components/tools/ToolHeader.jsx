import React from 'react';
import toolMetadataService from '../../services/ToolMetadataService';
import './ToolHeader.css';

const ToolHeader = ({ toolName, promptCount = 0 }) => {
  // Get tool information from metadata service
  const tool = toolMetadataService.getToolByDisplayName(toolName) || 
               toolMetadataService.createFallbackTool(toolName);

  const categoryInfo = toolMetadataService.getCategoryInfo(tool.category);

  const handleVisitWebsite = () => {
    if (tool.accessUrl && tool.accessUrl !== '#') {
      window.open(tool.accessUrl, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="tool-header">
      <div className="tool-header-main">
        <div className="tool-header-icon-section">
          <div className="tool-header-info">
            <h1 className="tool-header-title">{tool.displayName}</h1>
          
          </div>
        </div>

        <div className="tool-header-actions">
          {tool.accessUrl && tool.accessUrl !== '#' && (
            <button 
              className="btn btn-primary tool-header-action"
              onClick={handleVisitWebsite}
            >
              <span className="action-icon">🔗</span>
              Visit {tool.displayName}
            </button>
          )}
        </div>
      </div>

      <div className="tool-header-description">
        <p>{tool.detailedDescription || tool.description}</p>
      </div>

      {tool.isFallback && (
        <div className="tool-header-fallback-notice">
          <p>
            <strong>Note:</strong> This tool information is limited. 
            Visit the official website for more details.
          </p>
        </div>
      )}
    </div>
  );
};

export default ToolHeader;