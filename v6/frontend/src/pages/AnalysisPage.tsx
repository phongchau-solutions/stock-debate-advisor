import React, { FormEvent, useState } from 'react';
import { useAtom } from 'jotai';
import { selectedSymbolAtom } from '../state/selectionAtom';
import { useDebate } from '../hooks/useApi';

export const AnalysisPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useAtom(selectedSymbolAtom);
  const [symbolInput, setSymbolInput] = useState(selectedSymbol ?? '');
  const { result, loading, runDebate } = useDebate();
  const error = loading.error;

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!symbolInput.trim()) return;
    const symbol = symbolInput.trim().toUpperCase();
    setSelectedSymbol(symbol);
    try {
      await runDebate({ symbol });
    } catch (err) {
      console.error('Debate error:', err);
    }
  };

  return (
    <section className="space-y-6 animate-fade-in">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight text-foreground">Multi-Agent Debate</h1>
        <p className="text-base text-muted-foreground max-w-2xl">
          Run structured AI-powered debates between fundamental, technical, and sentiment analysts. Get comprehensive investment insights powered by generative AI.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr,2fr]">
        {/* Input Card */}
        <div className="lg:col-span-1">
          <form
            onSubmit={onSubmit}
            className="space-y-3 rounded-lg border border-border/50 bg-gradient-soft p-4 shadow-sm hover:shadow-md transition-shadow"
          >
            <div>
              <label className="block text-xs font-semibold text-foreground mb-1.5" htmlFor="symbol">
                <span className="fa-solid fa-magnifying-glass mr-2" />
                Stock Symbol (VN30)
              </label>
              <input
                id="symbol"
                name="symbol"
                placeholder="e.g., MBB, VCB, TCB, VNM, HPG"
                value={symbolInput}
                onChange={(e) => setSymbolInput(e.target.value)}
                className="w-full rounded-md border border-border bg-white dark:bg-slate-900 px-3 py-2 text-sm outline-none ring-offset-background focus:ring-2 focus:ring-primary focus:ring-offset-2 dark:focus:ring-offset-slate-950 placeholder-muted-foreground font-medium"
              />
            </div>
            <button
              type="submit"
              className="w-full inline-flex items-center justify-center gap-2 rounded-md bg-gradient-primary px-3 py-2 text-xs font-semibold text-white shadow-md hover:shadow-lg hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading.isLoading}
            >
              <span className="fa-solid fa-scale-balanced" aria-hidden="true" />
              <span>{loading.isLoading ? 'Running Debate…' : 'Start Debate'}</span>
            </button>
            
            {selectedSymbol && (
              <div className="pt-2 border-t border-border/30">
                <p className="text-xs text-muted-foreground">
                  <span className="font-medium text-foreground">{selectedSymbol}</span> selected
                </p>
              </div>
            )}
          </form>
        </div>

        {/* Results Card */}
        <div className="lg:col-span-1">
          <div className="space-y-3 rounded-lg border border-border/50 bg-white dark:bg-slate-900 p-4 shadow-sm">
            <div>
              <h2 className="text-base font-semibold text-foreground mb-1">
                <span className="fa-solid fa-comments mr-2 text-primary" />
                Debate Transcript
              </h2>
              <p className="text-xs text-muted-foreground">Live analysis from AI agents</p>
            </div>

            <div className="space-y-2">
              {!selectedSymbol && (
                <div className="rounded-md bg-primary-light p-3 border border-primary/20">
                  <p className="text-xs text-foreground/80 font-medium">
                    <span className="fa-solid fa-lightbulb mr-2 text-primary" />
                    Enter a ticker symbol to begin the multi-agent debate
                  </p>
                </div>
              )}

              {selectedSymbol && !result && !error && !loading.isLoading && (
                <div className="rounded-md bg-success-light p-3 border border-success/20">
                  <p className="text-xs text-foreground/80 font-medium">
                    Ready to debate <span className="font-semibold text-success">{selectedSymbol}</span>
                  </p>
                </div>
              )}

              {loading.isLoading && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-success rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                    </div>
                    <p className="text-xs font-medium text-foreground">
                      Running multi-agent analysis…
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">Analyzing fundamentals, technicals, and sentiment for {selectedSymbol}</p>
                </div>
              )}

              {error && (
                <div className="rounded-md bg-destructive-light p-3 border border-destructive/20">
                  <p className="text-xs text-destructive font-medium">
                    <span className="fa-solid fa-circle-exclamation mr-2" />
                    {error}
                  </p>
                </div>
              )}

              {result && result.agents && result.agents.length > 0 && (
                <div className="space-y-3">
                  {/* Judge Decision */}
                  <div className="rounded-md bg-primary-light p-3 border border-primary/30">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-xs font-semibold text-primary uppercase tracking-wide">Judge Decision</p>
                        <p className="text-sm font-bold text-foreground capitalize mt-1">
                          {result.judge_decision.recommendation}
                        </p>
                      </div>
                      <span className={`text-lg font-bold ${
                        result.judge_decision.recommendation === 'buy' ? 'text-success' :
                        result.judge_decision.recommendation === 'sell' ? 'text-destructive' :
                        'text-warning'
                      }`}>
                        {result.judge_decision.recommendation === 'buy' && '📈'}
                        {result.judge_decision.recommendation === 'sell' && '📉'}
                        {result.judge_decision.recommendation === 'hold' && '➡️'}
                      </span>
                    </div>
                    <p className="text-xs text-foreground/80">{result.judge_decision.rationale}</p>
                    <p className="text-xs text-muted-foreground mt-2">Confidence: {(result.judge_decision.confidence_score * 100).toFixed(0)}%</p>
                  </div>

                  {/* Moderator Summary */}
                  <div className="rounded-md bg-accent-light p-3 border border-accent/30">
                    <p className="text-xs font-semibold text-accent uppercase tracking-wide mb-1">Moderator Summary</p>
                    <p className="text-xs text-foreground/80">{result.moderator_summary}</p>
                  </div>

                  {/* Agent Analysis Cards */}
                  <div className="space-y-2">
                    <p className="text-xs font-semibold text-foreground uppercase tracking-wide">Agent Analyses</p>
                    {result.agents.map((agent, idx) => (
                      <div key={idx} className="rounded-md bg-muted/50 p-3 border border-border/30">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-bold text-primary uppercase">{agent.agent_name}</span>
                          <span className="inline-block px-2 py-0.5 rounded-full bg-primary/10 text-xs font-medium text-primary">
                            {(agent.confidence * 100).toFixed(0)}% confidence
                          </span>
                        </div>
                        <p className="text-xs text-foreground/80 leading-relaxed">{agent.analysis}</p>
                        {agent.key_points && agent.key_points.length > 0 && (
                          <ul className="text-xs text-muted-foreground mt-2 space-y-1 ml-3">
                            {agent.key_points.slice(0, 3).map((point, i) => (
                              <li key={i} className="list-disc">{point}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};


