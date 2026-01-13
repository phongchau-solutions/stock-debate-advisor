/**
 * Stock Debate Advisor API Client - TypeScript/React
 * 
 * This client integrates with the FastAPI backend.
 * Can be used with Atom state management for frontend.
 * 
 * Usage:
 * ```tsx
 * import { DebateAPI } from './api-client';
 * 
 * const api = new DebateAPI('http://localhost:8000');
 * const symbols = await api.getSymbols();
 * const sessionId = await api.startDebate('MBB', 3);
 * ```
 */

export interface DebateRequest {
  symbol: string;
  rounds: number;
}

export interface VerdictResponse {
  recommendation: 'BUY' | 'HOLD' | 'SELL';
  confidence: 'LOW' | 'MEDIUM' | 'HIGH';
  rationale: string;
  score: number;
}

export interface DebateSessionResponse {
  session_id: string;
  symbol: string;
  rounds: number;
  status: string;
  created_at: string;
}

export interface DebateStatusResponse {
  session_id: string;
  symbol: string;
  status: string;
  progress: number;
  current_round: number;
  total_rounds: number;
  estimated_completion?: string;
}

export interface DebateResultResponse {
  session_id: string;
  symbol: string;
  status: string;
  rounds: number;
  verdict?: VerdictResponse;
  debate_summary?: string;
  financial_data?: Record<string, any>;
  technical_data?: Record<string, any>;
  error?: string;
  completed_at?: string;
}

export interface SymbolListResponse {
  symbols: string[];
  count: number;
}

export interface Session {
  session_id: string;
  symbol: string;
  status: string;
  created_at: string;
  completed_at?: string;
}

export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: Record<string, any>
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export class DebateAPI {
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string = 'http://localhost:8000', timeout: number = 30000) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.timeout = timeout;
  }

  /**
   * Make HTTP request with error handling
   */
  private async request<T>(
    method: string,
    endpoint: string,
    body?: Record<string, any>
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const options: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(url, options);
      const data = await response.json();

      if (!response.ok) {
        throw new APIError(
          response.status,
          data.detail || data.error || 'Unknown error',
          data
        );
      }

      return data as T;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(0, `Connection error: ${error}`);
    }
  }

  // ==================== Health & Config ====================

  /**
   * Check API health
   */
  async healthCheck(): Promise<Record<string, any>> {
    return this.request('GET', '/');
  }

  /**
   * Get API configuration
   */
  async getConfig(): Promise<Record<string, any>> {
    return this.request('GET', '/api/config');
  }

  // ==================== Symbols ====================

  /**
   * Get available stock symbols
   */
  async getSymbols(): Promise<string[]> {
    const response = await this.request<SymbolListResponse>('GET', '/api/symbols');
    return response.symbols;
  }

  // ==================== Debate ====================

  /**
   * Start a new debate
   */
  async startDebate(symbol: string, rounds: number = 3): Promise<string> {
    const response = await this.request<DebateSessionResponse>(
      'POST',
      '/api/debate/start',
      { symbol, rounds }
    );
    return response.session_id;
  }

  /**
   * Get debate status
   */
  async getDebateStatus(sessionId: string): Promise<DebateStatusResponse> {
    return this.request('GET', `/api/debate/status/${sessionId}`);
  }

  /**
   * Get debate result
   */
  async getDebateResult(sessionId: string): Promise<DebateResultResponse> {
    return this.request('GET', `/api/debate/result/${sessionId}`);
  }

  /**
   * Poll for debate result with exponential backoff
   */
  async pollDebateResult(
    sessionId: string,
    pollInterval: number = 2000,
    maxWait: number = 300000
  ): Promise<DebateResultResponse> {
    const startTime = Date.now();
    let currentInterval = pollInterval;

    while (Date.now() - startTime < maxWait) {
      try {
        const result = await this.getDebateResult(sessionId);
        if (result.status === 'completed' || result.status === 'failed') {
          return result;
        }
      } catch (error) {
        if (error instanceof APIError && error.status !== 202) {
          throw error;
        }
      }

      await new Promise((resolve) => setTimeout(resolve, currentInterval));
      // Exponential backoff with cap at 5 seconds
      currentInterval = Math.min(currentInterval * 1.2, 5000);
    }

    throw new Error(`Debate did not complete within ${maxWait / 1000} seconds`);
  }

  /**
   * Stream debate status with callback
   */
  async streamDebateStatus(
    sessionId: string,
    callback: (status: DebateStatusResponse) => void,
    pollInterval: number = 2000,
    maxWait: number = 300000
  ): Promise<DebateStatusResponse> {
    const startTime = Date.now();

    while (Date.now() - startTime < maxWait) {
      try {
        const status = await this.getDebateStatus(sessionId);
        callback(status);

        if (status.status === 'completed' || status.status === 'failed') {
          return status;
        }
      } catch (error) {
        if (error instanceof APIError && error.status !== 202) {
          throw error;
        }
      }

      await new Promise((resolve) => setTimeout(resolve, pollInterval));
    }

    throw new Error(`Debate did not complete within ${maxWait / 1000} seconds`);
  }

  // ==================== Sessions ====================

  /**
   * List all debate sessions
   */
  async listSessions(): Promise<{ total: number; sessions: Session[] }> {
    return this.request('GET', '/api/sessions');
  }

  /**
   * Get session details
   */
  async getSession(sessionId: string): Promise<Record<string, any>> {
    return this.request('GET', `/api/sessions/${sessionId}`);
  }

  /**
   * Delete a session
   */
  async deleteSession(sessionId: string): Promise<void> {
    await this.request('DELETE', `/api/sessions/${sessionId}`);
  }
}

/**
 * React Hook for using the API
 */
export function useDebateAPI(baseUrl?: string) {
  const apiRef = React.useRef<DebateAPI | null>(null);

  if (!apiRef.current) {
    apiRef.current = new DebateAPI(baseUrl);
  }

  return apiRef.current;
}
