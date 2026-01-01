import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HeroMissionStatement from '../HeroMissionStatement';

describe('HeroMissionStatement', () => {
  it('renders the mission statement title', () => {
    render(<HeroMissionStatement />);
    expect(screen.getByText('Discover AI Prompts That Actually Work')).toBeInTheDocument();
  });

  it('renders the mission statement subtitle', () => {
    render(<HeroMissionStatement />);
    expect(screen.getByText(/Find proven prompts for ChatGPT, Claude/)).toBeInTheDocument();
  });

  it('applies animated class when isFirstTime is true', () => {
    const { container } = render(<HeroMissionStatement isFirstTime={true} />);
    expect(container.firstChild).toHaveClass('hero-mission--animated');
  });

  it('does not apply animated class when isFirstTime is false', () => {
    const { container } = render(<HeroMissionStatement isFirstTime={false} />);
    expect(container.firstChild).not.toHaveClass('hero-mission--animated');
  });
});