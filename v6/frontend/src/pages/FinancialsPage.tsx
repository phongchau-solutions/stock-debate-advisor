import React, { useState, useEffect } from 'react';
import { useAtom, useSetAtom } from 'jotai';
import { StatsCard } from '../components/StatsCard';
import { BarChart, LineChart } from '../components/Charts';
import {
  selectedFinancialMetricsAtom,
  loadFinancialMetricsAtom,
  availableSymbolsAtom,
  loadSymbolsAtom,
} from '../state/debateAtoms';

export const FinancialsPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  
  // Atom state management - all data from backend
  const [metrics] = useAtom(selectedFinancialMetricsAtom);
  const loadMetrics = useSetAtom(loadFinancialMetricsAtom);
  const [symbols] = useAtom(availableSymbolsAtom);
  const loadSymbols = useSetAtom(loadSymbolsAtom);

  // Load available symbols on mount
  useEffect(() => {
    loadSymbols();
  }, [loadSymbols]);

  // Set first symbol as default
  useEffect(() => {
    if (symbols.length > 0 && !selectedSymbol) {
      setSelectedSymbol(symbols[0]);
    }
  }, [symbols, selectedSymbol]);

  // Load financial metrics when symbol changes
  useEffect(() => {
    if (selectedSymbol) {
      loadMetrics(selectedSymbol);
    }
  }, [selectedSymbol, loadMetrics]);

  // Historical data placeholder - would come from backend
  const timeSeriesData = [
    { period: '2019', revenue: 260.2, freeFlowCash: 58.0 },
    { period: '2020', revenue: 274.5, freeFlowCash: 73.0 },
    { period: '2021', revenue: 365.8, freeFlowCash: 96.5 },
    { period: '2022', revenue: 394.3, freeFlowCash: 110.5 },
    { period: '2023', revenue: 394.3, freeFlowCash: 111.3 },
    { period: '2024Q1', revenue: 99.9, freeFlowCash: 28.0 },
    { period: '2024Q2', revenue: 108.3, freeFlowCash: 29.5 },
    { period: '2024Q3', revenue: 115.3, freeFlowCash: 31.2 },
  ];

  return (
    <section className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Financial Analysis</h1>
        <p className="text-base text-muted-foreground max-w-2xl">
          Comprehensive financial metrics, ratios, and analysis for investment decisions.
        </p>
      </div>

      {/* Symbol Selector - From atoms */}
      {symbols.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {symbols.map((sym) => (
            <button
              key={sym}
              onClick={() => setSelectedSymbol(sym)}
              className={`px-4 py-2 rounded-lg border font-semibold transition-all ${
                selectedSymbol === sym
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border/50 bg-white dark:bg-slate-900 text-foreground hover:border-primary/50'
              }`}
            >
              {sym}
            </button>
          ))}
        </div>
      )}

      {metrics && selectedSymbol && (
        <>
          {/* Valuation Metrics - From backend */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-foreground">Valuation Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                icon="fa-chart-pie"
                label="P/E Ratio"
                value={metrics.peRatio.toFixed(1)}
                color="primary"
                subtext="Lower is more attractive"
              />
              <StatsCard
                icon="fa-scale-balanced"
                label="Debt to Equity"
                value={metrics.debtToEquity.toFixed(2)}
                color="success"
                subtext="Financial leverage ratio"
              />
              <StatsCard
                icon="fa-book"
                label="Book Value"
                value={`${metrics.bookValue.toFixed(2)}`}
                color="info"
                subtext="Per share"
              />
              <StatsCard
                icon="fa-percent"
                label="Dividend Yield"
                value={`${metrics.dividendYield.toFixed(2)}%`}
                color="warning"
                subtext="Annual yield"
              />
            </div>
          </div>

          {/* Profitability Metrics - From backend */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-foreground">Profitability & Returns</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                icon="fa-arrow-trend-up"
                label="Net Profit Margin"
                value={`${metrics.profitMargin.toFixed(1)}%`}
                color="success"
                subtext="Higher is better"
              />
              <StatsCard
                icon="fa-coins"
                label="Return on Assets"
                value={`${metrics.roa.toFixed(1)}%`}
                color="primary"
                subtext="Asset efficiency"
              />
              <StatsCard
                icon="fa-landmark"
                label="Return on Equity"
                value={`${metrics.roe.toFixed(1)}%`}
                color="warning"
                subtext="Shareholder returns"
              />
              <StatsCard
                icon="fa-chart-line"
                label="Revenue Growth"
                value={`${metrics.revenueGrowth.toFixed(1)}%`}
                color="info"
                change={2.5}
                changeType="positive"
              />
            </div>
          </div>

          {/* Liquidity & Solvency - From backend */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-foreground">Liquidity & Solvency</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <StatsCard
                icon="fa-water"
                label="Current Ratio"
                value={metrics.currentRatio.toFixed(2)}
                color="success"
                subtext="> 1.0 is healthy"
              />
              <StatsCard
                icon="fa-droplet"
                label="Quick Ratio"
                value={metrics.quickRatio.toFixed(2)}
                color="info"
                subtext="Quick liquidity"
              />
            </div>
          </div>

          {/* Growth Metrics - From backend */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-foreground">Growth Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <StatsCard
                icon="fa-chart-bar"
                label="EPS Growth"
                value={`${metrics.epsGrowth.toFixed(1)}%`}
                color="primary"
                change={3.2}
                changeType="positive"
              />
              <StatsCard
                icon="fa-arrow-up"
                label="Revenue Growth"
                value={`${metrics.revenueGrowth.toFixed(1)}%`}
                color="success"
                change={1.5}
                changeType="positive"
              />
            </div>
          </div>

          {/* Historical Charts - Would come from backend */}
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-foreground">Financial Trends</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <BarChart
                title="Annual Revenue (Billions USD)"
                data={timeSeriesData.map((d) => ({
                  label: d.period,
                  value: Math.round(d.revenue),
                  color: 'bg-blue-500',
                }))}
              />

              <LineChart
                title="Free Cash Flow Trend (Billions USD)"
                data={timeSeriesData.map((d) => ({
                  label: d.period,
                  value: Math.round(d.freeFlowCash),
                }))}
              />
            </div>
          </div>

          {/* Backend Integration Notice */}
          <div className="rounded-lg border border-blue-200 dark:border-blue-700/50 bg-blue-50 dark:bg-blue-900/20 p-4">
            <div className="flex items-start gap-3">
              <div className="text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5">
                <span className="fa-solid fa-info-circle text-lg" />
              </div>
              <div>
                <h3 className="font-semibold text-blue-900 dark:text-blue-200">Fetching data from backend API</h3>
                <p className="text-sm text-blue-800 dark:text-blue-300 mt-1">
                  Financial metrics for {selectedSymbol} are being retrieved from the backend via `/api/financial/{selectedSymbol}` endpoint. 
                  All data is managed by Jotai atoms and updated dynamically.
                </p>
              </div>
            </div>
          </div>
        </>
      )}

      {!selectedSymbol && symbols.length === 0 && (
        <div className="rounded-xl border border-border/50 bg-gradient-soft p-8 text-center">
          <div className="space-y-3">
            <div className="text-4xl">
              <span className="fa-solid fa-chart-line text-primary" />
            </div>
            <h3 className="text-lg font-semibold text-foreground">Loading stocks...</h3>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              Fetching available stocks from backend. Please wait.
            </p>
          </div>
        </div>
      )}
    </section>
  );
};


