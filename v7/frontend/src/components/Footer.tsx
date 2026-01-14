import React from 'react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-border/50 bg-gradient-to-b from-muted/50 to-muted/80 backdrop-blur-sm dark:from-slate-950/50 dark:to-slate-950/80">
      <div className="mx-auto flex max-w-[100rem] flex-col gap-6 px-3 py-6 md:px-3">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
          {/* Brand Section */}
          <div>
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-primary text-white font-bold text-sm">
                <span className="fa-solid fa-landmark" />
              </div>
              <span className="font-bold text-foreground">FinanceHub</span>
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed">
              AI-powered investment analysis platform using multi-agent debate technology for smarter financial decisions.
            </p>
            <div className="flex gap-3 mt-4">
              <a href="#" className="inline-flex items-center justify-center w-8 h-8 rounded-lg border border-border/30 text-muted-foreground hover:bg-muted hover:text-blue-950 dark:hover:text-blue-400 active:bg-muted/80 active:text-blue-900 dark:active:text-blue-300 disabled:text-gray-400 dark:disabled:text-gray-600 transition-colors" style={{ backgroundImage: 'none' }}>
                <span className="fa-brands fa-twitter text-sm" />
              </a>
              <a href="#" className="inline-flex items-center justify-center w-8 h-8 rounded-lg border border-border/30 text-muted-foreground hover:bg-muted hover:text-blue-950 dark:hover:text-blue-400 active:bg-muted/80 active:text-blue-900 dark:active:text-blue-300 disabled:text-gray-400 dark:disabled:text-gray-600 transition-colors" style={{ backgroundImage: 'none' }}>
                <span className="fa-brands fa-linkedin text-sm" />
              </a>
              <a href="#" className="inline-flex items-center justify-center w-8 h-8 rounded-lg border border-border/30 text-muted-foreground hover:bg-muted hover:text-blue-950 dark:hover:text-blue-400 active:bg-muted/80 active:text-blue-900 dark:active:text-blue-300 disabled:text-gray-400 dark:disabled:text-gray-600 transition-colors" style={{ backgroundImage: 'none' }}>
                <span className="fa-brands fa-github text-sm" />
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="font-semibold text-foreground text-sm mb-4 flex items-center gap-2">
              <span className="fa-solid fa-chart-line text-primary" />
              Product
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Features
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Enterprise
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Roadmap
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold text-foreground text-sm mb-4 flex items-center gap-2">
              <span className="fa-solid fa-book text-accent" />
              Resources
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Documentation
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  API Reference
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Blog
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Community
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal & Support */}
          <div>
            <h4 className="font-semibold text-foreground text-sm mb-4 flex items-center gap-2">
              <span className="fa-solid fa-shield text-success" />
              Support
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Contact Support
                </Link>
              </li>
              <li>
                <Link to="/" className="text-muted-foreground hover:text-primary transition-colors">
                  Status Page
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-border/30" />

        {/* Bottom Footer */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-xs text-muted-foreground">
            &copy; {new Date().getFullYear()} FinanceHub. All rights reserved.
          </p>
          <div className="flex gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <span className="fa-solid fa-circle-info text-primary/50" />
              Not investment advice. For education only.
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};


