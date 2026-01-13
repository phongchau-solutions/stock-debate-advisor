"""
React Components for Stock Debate Advisor
Components using Atom state management
"""

import React, { useEffect } from 'react';
import { useAtom, useAtomValue, useSetAtom } from 'jotai';
import {
  currentSessionAtom,
  debateStatusAtom,
  errorMessageAtom,
  availableSymbolsAtom,
  loadSymbolsAtom,
  startDebateAtom,
  currentRoundAtom,
  loadAllKnowledgeAtom,
  fundamentalKnowledgeAtom,
  technicalKnowledgeAtom,
  sentimentKnowledgeAtom,
  endSessionAtom
} from '../state/debateAtoms';

// Symbol Selector Component
export function SymbolSelector() {
  const symbols = useAtomValue(availableSymbolsAtom);
  const loadSymbols = useSetAtom(loadSymbolsAtom);
  const [selectedSymbol, setSelectedSymbol] = React.useState<string>('');
  const [rounds, setRounds] = React.useState<number>(3);
  const startDebate = useSetAtom(startDebateAtom);
  const [status, setStatus] = useAtom(debateStatusAtom);

  useEffect(() => {
    loadSymbols();
  }, [loadSymbols]);

  const handleStartDebate = async () => {
    if (!selectedSymbol) return;
    try {
      await startDebate({ symbol: selectedSymbol, rounds });
    } catch (error) {
      console.error('Error starting debate:', error);
    }
  };

  return (
    <div className="symbol-selector">
      <h3>Select Stock</h3>
      <select 
        value={selectedSymbol} 
        onChange={(e) => setSelectedSymbol(e.target.value)}
        disabled={status === 'loading'}
      >
        <option value="">Choose a symbol...</option>
        {symbols.map(symbol => (
          <option key={symbol} value={symbol}>{symbol}</option>
        ))}
      </select>

      <div className="rounds-selector">
        <label>
          Rounds:
          <input 
            type="number" 
            min="1" 
            max="5" 
            value={rounds}
            onChange={(e) => setRounds(parseInt(e.target.value))}
            disabled={status === 'loading'}
          />
        </label>
      </div>

      <button 
        onClick={handleStartDebate}
        disabled={!selectedSymbol || status === 'loading'}
        className={`start-btn ${status === 'loading' ? 'loading' : ''}`}
      >
        {status === 'loading' ? 'Starting...' : 'Start Debate'}
      </button>
    </div>
  );
}

// Debate Status Component
export function DebateStatus() {
  const session = useAtomValue(currentSessionAtom);
  const status = useAtomValue(debateStatusAtom);
  const currentRound = useAtomValue(currentRoundAtom);
  const error = useAtomValue(errorMessageAtom);

  if (!session) {
    return <div className="debate-status empty">No active debate</div>;
  }

  return (
    <div className="debate-status">
      <h3>Debate Session: {session.session_id.substring(0, 8)}...</h3>
      <p>Symbol: <strong>{session.symbol}</strong></p>
      <p>Status: <strong>{status}</strong></p>
      <p>Round: {currentRound} / {session.rounds}</p>
      <div className="progress-bar">
        <div 
          className="progress" 
          style={{ width: `${(currentRound / session.rounds) * 100}%` }}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="data-loaded">
        <p>Data Loaded:</p>
        <ul>
          <li>Financial Reports: {session.data_loaded?.financial_reports || 0}</li>
          <li>Technical Data Points: {session.data_loaded?.technical_datapoints || 0}</li>
          <li>News Articles: {session.data_loaded?.news_articles || 0}</li>
        </ul>
      </div>
    </div>
  );
}

// Knowledge Display Component
export function KnowledgeDisplay() {
  const session = useAtomValue(currentSessionAtom);
  const fundamental = useAtomValue(fundamentalKnowledgeAtom);
  const technical = useAtomValue(technicalKnowledgeAtom);
  const sentiment = useAtomValue(sentimentKnowledgeAtom);
  const loadAllKnowledge = useSetAtom(loadAllKnowledgeAtom);

  useEffect(() => {
    if (session && !fundamental) {
      loadAllKnowledge(session.session_id);
    }
  }, [session, fundamental, loadAllKnowledge]);

  if (!session) {
    return null;
  }

  return (
    <div className="knowledge-display">
      <h3>Knowledge Base</h3>

      <div className="knowledge-section">
        <h4>📊 Fundamental Analysis</h4>
        <pre>{fundamental?.knowledge.substring(0, 500)}...</pre>
      </div>

      <div className="knowledge-section">
        <h4>📈 Technical Analysis</h4>
        <pre>{technical?.knowledge.substring(0, 500)}...</pre>
      </div>

      <div className="knowledge-section">
        <h4>📰 Sentiment Analysis</h4>
        <pre>{sentiment?.knowledge.substring(0, 500)}...</pre>
      </div>
    </div>
  );
}

// Debate Control Component
export function DebateControl() {
  const session = useAtomValue(currentSessionAtom);
  const [currentRound, setCurrentRound] = useAtom(currentRoundAtom);
  const status = useAtomValue(debateStatusAtom);
  const endSession = useSetAtom(endSessionAtom);

  if (!session) {
    return null;
  }

  const handleEndDebate = async () => {
    if (window.confirm('End the debate session?')) {
      await endSession(session.session_id);
    }
  };

  return (
    <div className="debate-control">
      <h3>Debate Control</h3>
      
      <div className="round-info">
        <p>Current Round: {currentRound} / {session.rounds}</p>
      </div>

      <button 
        onClick={() => setCurrentRound(currentRound + 1)}
        disabled={currentRound >= session.rounds || status !== 'in_progress'}
        className="next-round-btn"
      >
        Next Round →
      </button>

      <button 
        onClick={handleEndDebate}
        disabled={status === 'idle'}
        className="end-btn"
      >
        End Debate
      </button>
    </div>
  );
}

// Main App Component
export function DebateAdvisorApp() {
  return (
    <div className="debate-advisor-app">
      <header className="app-header">
        <h1>🤖 Stock Debate Advisor</h1>
        <p>Multi-agent AI debate system for stock analysis</p>
      </header>

      <main className="app-main">
        <div className="sidebar">
          <SymbolSelector />
          <DebateStatus />
        </div>

        <div className="content">
          <KnowledgeDisplay />
          <DebateControl />
        </div>
      </main>
    </div>
  );
}

export default DebateAdvisorApp;
