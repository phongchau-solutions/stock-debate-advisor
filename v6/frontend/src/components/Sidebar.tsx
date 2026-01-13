import React from 'react';
import { NavLink } from 'react-router-dom';

const navLinkBase =
  'flex items-center gap-3 rounded-lg px-4 py-2.5 text-sm font-medium transition-all duration-200';

export const Sidebar: React.FC = () => {
  return (
    <aside className="hidden w-64 border-r border-border/50 bg-muted/30 px-3 py-6 md:block overflow-y-auto">
      <nav className="flex flex-col gap-2 text-sm">
        <div className="px-1 py-2 mb-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Tools</p>
        </div>
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `${navLinkBase} ${
              isActive
                ? 'bg-gradient-primary text-white shadow-lg'
                : 'text-foreground hover:bg-white/50 dark:hover:bg-slate-800'
            }`
          }
        >
          <span className="fa-solid fa-chart-mixed text-base" aria-hidden="true" />
          <span>Dashboards</span>
        </NavLink>
        <NavLink
          to="/analysis"
          className={({ isActive }) =>
            `${navLinkBase} ${
              isActive
                ? 'bg-gradient-primary text-white shadow-lg'
                : 'text-foreground hover:bg-white/50 dark:hover:bg-slate-800'
            }`
          }
        >
          <span className="fa-solid fa-scale-balanced text-base" aria-hidden="true" />
          <span>Debate &amp; Analysis</span>
        </NavLink>
        <NavLink
          to="/financials"
          className={({ isActive }) =>
            `${navLinkBase} ${
              isActive
                ? 'bg-gradient-primary text-white shadow-lg'
                : 'text-foreground hover:bg-white/50 dark:hover:bg-slate-800'
            }`
          }
        >
          <span className="fa-solid fa-chart-line text-base" aria-hidden="true" />
          <span>Financials</span>
        </NavLink>
        <NavLink
          to="/stocks"
          className={({ isActive }) =>
            `${navLinkBase} ${
              isActive
                ? 'bg-gradient-primary text-white shadow-lg'
                : 'text-foreground hover:bg-white/50 dark:hover:bg-slate-800'
            }`
          }
        >
          <span className="fa-solid fa-coins text-base" aria-hidden="true" />
          <span>Stocks</span>
        </NavLink>
        <div className="px-1 py-2 mt-6 mb-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Library</p>
        </div>
        <NavLink
          to="/news"
          className={({ isActive }) =>
            `${navLinkBase} ${
              isActive
                ? 'bg-gradient-primary text-white shadow-lg'
                : 'text-foreground hover:bg-white/50 dark:hover:bg-slate-800'
            }`
          }
        >
          <span className="fa-solid fa-newspaper text-base" aria-hidden="true" />
          <span>News</span>
        </NavLink>
        <NavLink
          to="/watchlist"
          className={({ isActive }) =>
            `${navLinkBase} ${
              isActive
                ? 'bg-gradient-primary text-white shadow-lg'
                : 'text-foreground hover:bg-white/50 dark:hover:bg-slate-800'
            }`
          }
        >
          <span className="fa-solid fa-star text-base" aria-hidden="true" />
          <span>Watchlist</span>
        </NavLink>
      </nav>
    </aside>
  );
};


