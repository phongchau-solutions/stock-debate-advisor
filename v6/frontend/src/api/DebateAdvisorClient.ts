/*
 * Frontend API Client for Stock Debate Advisor
 * TypeScript/JavaScript client for frontend integration
 */

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

interface DebateSession {
  session_id: string;
  symbol: string;
  rounds: number;
  status: string;
  created_at: string;
  data_loaded?: {
    financial_reports: number;
    technical_datapoints: number;
    news_articles: number;
  };
}

interface SessionInfo {
  session_id: string;
  symbol: string;
  created_at: string;
  current_round: number;
  data: {
    financial_reports: number;
    technical_datapoints: number;
    news_articles: number;
    current_price?: number;
  };
  verdict?: any;
  transcript_length: number;
}

interface KnowledgeData {
  session_id: string;
  type: string;
  knowledge: string;
}

export class DebateAdvisorClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Health & System
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/`);
    return response.json();
  }

  // Symbols
  async getAvailableSymbols(): Promise<string[]> {
    const response = await fetch(`${this.baseUrl}/api/symbols`);
    const data = await response.json();
    return data.symbols || [];
  }

  // Debate Sessions
  async startDebate(symbol: string, rounds: number = 3): Promise<DebateSession> {
    const response = await fetch(`${this.baseUrl}/api/debate/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol, rounds })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start debate');
    }

    return response.json();
  }

  async getSessionInfo(sessionId: string): Promise<SessionInfo> {
    const response = await fetch(`${this.baseUrl}/api/session/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get session info');
    return response.json();
  }

  async getSessionStatus(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/session/${sessionId}/status`);
    if (!response.ok) throw new Error('Failed to get session status');
    return response.json();
  }

  async runDebateRound(sessionId: string, roundNum: number): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/session/${sessionId}/round/${roundNum}`,
      { method: 'POST' }
    );
    if (!response.ok) throw new Error('Failed to run debate round');
    return response.json();
  }

  async getDebateResults(sessionId: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/session/${sessionId}/results`);
    if (!response.ok) throw new Error('Failed to get results');
    return response.json();
  }

  async endSession(sessionId: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/session/${sessionId}`,
      { method: 'DELETE' }
    );
    if (!response.ok) throw new Error('Failed to end session');
    return response.json();
  }

  // Knowledge Management
  async getFundamentalKnowledge(sessionId: string): Promise<KnowledgeData> {
    const response = await fetch(
      `${this.baseUrl}/api/session/${sessionId}/knowledge/fundamental`
    );
    if (!response.ok) throw new Error('Failed to get fundamental knowledge');
    return response.json();
  }

  async getTechnicalKnowledge(sessionId: string): Promise<KnowledgeData> {
    const response = await fetch(
      `${this.baseUrl}/api/session/${sessionId}/knowledge/technical`
    );
    if (!response.ok) throw new Error('Failed to get technical knowledge');
    return response.json();
  }

  async getSentimentKnowledge(sessionId: string): Promise<KnowledgeData> {
    const response = await fetch(
      `${this.baseUrl}/api/session/${sessionId}/knowledge/sentiment`
    );
    if (!response.ok) throw new Error('Failed to get sentiment knowledge');
    return response.json();
  }

  async getAllKnowledge(sessionId: string): Promise<any> {
    const response = await fetch(
      `${this.baseUrl}/api/session/${sessionId}/knowledge/all`
    );
    if (!response.ok) throw new Error('Failed to get all knowledge');
    return response.json();
  }

  // Data Access
  async getFinancialData(symbol: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/data/${symbol}/financials`);
    if (!response.ok) throw new Error('Failed to get financial data');
    return response.json();
  }

  async getTechnicalData(symbol: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/data/${symbol}/technical`);
    if (!response.ok) throw new Error('Failed to get technical data');
    return response.json();
  }

  async getNewsData(symbol: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/data/${symbol}/news`);
    if (!response.ok) throw new Error('Failed to get news data');
    return response.json();
  }

  // Statistics
  async getStats(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/stats`);
    if (!response.ok) throw new Error('Failed to get stats');
    return response.json();
  }
}

// Export singleton instance
export const debateAdvisorClient = new DebateAdvisorClient();

// Type exports for frontend use
export type { DebateSession, SessionInfo, KnowledgeData };
