import React from 'react';

export const WatchlistPage: React.FC = () => {
  const watchlistItems = [
    { symbol: 'AAPL', price: '$178.50', change: '+2.5%', added: '3 days ago' },
    { symbol: 'TSLA', price: '$242.50', change: '-1.5%', added: '1 week ago' },
    { symbol: 'MSFT', price: '$380.20', change: '+1.8%', added: '2 weeks ago' },
  ];

  return (
    <section className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">My Watchlist</h1>
        <p className="text-base text-muted-foreground max-w-2xl">
          Track your favorite stocks and quickly access recent debates. Get AI insights with a single click.
        </p>
      </div>

      {watchlistItems.length > 0 ? (
        <div className="space-y-2">
          {watchlistItems.map((item, idx) => (
            <div key={idx} className="rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-3 shadow-sm hover:shadow-md transition-all group">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="font-bold text-base text-foreground">{item.symbol}</h3>
                  <p className="text-xs text-muted-foreground">Added {item.added}</p>
                </div>
                <div className="flex items-end gap-3 flex-shrink-0">
                  <div className="text-right">
                    <p className="font-semibold text-foreground text-base">{item.price}</p>
                    <p className={`text-xs font-medium ${
                      item.change.startsWith('+') 
                        ? 'text-success' 
                        : 'text-destructive'
                    }`}>
                      {item.change}
                    </p>
                  </div>
                  <button className="inline-flex items-center gap-1.5 rounded-md bg-primary text-white px-3 py-1.5 text-xs font-medium hover:bg-primary/90 transition-colors opacity-0 group-hover:opacity-100">
                    <span className="fa-solid fa-scale-balanced" />
                    <span>Debate</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-lg border border-border/50 bg-gradient-soft p-8 text-center">
          <div className="space-y-3">
            <div className="text-4xl">
              <span className="fa-solid fa-star text-warning" />
            </div>
            <h3 className="text-base font-semibold text-foreground">Your watchlist is empty</h3>
            <p className="text-xs text-muted-foreground max-w-md mx-auto">
              Add stocks from the Stocks page or use the search feature to build your watchlist.
            </p>
          </div>
        </div>
      )}
    </section>
  );
};


