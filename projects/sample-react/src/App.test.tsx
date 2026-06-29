import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import App from './App';

describe('App Component', () => {
  it('renders workspace title successfully', () => {
    render(<App />);
    const headingElements = screen.getAllByText(/DevForge Workspace/i);
    expect(headingElements.length).toBeGreaterThan(0);
  });

  it('defaults to showing the overview tab', () => {
    render(<App />);
    expect(screen.getByText(/Welcome to your/i)).toBeInTheDocument();
  });
});
