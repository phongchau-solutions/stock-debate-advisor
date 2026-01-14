import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

interface Stock {
  symbol: string;
  name: string;
  price?: number;
  change?: number;
  changePercent?: string;
  sector?: string;
}

export const StocksPage: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get<{ symbols: string[] }>('/companies');
        
        // Map the symbols to stock data (will fetch additional info later if needed)
        const stocksList: Stock[] = (response.symbols || []).map(symbol => ({
          symbol,
          name: symbol, // Will be populated with actual company names
          changePercent: '0%',
        }));
        
        setStocks(stocksList);
        setError(null);
      } catch (err) {
        setError('Failed to load stocks. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, []);

  const filteredStocks = stocks.filter(stock =>
    stock.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
    stock.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <section className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Stock Screener</h1>
        <p className="text-base text-muted-foreground max-w-2xl">
          Search, filter, and explore the equities universe. Select any stock to run a multi-agent debate analysis.
        </p>
      </div>

      <div className="rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm">
        <div className="flex items-center gap-2 mb-3">
          <input
            type="text"
            placeholder="Search ticker or company name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 rounded-md border border-border bg-muted/50 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 dark:focus:ring-offset-slate-900"
          />
          <button className="inline-flex items-center gap-2 rounded-md bg-primary text-white px-3 py-2 text-sm font-medium hover:bg-primary/90 transition-colors">
            <span className="fa-solid fa-magnifying-glass" />
            <span>Search</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-destructive">
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">
          VN30 Stocks {loading && <span className="text-xs text-muted-foreground">(Loading...)</span>}
        </h2>
        {loading ? (
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm animate-pulse">
                <div className="h-5 bg-muted rounded w-16 mb-2" />
                <div className="h-3 bg-muted rounded w-32 mb-4" />
                <div className="space-y-2">
                  <div className="h-3 bg-muted rounded" />
                  <div className="h-3 bg-muted rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {filteredStocks.map((stock) => (
              <div 
                key={stock.symbol} 
                className="group rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm hover:shadow-md hover:border-primary/30 transition-all duration-300 cursor-pointer"
                onClick={() => window.location.href = `/analysis?symbol=${stock.symbol}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="min-w-0">
                    <h3 className="font-bold text-foreground text-base">{stock.symbol}</h3>
                    <p className="text-xs text-muted-foreground truncate">{stock.name}</p>
                  </div>
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full flex-shrink-0 ${
                    stock.changePercent?.startsWith('+') || stock.changePercent === '0%'
                      ? 'bg-success/10 text-success' 
                      : 'bg-destructive/10 text-destructive'
                  }`}>
                    {stock.changePercent}
                  </span>
                </div>
                <div className="space-y-1.5 pt-2 border-t border-border/30">
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Price</span>
                    <span className="font-semibold text-foreground">{stock.price ? `₫${stock.price.toFixed(2)}` : 'N/A'}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-muted-foreground">Change</span>
                    <span className="font-semibold text-foreground">{stock.changePercent}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="rounded-xl border border-border/50 bg-gradient-soft p-8 text-center">
        <div className="space-y-3">
          <div className="text-4xl">
            <i className="fa-solid fa-arrow-trend-up text-success"></i>
          </div>
          <h3 className="text-lg font-semibold text-foreground">Advanced Screening</h3>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            Premium screening filters by P/E ratio, market cap, dividend yield, and more coming soon.
          </p>
        </div>
      </div>
    </section>
  );
};


