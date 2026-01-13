import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTheme } from '../hooks/useTheme';

export const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [showAccountMenu, setShowAccountMenu] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-border/50 bg-white/95 backdrop-blur-xl dark:bg-slate-950/95">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 md:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-primary rounded-lg opacity-75 group-hover:opacity-100 blur transition-all" />
            <div className="relative inline-flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-primary text-white font-bold text-lg">
              <span className="fa-solid fa-landmark" />
            </div>
          </div>
          <div className="flex flex-col">
            <span className="font-bold text-lg tracking-tight text-foreground">FinanceHub</span>
            <span className="text-xs text-muted-foreground font-medium">AI Investment Analysis</span>
          </div>
        </Link>

        {/* Right actions */}
        <div className="flex items-center gap-2 md:gap-4">
          {/* Theme Toggle */}
          <button
            type="button"
            onClick={toggleTheme}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-border/30 bg-muted/40 p-2 md:px-3 md:py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:ring-offset-2 dark:focus:ring-offset-slate-950"
            aria-label="Toggle theme"
            title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
          >
            <span
              className={`text-base ${theme === 'dark' ? 'fa-solid fa-moon text-warning' : 'fa-solid fa-sun text-warning'}`}
              aria-hidden="true"
            />
            <span className="hidden md:inline">{theme === 'dark' ? 'Dark' : 'Light'}</span>
          </button>

          {/* Notifications */}
          <button
            type="button"
            className="relative inline-flex items-center justify-center p-2 rounded-lg border border-border/30 bg-muted/40 hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:ring-offset-2 dark:focus:ring-offset-slate-950"
            aria-label="Notifications"
            title="Notifications"
          >
            <span className="fa-solid fa-bell text-base text-foreground" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-warning rounded-full" />
          </button>

          {/* Account/Settings Dropdown */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowAccountMenu(!showAccountMenu)}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-border/30 bg-muted/40 p-2 hover:bg-muted transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:ring-offset-2 dark:focus:ring-offset-slate-950"
              aria-label="Account menu"
              title="Account settings"
            >
              <span className="fa-solid fa-circle-user text-base text-foreground" />
              <span className="hidden sm:inline text-sm font-medium">Account</span>
            </button>

            {/* Dropdown Menu */}
            {showAccountMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-slate-900 rounded-lg border border-border/50 shadow-lg z-50">
                <div className="p-3 border-b border-border/30">
                  <p className="text-sm font-semibold text-foreground">John Doe</p>
                  <p className="text-xs text-muted-foreground">john@example.com</p>
                </div>
                <div className="space-y-1 p-2">
                  <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-foreground hover:bg-muted transition-colors flex items-center gap-2">
                    <span className="fa-solid fa-user text-primary" />
                    <span>Profile</span>
                  </button>
                  <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-foreground hover:bg-muted transition-colors flex items-center gap-2">
                    <span className="fa-solid fa-sliders text-primary" />
                    <span>Settings</span>
                  </button>
                  <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-foreground hover:bg-muted transition-colors flex items-center gap-2">
                    <span className="fa-solid fa-key text-primary" />
                    <span>API Keys</span>
                  </button>
                  <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-foreground hover:bg-muted transition-colors flex items-center gap-2">
                    <span className="fa-solid fa-book text-primary" />
                    <span>Documentation</span>
                  </button>
                </div>
                <div className="border-t border-border/30 p-2">
                  <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-destructive hover:bg-destructive/10 transition-colors flex items-center gap-2">
                    <span className="fa-solid fa-sign-out-alt" />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};


