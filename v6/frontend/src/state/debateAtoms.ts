/*
 * Atom State Management for Stock Debate Advisor Frontend
 * Using Jotai for atom-based state management
 */

import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai';
import { debateAdvisorClient, DebateSession, SessionInfo, KnowledgeData } from '../api/DebateAdvisorClient';

// ============================================
// Core Atoms
// ============================================

// Available symbols
export const availableSymbolsAtom = atom<string[]>([]);

// Current debate session
export const currentSessionAtom = atom<DebateSession | null>(null);

// Session info (detailed)
export const sessionInfoAtom = atom<SessionInfo | null>(null);

// Debate transcript
export const debateTranscriptAtom = atom<Array<{
  round: number;
  speaker: string;
  content: string;
  timestamp: string;
}>>([]);

// Current round
export const currentRoundAtom = atom<number>(0);

// Debate status
export const debateStatusAtom = atom<'idle' | 'loading' | 'in_progress' | 'completed' | 'error'>('idle');

// Error messages
export const errorMessageAtom = atom<string | null>(null);

// ============================================
// Knowledge Atoms
// ============================================

// Fundamental knowledge
export const fundamentalKnowledgeAtom = atom<KnowledgeData | null>(null);

// Technical knowledge
export const technicalKnowledgeAtom = atom<KnowledgeData | null>(null);

// Sentiment knowledge
export const sentimentKnowledgeAtom = atom<KnowledgeData | null>(null);

// All knowledge loaded
export const allKnowledgeAtom = atom<{
  fundamental: string;
  technical: string;
  sentiment: string;
} | null>(null);

// Knowledge loaded status
export const knowledgeLoadedAtom = atom<boolean>(false);

// ============================================
// Raw Data Atoms
// ============================================

// Financial data
export const financialDataAtom = atom<any>(null);

// Technical data
export const technicalDataAtom = atom<any>(null);

// News data
export const newsDataAtom = atom<any>(null);

// ============================================
// Async Atoms (derived)
// ============================================

// Load symbols
export const loadSymbolsAtom = atom(
  null,
  async (get, set) => {
    try {
      const symbols = await debateAdvisorClient.getAvailableSymbols();
      set(availableSymbolsAtom, symbols);
      return symbols;
    } catch (error) {
      set(errorMessageAtom, `Failed to load symbols: ${error}`);
      throw error;
    }
  }
);

// Start debate session
export const startDebateAtom = atom(
  null,
  async (get, set, { symbol, rounds }: { symbol: string; rounds: number }) => {
    try {
      set(debateStatusAtom, 'loading');
      set(errorMessageAtom, null);

      const session = await debateAdvisorClient.startDebate(symbol, rounds);
      set(currentSessionAtom, session);
      set(debateStatusAtom, 'in_progress');

      // Load knowledge after session starts
      await loadSessionKnowledge(get, set, session.session_id);

      return session;
    } catch (error) {
      set(debateStatusAtom, 'error');
      set(errorMessageAtom, `Failed to start debate: ${error}`);
      throw error;
    }
  }
);

// Get session info
export const getSessionInfoAtom = atom(
  null,
  async (get, set, sessionId: string) => {
    try {
      const info = await debateAdvisorClient.getSessionInfo(sessionId);
      set(sessionInfoAtom, info);
      return info;
    } catch (error) {
      set(errorMessageAtom, `Failed to get session info: ${error}`);
      throw error;
    }
  }
);

// Run debate round
export const runDebateRoundAtom = atom(
  null,
  async (get, set, { sessionId, roundNum }: { sessionId: string; roundNum: number }) => {
    try {
      set(debateStatusAtom, 'loading');
      const result = await debateAdvisorClient.runDebateRound(sessionId, roundNum);
      set(currentRoundAtom, roundNum);
      set(debateStatusAtom, 'in_progress');
      return result;
    } catch (error) {
      set(debateStatusAtom, 'error');
      set(errorMessageAtom, `Failed to run debate round: ${error}`);
      throw error;
    }
  }
);

// Load fundamental knowledge
export const loadFundamentalKnowledgeAtom = atom(
  null,
  async (get, set, sessionId: string) => {
    try {
      const knowledge = await debateAdvisorClient.getFundamentalKnowledge(sessionId);
      set(fundamentalKnowledgeAtom, knowledge);
      return knowledge;
    } catch (error) {
      set(errorMessageAtom, `Failed to load fundamental knowledge: ${error}`);
      throw error;
    }
  }
);

// Load technical knowledge
export const loadTechnicalKnowledgeAtom = atom(
  null,
  async (get, set, sessionId: string) => {
    try {
      const knowledge = await debateAdvisorClient.getTechnicalKnowledge(sessionId);
      set(technicalKnowledgeAtom, knowledge);
      return knowledge;
    } catch (error) {
      set(errorMessageAtom, `Failed to load technical knowledge: ${error}`);
      throw error;
    }
  }
);

// Load sentiment knowledge
export const loadSentimentKnowledgeAtom = atom(
  null,
  async (get, set, sessionId: string) => {
    try {
      const knowledge = await debateAdvisorClient.getSentimentKnowledge(sessionId);
      set(sentimentKnowledgeAtom, knowledge);
      return knowledge;
    } catch (error) {
      set(errorMessageAtom, `Failed to load sentiment knowledge: ${error}`);
      throw error;
    }
  }
);

// Helper function to load all knowledge
async function loadSessionKnowledge(get, set, sessionId: string) {
  try {
    const [fundamental, technical, sentiment] = await Promise.all([
      debateAdvisorClient.getFundamentalKnowledge(sessionId),
      debateAdvisorClient.getTechnicalKnowledge(sessionId),
      debateAdvisorClient.getSentimentKnowledge(sessionId)
    ]);

    set(fundamentalKnowledgeAtom, fundamental);
    set(technicalKnowledgeAtom, technical);
    set(sentimentKnowledgeAtom, sentiment);

    set(allKnowledgeAtom, {
      fundamental: fundamental.knowledge,
      technical: technical.knowledge,
      sentiment: sentiment.knowledge
    });

    set(knowledgeLoadedAtom, true);
  } catch (error) {
    console.error('Failed to load knowledge:', error);
    set(errorMessageAtom, `Failed to load knowledge: ${error}`);
  }
}

// Load all knowledge
export const loadAllKnowledgeAtom = atom(
  null,
  async (get, set, sessionId: string) => {
    await loadSessionKnowledge(get, set, sessionId);
  }
);

// Load financial data
export const loadFinancialDataAtom = atom(
  null,
  async (get, set, symbol: string) => {
    try {
      const data = await debateAdvisorClient.getFinancialData(symbol);
      set(financialDataAtom, data);
      return data;
    } catch (error) {
      set(errorMessageAtom, `Failed to load financial data: ${error}`);
      throw error;
    }
  }
);

// Load technical data
export const loadTechnicalDataAtom = atom(
  null,
  async (get, set, symbol: string) => {
    try {
      const data = await debateAdvisorClient.getTechnicalData(symbol);
      set(technicalDataAtom, data);
      return data;
    } catch (error) {
      set(errorMessageAtom, `Failed to load technical data: ${error}`);
      throw error;
    }
  }
);

// Load news data
export const loadNewsDataAtom = atom(
  null,
  async (get, set, symbol: string) => {
    try {
      const data = await debateAdvisorClient.getNewsData(symbol);
      set(newsDataAtom, data);
      return data;
    } catch (error) {
      set(errorMessageAtom, `Failed to load news data: ${error}`);
      throw error;
    }
  }
);

// End debate session
export const endSessionAtom = atom(
  null,
  async (get, set, sessionId: string) => {
    try {
      await debateAdvisorClient.endSession(sessionId);
      set(currentSessionAtom, null);
      set(sessionInfoAtom, null);
      set(debateStatusAtom, 'idle');
      set(currentRoundAtom, 0);
      set(debateTranscriptAtom, []);
      return true;
    } catch (error) {
      set(errorMessageAtom, `Failed to end session: ${error}`);
      throw error;
    }
  }
);

// ============================================
// Custom Hooks
// ============================================

export function useDebateSession() {
  const [session, setSession] = useAtom(currentSessionAtom);
  const [status, setStatus] = useAtom(debateStatusAtom);
  const [error, setError] = useAtom(errorMessageAtom);

  return { session, setSession, status, setStatus, error, setError };
}

export function useKnowledge() {
  const fundamental = useAtomValue(fundamentalKnowledgeAtom);
  const technical = useAtomValue(technicalKnowledgeAtom);
  const sentiment = useAtomValue(sentimentKnowledgeAtom);
  const knowledgeLoaded = useAtomValue(knowledgeLoadedAtom);

  return { fundamental, technical, sentiment, knowledgeLoaded };
}

export function useDebateControl() {
  const [currentSession] = useAtom(currentSessionAtom);
  const [currentRound, setCurrentRound] = useAtom(currentRoundAtom);
  const [status, setStatus] = useAtom(debateStatusAtom);
  const setTranscript = useSetAtom(debateTranscriptAtom);

  return {
    currentSession,
    currentRound,
    setCurrentRound,
    status,
    setStatus,
    setTranscript
  };
}

export function useRawData() {
  const financial = useAtomValue(financialDataAtom);
  const technical = useAtomValue(technicalDataAtom);
  const news = useAtomValue(newsDataAtom);

  return { financial, technical, news };
}

// ============================================
// Dashboard Analytics Atoms
// ============================================

export interface DebateHistoryItem {
  symbol: string;
  verdict: 'BUY' | 'HOLD' | 'SELL';
  confidence: number;
  timestamp: number;
}

// Dashboard debate history
export const debateHistoryAtom = atom<DebateHistoryItem[]>([]);

// Dashboard statistics
export const dashboardStatsAtom = atom<{
  total: number;
  buyCount: number;
  holdCount: number;
  sellCount: number;
  avgConfidence: number;
  winRate: number;
} | null>(null);

// Load dashboard history from backend
export const loadDebateHistoryAtom = atom(
  null,
  async (get, set) => {
    try {
      // Fetch from backend API
      const response = await apiClient.get<any>('/api/debate/history');
      const history: DebateHistoryItem[] = response.debates || [];
      set(debateHistoryAtom, history);
      
      // Calculate stats
      const total = history.length;
      const buyCount = history.filter((d) => d.verdict === 'BUY').length;
      const holdCount = history.filter((d) => d.verdict === 'HOLD').length;
      const sellCount = history.filter((d) => d.verdict === 'SELL').length;
      const avgConfidence = total > 0 ? Math.round(history.reduce((sum, d) => sum + d.confidence, 0) / total) : 0;
      const winRate = total > 0 ? Math.round((buyCount / total) * 100) : 0;
      
      set(dashboardStatsAtom, {
        total,
        buyCount,
        holdCount,
        sellCount,
        avgConfidence,
        winRate,
      });
      
      return history;
    } catch (error) {
      set(errorMessageAtom, `Failed to load debate history: ${error}`);
      return [];
    }
  }
);

// ============================================
// Financial Data Atoms
// ============================================

export interface FinancialMetrics {
  symbol: string;
  peRatio: number;
  debtToEquity: number;
  profitMargin: number;
  roa: number;
  roe: number;
  currentRatio: number;
  quickRatio: number;
  revenueGrowth: number;
  epsGrowth: number;
  dividendYield: number;
  bookValue: number;
}

// Financial metrics for selected symbol
export const selectedFinancialMetricsAtom = atom<FinancialMetrics | null>(null);

// Load financial metrics from backend
export const loadFinancialMetricsAtom = atom(
  null,
  async (get, set, symbol: string) => {
    try {
      const response = await apiClient.get<any>(`/api/financial/${symbol}`);
      const metrics: FinancialMetrics = {
        symbol: response.symbol,
        peRatio: response.pe_ratio || 0,
        debtToEquity: response.debt_to_equity || 0,
        profitMargin: response.profit_margin || 0,
        roa: response.roa || 0,
        roe: response.roe || 0,
        currentRatio: response.current_ratio || 0,
        quickRatio: response.quick_ratio || 0,
        revenueGrowth: response.revenue_growth || 0,
        epsGrowth: response.eps_growth || 0,
        dividendYield: response.dividend_yield || 0,
        bookValue: response.book_value || 0,
      };
      set(selectedFinancialMetricsAtom, metrics);
      return metrics;
    } catch (error) {
      set(errorMessageAtom, `Failed to load financial metrics for ${symbol}: ${error}`);
      return null;
    }
  }
);
