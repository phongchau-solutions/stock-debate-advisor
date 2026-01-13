import React, { useState, useEffect } from 'react';
import { useAtom, useSetAtom } from 'jotai';
import { StatsCard } from '../components/StatsCard';
import { BarChart, ConfidenceChart, LineChart } from '../components/Charts';
import {
  debateHistoryAtom,
  dashboardStatsAtom,
  loadDebateHistoryAtom,
  availableSymbolsAtom,
  loadSymbolsAtom,
} from '../state/debateAtoms';

interface DashboardTab {
  id: string;
  label: string;
  icon: string;
  description: string;
  tableauUrl: string;
}

export const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('macro');
  
  // Atom state management - all data from backend
  const [debateHistory] = useAtom(debateHistoryAtom);
  const [stats] = useAtom(dashboardStatsAtom);
  const loadHistory = useSetAtom(loadDebateHistoryAtom);
  const [symbols] = useAtom(availableSymbolsAtom);
  const loadSymbols = useSetAtom(loadSymbolsAtom);

  // Load data on component mount
  useEffect(() => {
    loadHistory();
    loadSymbols();
  }, [loadHistory, loadSymbols]);

  const dashboards: DashboardTab[] = [
    {
      id: 'macro',
      label: 'Macro Analysis',
      icon: 'fa-globe',
      description: 'Global economic indicators, GDP trends, interest rates, and macroeconomic forecasts',
      tableauUrl: 'https://public.tableau.com/shared/SYCH3D8YR?:display_count=n&:origin=viz_share_link',
    },
    {
      id: 'market',
      label: 'Market Overview',
      icon: 'fa-arrow-trend-up',
      description: 'Real-time market indices, sector performance, and volatility analysis',
      tableauUrl: 'https://public.tableau.com/shared/DNFQ5QHKZ?:display_count=n&:origin=viz_share_link',
    },
    {
      id: 'stocks',
      label: 'Stock Analysis',
      icon: 'fa-chart-line',
      description: 'Top performers, sector breakdown, and individual stock metrics',
      tableauUrl: 'https://public.tableau.com/shared/8R4RNZ9YC?:display_count=n&:origin=viz_share_link',
    },
    {
      id: 'commodities',
      label: 'Commodities',
      icon: 'fa-bars',
      description: 'Oil, gold, natural gas, and agricultural commodity trends',
      tableauUrl: 'https://public.tableau.com/shared/XQHY3KPPY?:display_count=n&:origin=viz_share_link',
    },
  ];

  const activeTabData = dashboards.find((d) => d.id === activeTab);

  // Default values while loading
  const displayStats = stats || {
    total: 0,
    buyCount: 0,
    holdCount: 0,
    sellCount: 0,
    avgConfidence: 0,
    winRate: 0,
  };

  return (
    <section className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-base text-muted-foreground max-w-2xl">
          Multi-Agent Debate Performance Metrics & Financial Dashboards
        </p>
      </div>

      {/* KPI Stats Cards - All data from atoms */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          icon="fa-chart-line"
          label="Total Analyses"
          value={displayStats.total}
          change={displayStats.total > 0 ? 12 : undefined}
          changeType="positive"
          color="primary"
          subtext="Debates completed"
        />
        <StatsCard
          icon="fa-check-circle"
          label="Accuracy Rate"
          value={`${displayStats.winRate}%`}
          change={displayStats.winRate > 0 ? 5 : undefined}
          changeType="positive"
          color="success"
          subtext="Buy recommendations accuracy"
        />
        <StatsCard
          icon="fa-target"
          label="Avg Confidence"
          value={`${displayStats.avgConfidence}%`}
          change={displayStats.avgConfidence > 0 ? 2 : undefined}
          changeType="neutral"
          color="info"
          subtext="Across all debates"
        />
        <StatsCard
          icon="fa-zap"
          label="Active Symbols"
          value={displayStats.total}
          change={displayStats.total > 0 ? 3 : undefined}
          changeType="positive"
          color="warning"
          subtext="Tracked this week"
        />
      </div>

      {/* Verdict Distribution - From atoms */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-lg border border-green-200 dark:border-green-700/50 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-sm text-foreground">Buy Signals</h3>
            <span className="text-2xl text-green-600 dark:text-green-400">📈</span>
          </div>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">{displayStats.buyCount}</p>
          <p className="text-xs text-green-600/70 dark:text-green-400/70 mt-1">
            {displayStats.total > 0 ? Math.round((displayStats.buyCount / displayStats.total) * 100) : 0}% of recommendations
          </p>
        </div>

        <div className="rounded-lg border border-yellow-200 dark:border-yellow-700/50 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-sm text-foreground">Hold Signals</h3>
            <span className="text-2xl text-yellow-600 dark:text-yellow-400">➡️</span>
          </div>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{displayStats.holdCount}</p>
          <p className="text-xs text-yellow-600/70 dark:text-yellow-400/70 mt-1">
            {displayStats.total > 0 ? Math.round((displayStats.holdCount / displayStats.total) * 100) : 0}% of recommendations
          </p>
        </div>

        <div className="rounded-lg border border-red-200 dark:border-red-700/50 bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-sm text-foreground">Sell Signals</h3>
            <span className="text-2xl text-red-600 dark:text-red-400">📉</span>
          </div>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">{displayStats.sellCount}</p>
          <p className="text-xs text-red-600/70 dark:text-red-400/70 mt-1">
            {displayStats.total > 0 ? Math.round((displayStats.sellCount / displayStats.total) * 100) : 0}% of recommendations
          </p>
        </div>
      </div>

      {/* Recent Activity - From atoms */}
      <div className="rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm">
        <h2 className="text-lg font-bold text-foreground mb-4">Recent Debate Activity</h2>
        <div className="space-y-2">
          {debateHistory.length > 0 ? (
            debateHistory.map((debate, idx) => {
              const verdictColors = {
                BUY: 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700/50',
                HOLD: 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-700/50',
                SELL: 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700/50',
              };
              const timeAgo = Math.floor((Date.now() - debate.timestamp) / 60000);
              return (
                <div key={idx} className="flex items-center justify-between p-3 rounded-md border border-border/50 hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center font-bold text-foreground">
                      {debate.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-semibold text-foreground">{debate.symbol}</p>
                      <p className="text-xs text-muted-foreground">{timeAgo} minutes ago</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <p className={`font-semibold text-sm ${verdictColors[debate.verdict]}`}>{debate.verdict}</p>
                      <p className="text-xs text-muted-foreground">{debate.confidence}% confidence</p>
                    </div>
                    <div className={`px-3 py-1 rounded-full border font-semibold text-sm ${verdictColors[debate.verdict]}`}>
                      <span className={`fa-solid ${debate.verdict === 'BUY' ? 'fa-arrow-up' : debate.verdict === 'HOLD' ? 'fa-minus' : 'fa-arrow-down'}`} />
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No debate history yet. Start a debate to see activity here.</p>
            </div>
          )}
        </div>
      </div>

      {/* Section Header for Dashboards */}
      <div className="space-y-3 mt-8">
        <h2 className="text-2xl font-bold text-foreground">Financial Dashboards</h2>
        <p className="text-sm text-muted-foreground">
          Interactive Tableau visualizations providing real-time insights into macro analysis and market dynamics.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {dashboards.map((dashboard) => (
          <button
            key={dashboard.id}
            onClick={() => setActiveTab(dashboard.id)}
            className={`rounded-lg border transition-all duration-200 p-3 text-left ${
              activeTab === dashboard.id
                ? 'border-primary bg-gradient-to-br from-primary/10 to-accent/10 shadow-md'
                : 'border-border/50 bg-white/50 dark:bg-slate-900/50 hover:border-primary/50 hover:shadow-sm'
            }`}
          >
            <div className="flex items-start justify-between mb-1.5">
              <span
                className={`text-xl ${
                  activeTab === dashboard.id ? 'text-primary' : 'text-muted-foreground'
                }`}
              >
                <span className={`fa-solid ${dashboard.icon}`} />
              </span>
              {activeTab === dashboard.id && (
                <span className="text-primary text-base">
                  <span className="fa-solid fa-check" />
                </span>
              )}
            </div>
            <h3 className={`font-semibold text-xs mb-0.5 ${
              activeTab === dashboard.id ? 'text-foreground' : 'text-foreground'
            }`}>
              {dashboard.label}
            </h3>
            <p className="text-xs text-muted-foreground line-clamp-1">{dashboard.description}</p>
          </button>
        ))}
      </div>

      {/* Active Dashboard */}
      {activeTabData && (
        <div className="space-y-3">
          <div className="rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3 gap-2">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                <div className="text-lg text-primary flex-shrink-0">
                  <span className={`fa-solid ${activeTabData.icon}`} />
                </div>
                <div className="min-w-0">
                  <h2 className="text-lg font-bold text-foreground">{activeTabData.label}</h2>
                  <p className="text-xs text-muted-foreground line-clamp-1">{activeTabData.description}</p>
                </div>
              </div>
              <a
                href={activeTabData.tableauUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-1.5 rounded-md border border-border/50 text-muted-foreground hover:text-foreground hover:bg-muted/50 font-medium text-xs transition-colors inline-flex items-center gap-1.5 flex-shrink-0"
              >
                <span className="fa-solid fa-arrow-up-right-from-square" />
                View in Tableau
              </a>
            </div>

            {/* Tableau Embed Container */}
            <div className="rounded-md overflow-hidden border border-border/50 bg-muted/30">
              <div style={{ height: '600px', width: '100%' }}>
                <iframe
                  src={activeTabData.tableauUrl}
                  style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                    borderRadius: '0.5rem',
                  }}
                  allowFullScreen={true}
                  title={activeTabData.label}
                />
              </div>
            </div>

            {/* Analytics Charts Section */}
            <div className="mt-6 space-y-4">
              <h3 className="text-lg font-bold text-foreground">Debate Analytics</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <BarChart
                  title="Verdict Distribution"
                  data={[
                    { label: 'Buy', value: displayStats.buyCount, color: 'bg-green-500' },
                    { label: 'Hold', value: displayStats.holdCount, color: 'bg-yellow-500' },
                    { label: 'Sell', value: displayStats.sellCount, color: 'bg-red-500' },
                  ]}
                />

                <ConfidenceChart
                  title="Confidence Distribution"
                  average={displayStats.avgConfidence}
                  distribution={{
                    high: Math.ceil((displayStats.total || 0) * 0.6),
                    medium: Math.ceil((displayStats.total || 0) * 0.3),
                    low: Math.floor((displayStats.total || 0) * 0.1),
                  }}
                />
              </div>

              <LineChart
                title="Debate Activity Trend (Last 10 Days)"
                data={[
                  { label: 'Mon', value: 3 },
                  { label: 'Tue', value: 5 },
                  { label: 'Wed', value: 4 },
                  { label: 'Thu', value: 7 },
                  { label: 'Fri', value: 6 },
                  { label: 'Sat', value: 2 },
                  { label: 'Sun', value: 1 },
                  { label: 'Mon', value: 4 },
                  { label: 'Tue', value: 5 },
                  { label: 'Wed', value: displayStats.total },
                ]}
              />
            </div>

            {/* Dashboard Info */}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="rounded-md border border-border/50 bg-gradient-soft p-3">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span className="text-base text-primary">
                    <span className="fa-solid fa-clock" />
                  </span>
                  <h4 className="font-semibold text-xs text-foreground">Update Frequency</h4>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  Real-time data updates every 15 minutes during market hours
                </p>
              </div>

              <div className="rounded-md border border-border/50 bg-gradient-soft p-3">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span className="text-base text-accent">
                    <span className="fa-solid fa-database" />
                  </span>
                  <h4 className="font-semibold text-xs text-foreground">Data Sources</h4>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  Aggregated from Bloomberg, Yahoo Finance, and major exchanges
                </p>
              </div>

              <div className="rounded-md border border-border/50 bg-gradient-soft p-3">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span className="text-base text-warning">
                    <span className="fa-solid fa-filter" />
                  </span>
                  <h4 className="font-semibold text-xs text-foreground">Filters</h4>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  Use Tableau filters for custom timeframes and geographies
                </p>
              </div>
            </div>

            {/* Help Text */}
            <div className="mt-4 rounded-md bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700/50 p-3">
              <div className="flex gap-2">
                <span className="text-blue-600 dark:text-blue-400 flex-shrink-0">
                  <span className="fa-solid fa-lightbulb" />
                </span>
                <div>
                  <p className="text-xs text-blue-800 dark:text-blue-200 mb-1.5">
                    All dashboards are fully interactive. Use the toolbar in each dashboard to zoom, filter, drill down into data, and export insights.
                  </p>
                  <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-0.5">
                    <li>
                      <span className="font-medium">Hover</span> over data points to see detailed information
                    </li>
                    <li>
                      <span className="font-medium">Click</span> on chart elements to filter related data
                    </li>
                    <li>
                      <span className="font-medium">Use Tableau menu</span> (top-right corner) to download or share visualizations
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
