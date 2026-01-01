import React, { useState } from 'react';
import { useToast } from './Toast';
import { API_URL } from '../config';

const StarButton = ({ 
  promptId, 
  isFavorited = false, 
  onToggle, 
  size = 'medium'
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [localIsFavorited, setLocalIsFavorited] = useState(isFavorited);
  const { addToast } = useToast();

  const handleToggle = async (e) => {
    e.stopPropagation(); // Prevent triggering parent click handlers
    
    setIsLoading(true);
    try {
      const method = localIsFavorited ? 'DELETE' : 'POST';
      const response = await fetch(`${API_URL}/users/me/favorites/${promptId}`, {
        method,
        credentials: 'include',
      });

      if (response.ok) {
        const newState = !localIsFavorited;
        setLocalIsFavorited(newState);
        
        // Call parent callback if provided
        if (onToggle) {
          onToggle(promptId, newState);
        }
        
        addToast(
          newState ? 'Added to favorites!' : 'Removed from favorites!', 
          'success'
        );
      } else {
        const errorData = await response.json().catch(() => ({}));
        addToast(
          errorData.detail || 'Failed to update favorites', 
          'error'
        );
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      addToast('Error updating favorites', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return { fontSize: '0.9rem', padding: '0.25rem 0.5rem' };
      case 'large':
        return { fontSize: '1.2rem', padding: '0.5rem 0.75rem' };
      default:
        return { fontSize: '1rem', padding: '0.375rem 0.625rem' };
    }
  };

  const sizeStyles = getSizeStyles();

  return (
    <button
      onClick={handleToggle}
      disabled={isLoading}
      className="star-button"
      title={localIsFavorited ? 'Remove from favorites' : 'Add to favorites'}
      style={{
        background: 'transparent',
        border: '1px solid rgba(148, 163, 184, 0.3)',
        borderRadius: '0.375rem',
        color: localIsFavorited ? '#fbbf24' : '#94a3b8',
        cursor: isLoading ? 'not-allowed' : 'pointer',
        display: 'flex',
        alignItems: 'center',
        gap: '0.25rem',
        transition: 'all 0.2s ease',
        opacity: isLoading ? 0.6 : 1,
        ...sizeStyles
      }}
      onMouseEnter={(e) => {
        if (!isLoading) {
          e.target.style.borderColor = localIsFavorited ? '#fbbf24' : '#e2e8f0';
          e.target.style.background = 'rgba(148, 163, 184, 0.1)';
        }
      }}
      onMouseLeave={(e) => {
        if (!isLoading) {
          e.target.style.borderColor = 'rgba(148, 163, 184, 0.3)';
          e.target.style.background = 'transparent';
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
        <span style={{ fontSize: 'inherit' }}>
          {localIsFavorited ? '★' : '☆'}
        </span>
      )}
    </button>
  );
};

export default StarButton;