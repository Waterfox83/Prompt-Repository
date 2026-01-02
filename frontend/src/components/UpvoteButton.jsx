import React, { useState } from 'react';
import { useToast } from './Toast';
import { API_URL } from '../config';

const UpvoteButton = ({ 
  promptId, 
  upvotes = 0, 
  isUpvoted = false, 
  onUpvote, 
  size = 'medium' 
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [localUpvotes, setLocalUpvotes] = useState(upvotes);
  const [localIsUpvoted, setLocalIsUpvoted] = useState(isUpvoted);
  const { addToast } = useToast();

  const handleUpvote = async (e) => {
    e.stopPropagation(); // Prevent triggering parent click handlers
    
    setIsLoading(true);
    try {
      const method = localIsUpvoted ? 'DELETE' : 'POST';
      const response = await fetch(`${API_URL}/prompts/${promptId}/upvote`, {
        method,
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        const newUpvoteCount = data.upvotes;
        const newIsUpvoted = !localIsUpvoted;
        
        setLocalUpvotes(newUpvoteCount);
        setLocalIsUpvoted(newIsUpvoted);
        
        // Call parent callback if provided
        if (onUpvote) {
          onUpvote(promptId, newUpvoteCount, newIsUpvoted);
        }
        
        addToast(
          newIsUpvoted ? 'Upvoted!' : 'Upvote removed!', 
          'success'
        );
      } else {
        const errorData = await response.json().catch(() => ({}));
        
        // Handle specific error cases
        if (response.status === 400 && errorData.detail === 'Already upvoted') {
          addToast('You have already upvoted this prompt', 'error');
        } else if (response.status === 400 && errorData.detail === 'Not upvoted') {
          addToast('You have not upvoted this prompt', 'error');
        } else if (response.status === 404) {
          addToast('Prompt not found', 'error');
        } else {
          addToast(
            errorData.detail || 'Failed to update upvote', 
            'error'
          );
        }
      }
    } catch (error) {
      console.error('Error toggling upvote:', error);
      addToast('Failed to update upvote. Please try again.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return { 
          fontSize: '0.85rem', 
          padding: '0.25rem 0.5rem',
          iconSize: '0.9rem',
          gap: '0.25rem'
        };
      case 'large':
        return { 
          fontSize: '1.1rem', 
          padding: '0.5rem 0.75rem',
          iconSize: '1.2rem',
          gap: '0.375rem'
        };
      default:
        return { 
          fontSize: '0.95rem', 
          padding: '0.375rem 0.625rem',
          iconSize: '1rem',
          gap: '0.3rem'
        };
    }
  };

  const sizeStyles = getSizeStyles();

  return (
    <button
      onClick={handleUpvote}
      disabled={isLoading}
      className="upvote-button"
      title={localIsUpvoted ? 'Remove upvote' : 'Upvote this prompt'}
      style={{
        background: localIsUpvoted 
          ? 'rgba(34, 197, 94, 0.1)' 
          : 'transparent',
        border: localIsUpvoted 
          ? '1px solid rgba(34, 197, 94, 0.3)' 
          : '1px solid rgba(148, 163, 184, 0.3)',
        borderRadius: '0.375rem',
        color: localIsUpvoted ? '#22c55e' : '#94a3b8',
        cursor: isLoading ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: sizeStyles.gap,
        transition: 'all 0.2s ease',
        opacity: isLoading ? 0.6 : 1,
        fontSize: sizeStyles.fontSize,
        padding: sizeStyles.padding,
        fontWeight: '500'
      }}
      onMouseEnter={(e) => {
        if (!isLoading) {
          if (localIsUpvoted) {
            e.target.style.borderColor = 'rgba(34, 197, 94, 0.5)';
            e.target.style.background = 'rgba(34, 197, 94, 0.15)';
          } else {
            e.target.style.borderColor = 'rgba(148, 163, 184, 0.5)';
            e.target.style.background = 'rgba(148, 163, 184, 0.1)';
          }
        }
      }}
      onMouseLeave={(e) => {
        if (!isLoading) {
          if (localIsUpvoted) {
            e.target.style.borderColor = 'rgba(34, 197, 94, 0.3)';
            e.target.style.background = 'rgba(34, 197, 94, 0.1)';
          } else {
            e.target.style.borderColor = 'rgba(148, 163, 184, 0.3)';
            e.target.style.background = 'transparent';
          }
        }
      }}
    >
      {isLoading ? (
        <span 
          className="spinner"
          style={{
            width: '12px',
            height: '12px',
            border: '2px solid rgba(148, 163, 184, 0.3)',
            borderTop: '2px solid #94a3b8',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }}
        />
      ) : (
        <>
          <span style={{ 
            fontSize: sizeStyles.iconSize,
            lineHeight: 1,
            transform: localIsUpvoted ? 'scale(1.1)' : 'scale(1)',
            transition: 'transform 0.2s ease'
          }}>
            {localIsUpvoted ? '▲' : '△'}
          </span>
          <span style={{ 
            fontSize: 'inherit',
            fontWeight: '600',
            minWidth: '1ch'
          }}>
            {localUpvotes}
          </span>
        </>
      )}
    </button>
  );
};

export default UpvoteButton;