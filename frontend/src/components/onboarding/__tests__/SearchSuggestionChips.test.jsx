import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import SearchSuggestionChips from '../SearchSuggestionChips';

describe('SearchSuggestionChips', () => {
  it('renders suggestion chips', () => {
    render(<SearchSuggestionChips />);
    expect(screen.getByText('Refactor Python Code')).toBeInTheDocument();
    expect(screen.getByText('Write Unit Tests')).toBeInTheDocument();
    expect(screen.getByText('Email Drafting')).toBeInTheDocument();
  });

  it('calls onSuggestionClick when a chip is clicked', () => {
    const mockOnSuggestionClick = vi.fn();
    render(<SearchSuggestionChips onSuggestionClick={mockOnSuggestionClick} />);
    
    fireEvent.click(screen.getByText('Refactor Python Code'));
    expect(mockOnSuggestionClick).toHaveBeenCalledWith('refactor python code');
  });

  it('applies animated class when isFirstTime is true', () => {
    const { container } = render(<SearchSuggestionChips isFirstTime={true} />);
    expect(container.firstChild).toHaveClass('search-suggestions--animated');
  });

  it('renders the correct number of suggestion chips', () => {
    render(<SearchSuggestionChips />);
    const chips = screen.getAllByRole('button');
    expect(chips).toHaveLength(6);
  });
});