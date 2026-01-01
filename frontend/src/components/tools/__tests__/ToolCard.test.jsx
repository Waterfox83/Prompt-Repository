import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ToolCard from '../ToolCard';

// Mock the ToolMetadataService
vi.mock('../../../services/ToolMetadataService', () => ({
  default: {
    getToolByDisplayName: vi.fn((toolName) => ({
      id: 'chatgpt',
      displayName: 'ChatGPT',
      description: 'OpenAI\'s conversational AI for general-purpose text generation and problem-solving',
      detailedDescription: 'ChatGPT is a versatile AI assistant that excels at writing, coding, analysis, and creative tasks.',
      category: 'coding',
      accessUrl: 'https://chat.openai.com',
      useCases: ['Code review and debugging', 'Writing documentation', 'Explaining complex algorithms'],
      isFallback: false
    })),
    getCategoryInfo: vi.fn(() => ({
      name: 'Coding & Development',
      description: 'AI tools for software development',
      icon: '💻'
    })),
    createFallbackTool: vi.fn((toolName) => ({
      id: toolName.toLowerCase(),
      displayName: toolName,
      description: `AI tool: ${toolName}`,
      category: 'coding',
      icon: '🤖',
      accessUrl: '#',
      useCases: ['General AI assistance'],
      isFallback: true
    }))
  }
}));

describe('ToolCard', () => {
  const mockProps = {
    toolName: 'ChatGPT',
    onViewPrompts: vi.fn(),
    onClose: vi.fn(),
    promptCount: 5
  };

  it('renders tool information correctly', () => {
    render(<ToolCard {...mockProps} />);
    
    expect(screen.getByText('ChatGPT')).toBeInTheDocument();
    expect(screen.getByText(/ChatGPT is a versatile AI assistant/)).toBeInTheDocument();
    expect(screen.getByText('Coding & Development')).toBeInTheDocument();
    expect(screen.getByText('5 prompts available')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    render(<ToolCard {...mockProps} />);
    
    const closeButton = screen.getByLabelText('Close tool information');
    fireEvent.click(closeButton);
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('calls onViewPrompts when view all prompts button is clicked', () => {
    render(<ToolCard {...mockProps} />);
    
    const viewPromptsButton = screen.getByText(/View All Prompts/);
    fireEvent.click(viewPromptsButton);
    
    expect(mockProps.onViewPrompts).toHaveBeenCalledWith('ChatGPT');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('opens official website when visit website button is clicked', () => {
    // Mock window.open
    const mockOpen = vi.fn();
    global.window.open = mockOpen;
    
    render(<ToolCard {...mockProps} />);
    
    const visitWebsiteButton = screen.getByText('Visit Official Website');
    fireEvent.click(visitWebsiteButton);
    
    expect(mockOpen).toHaveBeenCalledWith('https://chat.openai.com', '_blank', 'noopener,noreferrer');
  });

  it('handles escape key to close modal', () => {
    render(<ToolCard {...mockProps} />);
    
    fireEvent.keyDown(document, { key: 'Escape' });
    
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('displays use cases correctly', () => {
    render(<ToolCard {...mockProps} />);
    
    expect(screen.getByText('Code review and debugging')).toBeInTheDocument();
    expect(screen.getByText('Writing documentation')).toBeInTheDocument();
    expect(screen.getByText('Explaining complex algorithms')).toBeInTheDocument();
  });

  it('handles zero prompt count correctly', () => {
    const propsWithZeroPrompts = { ...mockProps, promptCount: 0 };
    render(<ToolCard {...propsWithZeroPrompts} />);
    
    expect(screen.queryByText(/View All Prompts/)).not.toBeInTheDocument();
    expect(screen.queryByText(/prompts available/)).not.toBeInTheDocument();
  });
});