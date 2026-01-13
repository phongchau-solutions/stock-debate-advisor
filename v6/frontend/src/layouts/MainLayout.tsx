import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { Sidebar } from '../components/Sidebar';
import { MD3Navbar } from '../components/md3/MD3Navbar';
import { MD3CollapsibleMenu } from '../components/md3/MD3CollapsibleMenu';

export const MainLayout: React.FC = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  const navItems = [
    { label: 'Dashboard', icon: 'fa-chart-pie', path: '/dashboard' },
    { label: 'Multi-Agent Debate', icon: 'fa-comments', path: '/analysis' },
    { label: 'Financials', icon: 'fa-building-columns', path: '/financials' },
    { label: 'Stocks', icon: 'fa-chart-line', path: '/stocks' },
    { label: 'News', icon: 'fa-newspaper', path: '/news' },
    { label: 'Watchlist', icon: 'fa-star', path: '/watchlist' },
  ];

  const menuItems = [
    { label: 'Dashboard', icon: 'fa-chart-pie', onClick: () => { navigate('/dashboard'); setMenuOpen(false); } },
    { label: 'Analysis', icon: 'fa-comments', onClick: () => { navigate('/analysis'); setMenuOpen(false); } },
    { label: 'Market Data', icon: 'fa-chart-line', children: [
      { label: 'Financials', icon: 'fa-building-columns', onClick: () => { navigate('/financials'); setMenuOpen(false); } },
      { label: 'Stocks', icon: 'fa-share-nodes', onClick: () => { navigate('/stocks'); setMenuOpen(false); } },
      { label: 'News', icon: 'fa-newspaper', onClick: () => { navigate('/news'); setMenuOpen(false); } },
    ]},
    { label: 'Watchlist', icon: 'fa-star', onClick: () => { navigate('/watchlist'); setMenuOpen(false); } },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-background text-foreground dark:bg-slate-950">
      {/* Material Design 3 Navbar */}
      <MD3Navbar 
        items={navItems}
        title="Stock Debate Advisor"
        onMenuToggle={setMenuOpen}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* MD3 Collapsible Menu */}
        {menuOpen && (
          <MD3CollapsibleMenu 
            items={menuItems}
            isOpen={menuOpen}
            onClose={() => setMenuOpen(false)}
          />
        )}

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto px-4 py-6 md:px-8 lg:px-12 bg-gradient-to-br from-background/50 via-transparent to-transparent dark:from-slate-950/50">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
};


