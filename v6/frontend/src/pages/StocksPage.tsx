import React from 'react';

export const StocksPage: React.FC = () => {
  const popularStocks = [
    { symbol: 'AAPL', name: 'Apple Inc.', price: '$178.50', change: '+2.5%', sector: 'Technology' },
    { symbol: 'MSFT', name: 'Microsoft Corp.', price: '$380.20', change: '+1.8%', sector: 'Technology' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', price: '$139.80', change: '+3.2%', sector: 'Technology' },
    { symbol: 'TSLA', name: 'Tesla Inc.', price: '$242.50', change: '-1.5%', sector: 'Automotive' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', price: '$193.10', change: '+4.1%', sector: 'E-Commerce' },
    { symbol: 'NVDA', name: 'NVIDIA Corp.', price: '$875.30', change: '+5.8%', sector: 'Semiconductors' },
  ];

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
            className="flex-1 rounded-md border border-border bg-muted/50 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 dark:focus:ring-offset-slate-900"
          />
          <button className="inline-flex items-center gap-2 rounded-md bg-primary text-white px-3 py-2 text-sm font-medium hover:bg-primary/90 transition-colors">
            <span className="fa-solid fa-magnifying-glass" />
            <span>Search</span>
          </button>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-foreground mb-3">Popular Stocks</h2>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {popularStocks.map((stock) => (
            <div key={stock.symbol} className="group rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm hover:shadow-md hover:border-primary/30 transition-all duration-300 cursor-pointer">
              <div className="flex items-start justify-between mb-2">
                <div className="min-w-0">
                  <h3 className="font-bold text-foreground text-base">{stock.symbol}</h3>
                  <p className="text-xs text-muted-foreground truncate">{stock.name}</p>
                </div>
                <span className={`text-xs font-semibold px-2 py-1 rounded-full flex-shrink-0 ${
                  stock.change.startsWith('+') 
                    ? 'bg-success/10 text-success' 
                    : 'bg-destructive/10 text-destructive'
                }`}>
                  {stock.change}
                </span>
              </div>
              <div className="space-y-1.5 pt-2 border-t border-border/30">
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Price</span>
                  <span className="font-semibold text-foreground">{stock.price}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-muted-foreground">Sector</span>
                  <span className="text-sm text-foreground">{stock.sector}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-border/50 bg-gradient-soft p-8 text-center">
        <div className="space-y-3">
          <div className="text-4xl">
            <span className="fa-solid fa-arrow-trend-up text-success" />
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


