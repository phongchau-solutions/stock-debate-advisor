import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import MD3Navbar from '../../components/md3/MD3Navbar';

const mockNavItems = [
  { label: 'Dashboard', icon: 'fa-chart-line', path: '/dashboard', badge: 2 },
  { label: 'Analysis', icon: 'fa-scale-balanced', path: '/analysis' },
  { label: 'Settings', icon: 'fa-cog', path: '/settings' },
];

describe('MD3Navbar', () => {
  it('should render navbar with title', () => {
    render(
      <BrowserRouter>
        <MD3Navbar items={mockNavItems} title="Financial Dashboard" />
      </BrowserRouter>
    );

    expect(screen.getByText('Financial Dashboard')).toBeInTheDocument();
  });

  it('should render all nav items', () => {
    render(
      <BrowserRouter>
        <MD3Navbar items={mockNavItems} title="Dashboard" />
      </BrowserRouter>
    );

    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Analysis')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('should display badge if present', () => {
    render(
      <BrowserRouter>
        <MD3Navbar items={mockNavItems} title="Dashboard" />
      </BrowserRouter>
    );

    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('should call onMenuToggle when menu button is clicked', () => {
    const handleMenuToggle = jest.fn();
    render(
      <BrowserRouter>
        <MD3Navbar items={mockNavItems} title="Dashboard" onMenuToggle={handleMenuToggle} />
      </BrowserRouter>
    );

    const menuButton = screen.getByTitle('Toggle menu');
    fireEvent.click(menuButton);

    expect(handleMenuToggle).toHaveBeenCalledWith(true);
  });

  it('should have proper navigation links', () => {
    render(
      <BrowserRouter>
        <MD3Navbar items={mockNavItems} title="Dashboard" />
      </BrowserRouter>
    );

    const links = screen.getAllByRole('link');
    expect(links).toHaveLength(mockNavItems.length);
    expect(links[0]).toHaveAttribute('href', '/dashboard');
  });
});
