import React, { useState } from 'react';
import toolMetadataService from '../../services/ToolMetadataService';
import './ToolHeader.css';

const ToolHeader = ({ toolName, promptCount = 0 }) => {
  const [isUseCasesExpanded, setIsUseCasesExpanded] = useState(false);

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

      {tool.useCases && tool.useCases.length > 0 && (
        <div className="tool-header-use-cases">
          <button 
            className="use-cases-header"
            onClick={() => setIsUseCasesExpanded(!isUseCasesExpanded)}
          >
            <h3>Use Cases ({tool.useCases.length})</h3>
            <span className={`expand-icon ${isUseCasesExpanded ? 'expanded' : ''}`}>
              ▶
            </span>
          </button>
          
          {isUseCasesExpanded && (
            <ul className="use-cases-list">
              {tool.useCases.map((useCase, index) => (
                <li key={index} className="use-case-item">
                  {useCase}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default ToolHeader;