import React from 'react';
import './SearchSuggestionChips.css';

const SearchSuggestionChips = ({ onSuggestionClick, isFirstTime = false }) => {
  const suggestions = [
    { label: 'Refactor Python Code', query: 'refactor python code', category: 'coding' },
    { label: 'Write Unit Tests', query: 'write unit tests', category: 'coding' },
    { label: 'Review Kotlin code', query: 'kotlin code review', category: 'writing' },
    { label: 'Debug JavaScript', query: 'debug javascript errors', category: 'coding' },
    { label: 'Generate Documentation', query: 'generate documentation', category: 'coding' }
  ];

  const handleChipClick = (suggestion) => {
    if (onSuggestionClick) {
      onSuggestionClick(suggestion.query);
    }
  };

  return (
    <div className={`search-suggestions ${isFirstTime ? 'search-suggestions--animated' : ''}`}>
      <span className="search-suggestions__label">Try searching for:</span>
      <div className="search-suggestions__chips">
        {suggestions.map((suggestion, index) => (
          <button
            key={suggestion.query}
            className={`search-chip search-chip--${suggestion.category}`}
            onClick={() => handleChipClick(suggestion)}
            style={{
              animationDelay: isFirstTime ? `${0.1 * index}s` : '0s'
            }}
          >
            {suggestion.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SearchSuggestionChips;