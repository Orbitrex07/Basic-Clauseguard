import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DisclaimerBanner } from '../components/DisclaimerBanner';
import { RiskBadge } from '../components/RiskBadge';
import { CategoryBadge } from '../components/CategoryBadge';
import { LandingPage } from '../pages/LandingPage';
import { LoginPage } from '../pages/LoginPage';
import { AuthProvider } from '../context/AuthContext';

describe('ClauseGuard Frontend Component Suite', () => {
  it('renders visible legal disclaimer banner', () => {
    render(<DisclaimerBanner />);
    expect(screen.getByText(/This tool is informational and is not legal advice/i)).toBeInTheDocument();
  });

  it('renders multi-channel risk badges accurately', () => {
    const { rerender } = render(<RiskBadge level="High" score={85} showScore />);
    expect(screen.getByText('High Risk')).toBeInTheDocument();
    expect(screen.getByText('(85/100)')).toBeInTheDocument();

    rerender(<RiskBadge level="Low" score={10} showScore />);
    expect(screen.getByText('Low Risk')).toBeInTheDocument();
    expect(screen.getByText('(10/100)')).toBeInTheDocument();
  });

  it('renders canonical category badge', () => {
    render(<CategoryBadge category="Termination" />);
    expect(screen.getByText('Termination')).toBeInTheDocument();
  });

  it('renders landing page hero and calls to action', () => {
    render(
      <BrowserRouter>
        <LandingPage />
      </BrowserRouter>
    );
    expect(screen.getByText(/Understand your contract/i)).toBeInTheDocument();
    expect(screen.getByText(/Analyze a Contract/i)).toBeInTheDocument();
  });

  it('renders sign in form with admin demo fill option', () => {
    render(
      <AuthProvider>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </AuthProvider>
    );
    expect(screen.getByText('Welcome back')).toBeInTheDocument();
    expect(screen.getByText('Fill Admin Credentials')).toBeInTheDocument();
  });
});
