import React from 'react';

export const NewsPage: React.FC = () => {
  const newsItems = [
    { title: 'Tech stocks rally on AI momentum', date: '2 hours ago', sentiment: 'positive', category: 'Technology' },
    { title: 'Fed signals potential rate cuts next quarter', date: '4 hours ago', sentiment: 'positive', category: 'Market' },
    { title: 'Energy sector faces headwinds from supply concerns', date: '6 hours ago', sentiment: 'negative', category: 'Energy' },
  ];

  return (
    <section className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Market News</h1>
        <p className="text-base text-muted-foreground max-w-2xl">
          Curated financial news and market narratives. Our sentiment analyzer highlights key drivers for your watched stocks.
        </p>
      </div>

      <div className="space-y-2">
        {newsItems.map((item, idx) => (
          <div key={idx} className="rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start gap-3">
              <div className={`text-lg p-1.5 rounded flex-shrink-0 ${
                item.sentiment === 'positive' 
                  ? 'bg-success/10 text-success' 
                  : item.sentiment === 'negative'
                  ? 'bg-destructive/10 text-destructive'
                  : 'bg-warning/10 text-warning'
              }`}>
                <span className={`fa-solid ${
                  item.sentiment === 'positive' 
                    ? 'fa-arrow-trend-up' 
                    : item.sentiment === 'negative'
                    ? 'fa-arrow-trend-down'
                    : 'fa-minus'
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-foreground text-sm mb-1">{item.title}</h3>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs px-2 py-0.5 rounded-full bg-muted text-muted-foreground font-medium">{item.category}</span>
                  <span className="text-xs text-muted-foreground">{item.date}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="rounded-lg border border-border/50 bg-gradient-soft p-6 text-center">
        <div className="space-y-3">
          <div className="text-3xl">
            <span className="fa-solid fa-newspaper text-primary" />
          </div>
          <h3 className="text-base font-semibold text-foreground">News Feed Integration</h3>
          <p className="text-xs text-muted-foreground max-w-md mx-auto">
            Real-time news and sentiment integration from major financial sources coming soon.
          </p>
        </div>
      </div>
    </section>
  );
};


