import { atom } from 'jotai';
import { apiClient } from './client';

// ============================================================================
// Types
// ============================================================================

export interface DebateRequest {
  symbol: string;
  context?: string;
}

export interface DebateResponse {
  symbol: string;
  debate_id: string;
  agents: AgentResponse[];
  moderator_summary: string;
  judge_decision: JudgeDecision;
  confidence: number;
  timestamp: string;
}

export interface AgentResponse {
  agent_name: string;
  agent_type: 'fundamental' | 'technical' | 'sentiment';
  analysis: string;
  confidence: number;
  key_points: string[];
}

export interface JudgeDecision {
  recommendation: 'buy' | 'hold' | 'sell';
  rationale: string;
  confidence_score: number;
  key_factors: string[];
}

export interface FinancialData {
  symbol: string;
  company_name: string;
  sector: string;
  industry: string;
  market_cap: number;
  pe_ratio: number;
  dividend_yield: number;
  revenue: number;
  net_income: number;
  cash_flow: number;
  balance_sheet: {
    total_assets: number;
    total_liabilities: number;
    shareholders_equity: number;
  };
  metrics: Record<string, number>;
}

export interface CompanyInfo {
  symbol: string;
  name: string;
  description: string;
  sector: string;
  industry: string;
  website: string;
  employees: number;
  founded: string;
  headquarters: string;
  ceo: string;
}

export interface NewsItem {
  id: string;
  title: string;
  content: string;
  source: string;
  published_at: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  relevance_score: number;
  url?: string;
}

export interface MarketAnalysis {
  timestamp: string;
  market_indices: {
    name: string;
    value: number;
    change: number;
    change_percent: number;
  }[];
  sector_performance: {
    sector: string;
    change_percent: number;
    performers: string[];
  }[];
  volatility_index: number;
  market_sentiment: 'bullish' | 'neutral' | 'bearish';
  macroeconomic_indicators: Record<string, number>;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

// ============================================================================
// Atoms for Loading States
// ============================================================================

export const debateLoadingAtom = atom<LoadingState>({
  isLoading: false,
  error: null,
});

export const financialLoadingAtom = atom<LoadingState>({
  isLoading: false,
  error: null,
});

export const companyLoadingAtom = atom<LoadingState>({
  isLoading: false,
  error: null,
});

export const newsLoadingAtom = atom<LoadingState>({
  isLoading: false,
  error: null,
});

export const marketLoadingAtom = atom<LoadingState>({
  isLoading: false,
  error: null,
});

// ============================================================================
// Atoms for Data
// ============================================================================

export const debateResultAtom = atom<DebateResponse | null>(null);
export const financialDataAtom = atom<FinancialData | null>(null);
export const companyInfoAtom = atom<CompanyInfo | null>(null);
export const newsAtom = atom<NewsItem[]>([]);
export const marketAnalysisAtom = atom<MarketAnalysis | null>(null);

// ============================================================================
// API Functions (using atoms as async state)
// ============================================================================

/**
 * Run multi-agent debate on a stock
 * Maps to crewai-orchestration endpoints:
 * 1. POST /v1/debate/start - Start debate session
 * 2. GET /v1/debate/status/{session_id} - Poll for completion
 * 3. GET /v1/debate/result/{session_id} - Get results
 */
export const fetchDebateAsync = async (
  params: DebateRequest
): Promise<DebateResponse> => {
  try {
    // Step 1: Start debate session
    const startResponse = await apiClient.post<any>(
      '/v1/debate/start',
      {
        ticker: params.symbol,
        timeframe: '3 months',
        min_rounds: 1,
        max_rounds: 1
      }
    );
    
    const sessionId = startResponse.session_id;
    
    // Step 2: Poll for completion (with timeout)
    let debateResult: any = null;
    let isComplete = false;
    let pollCount = 0;
    const maxPolls = 60; // 60 seconds with 1s intervals
    
    while (!isComplete && pollCount < maxPolls) {
      const statusResponse = await apiClient.get<any>(
        `/v1/debate/status/${sessionId}`
      );
      
      const status = statusResponse.status || 'in_progress';
      const progress = statusResponse.progress || 0;
      
      if (status === 'completed' || progress >= 100) {
        isComplete = true;
        // Step 3: Get final results
        debateResult = await apiClient.get<any>(
          `/v1/debate/result/${sessionId}`
        );
        break;
      }
      
      pollCount++;
      // Wait 1 second before next poll
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    if (!isComplete) {
      throw new Error('Debate session timed out. Please check status manually.');
    }
    
    // Parse debate result
    const result = debateResult.data || debateResult;
    const agents: AgentResponse[] = [];
    
    // Add placeholder agent response
    if (result.debate_summary) {
      agents.push({
        agent_name: 'Debate Panel',
        agent_type: 'fundamental',
        analysis: result.debate_summary,
        confidence: 0.8,
        key_points: []
      });
    }
    
    // Parse verdict
    const verdict = result.verdict || {};
    const recommendation = (verdict.recommendation || 'HOLD').toUpperCase();
    
    return {
      symbol: params.symbol,
      debate_id: sessionId,
      agents,
      moderator_summary: result.debate_summary || 'Debate completed successfully',
      judge_decision: {
        recommendation: (recommendation === 'BUY' ? 'buy' : recommendation === 'SELL' ? 'sell' : 'hold') as 'buy' | 'hold' | 'sell',
        rationale: verdict.rationale || 'Analysis complete',
        confidence_score: (verdict.score || 5) / 10,
        key_factors: []
      },
      confidence: (verdict.score || 5) / 10,
      timestamp: result.completed_at || new Date().toISOString()
    };
    
  } catch (error) {
    throw new Error('Failed to run debate. Please try again.');
  }
};

/**
 * Fetch financial data for a symbol
 */
export const fetchFinancialDataAsync = async (
  symbol: string
): Promise<FinancialData> => {
  try {
    // Backend doesn't have dedicated financial endpoint yet
    // Return mock data - will be populated from debate analysis
    return {
      symbol,
      company_name: symbol,
      sector: 'Technology',
      industry: 'Software',
      market_cap: 0,
      pe_ratio: 0,
      dividend_yield: 0,
      revenue: 0,
      net_income: 0,
      cash_flow: 0,
      balance_sheet: {
        total_assets: 0,
        total_liabilities: 0,
        shareholders_equity: 0
      },
      metrics: {}
    };
  } catch (error) {
    throw new Error(`Failed to fetch financial data for ${symbol}`);
  }
};

/**
 * Fetch company information
 */
export const fetchCompanyInfoAsync = async (
  symbol: string
): Promise<CompanyInfo> => {
  try {
    // Backend doesn't have dedicated company endpoint yet
    // Return mock data structure
    return {
      symbol,
      name: symbol,
      description: 'Company information',
      sector: 'Technology',
      industry: 'Software',
      website: `https://www.${symbol.toLowerCase()}.com`,
      employees: 0,
      founded: '2000',
      headquarters: 'USA',
      ceo: 'Unknown'
    };
  } catch (error) {
    throw new Error(`Failed to fetch company info for ${symbol}`);
  }
};

/**
 * Fetch news for a symbol
 */
export const fetchNewsAsync = async (
  symbol: string,
  limit: number = 10
): Promise<NewsItem[]> => {
  try {
    // Backend doesn't have dedicated news endpoint yet
    // Return empty array - will integrate when backend has news service
    return [];
  } catch (error) {
    throw new Error(`Failed to fetch news for ${symbol}`);
  }
};

/**
 * Fetch market analysis
 */
export const fetchMarketAnalysisAsync = async (): Promise<MarketAnalysis> => {
  try {
    // Backend doesn't have dedicated market analysis endpoint yet
    // Return empty structure
    return {
      timestamp: new Date().toISOString(),
      market_indices: [],
      sector_performance: [],
      volatility_index: 0,
      market_sentiment: 'neutral',
      macroeconomic_indicators: {}
    };
  } catch (error) {
    throw new Error('Failed to fetch market analysis');
  }
};

/**
 * Fetch multiple endpoints in parallel
 */
export const fetchComprehensiveAnalysisAsync = async (
  symbol: string
): Promise<{
  financial: FinancialData;
  company: CompanyInfo;
  news: NewsItem[];
}> => {
  try {
    const [financial, company, news] = await Promise.all([
      fetchFinancialDataAsync(symbol),
      fetchCompanyInfoAsync(symbol),
      fetchNewsAsync(symbol),
    ]);

    return { financial, company, news };
  } catch (error) {
    throw new Error('Failed to fetch comprehensive analysis');
  }
};
