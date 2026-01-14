import { renderHook, act, waitFor } from '@testing-library/react';
import { useDebate, useFinancialData, useCompanyInfo, useNews, useMarketAnalysis } from '../../hooks/useApi';
import * as endpoints from '../../api/endpoints';

jest.mock('../../api/endpoints');

describe('useApi Hooks', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('useDebate', () => {
    it('should initialize with null result and loading false', () => {
      const { result } = renderHook(() => useDebate());
      
      expect(result.current.result).toBeNull();
      expect(result.current.loading.isLoading).toBe(false);
      expect(result.current.loading.error).toBeNull();
    });

    it('should set loading state while running debate', async () => {
      const mockDebateData = {
        symbol: 'AAPL',
        debate_id: 'debate-123',
        agents: [],
        moderator_summary: 'Summary',
        judge_decision: {
          recommendation: 'buy',
          rationale: 'Good fundamentals',
          confidence_score: 0.85,
          key_factors: ['Growth'],
        },
        confidence: 0.85,
        timestamp: '2024-01-10T00:00:00Z',
      };

      (endpoints.fetchDebateAsync as jest.Mock).mockResolvedValue(mockDebateData);

      const { result } = renderHook(() => useDebate());

      act(() => {
        result.current.runDebate({ symbol: 'AAPL' });
      });

      await waitFor(() => {
        expect(result.current.loading.isLoading).toBe(false);
      });

      expect(result.current.result).toEqual(mockDebateData);
    });

    it('should handle debate error', async () => {
      const error = new Error('Debate failed');
      (endpoints.fetchDebateAsync as jest.Mock).mockRejectedValue(error);

      const { result } = renderHook(() => useDebate());

      await act(async () => {
        try {
          await result.current.runDebate({ symbol: 'AAPL' });
        } catch (e) {
          // Expected error
        }
      });

      expect(result.current.loading.error).toBe('Debate failed');
    });
  });

  describe('useFinancialData', () => {
    it('should fetch financial data successfully', async () => {
      const mockFinancialData = {
        symbol: 'AAPL',
        company_name: 'Apple Inc.',
        sector: 'Technology',
        industry: 'Consumer Electronics',
        market_cap: 2800000000000,
        pe_ratio: 28.5,
        dividend_yield: 0.005,
        revenue: 383285000000,
        net_income: 99803000000,
        cash_flow: 110543000000,
        balance_sheet: {
          total_assets: 352755000000,
          total_liabilities: 123137000000,
          shareholders_equity: 50251000000,
        },
        metrics: {},
      };

      (endpoints.fetchFinancialDataAsync as jest.Mock).mockResolvedValue(mockFinancialData);

      const { result } = renderHook(() => useFinancialData());

      await act(async () => {
        await result.current.fetchData('AAPL');
      });

      expect(result.current.data).toEqual(mockFinancialData);
      expect(result.current.loading.isLoading).toBe(false);
    });

    it('should handle financial data error', async () => {
      const error = new Error('Failed to fetch financial data for AAPL');
      (endpoints.fetchFinancialDataAsync as jest.Mock).mockRejectedValue(error);

      const { result } = renderHook(() => useFinancialData());

      await act(async () => {
        try {
          await result.current.fetchData('AAPL');
        } catch (e) {
          // Expected error
        }
      });

      expect(result.current.loading.error).toBe('Failed to fetch financial data for AAPL');
    });
  });

  describe('useCompanyInfo', () => {
    it('should fetch company info successfully', async () => {
      const mockCompanyInfo = {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        description: 'Technology company',
        sector: 'Technology',
        industry: 'Consumer Electronics',
        website: 'https://www.apple.com',
        employees: 164000,
        founded: '1976',
        headquarters: 'Cupertino, CA',
        ceo: 'Tim Cook',
      };

      (endpoints.fetchCompanyInfoAsync as jest.Mock).mockResolvedValue(mockCompanyInfo);

      const { result } = renderHook(() => useCompanyInfo());

      await act(async () => {
        await result.current.fetchData('AAPL');
      });

      expect(result.current.data).toEqual(mockCompanyInfo);
      expect(result.current.loading.isLoading).toBe(false);
    });
  });

  describe('useNews', () => {
    it('should fetch news successfully', async () => {
      const mockNews = [
        {
          id: 'news-1',
          title: 'Apple announces new product',
          content: 'Apple has announced a new product',
          source: 'Reuters',
          published_at: '2024-01-10T10:00:00Z',
          sentiment: 'positive' as const,
          relevance_score: 0.95,
        },
      ];

      (endpoints.fetchNewsAsync as jest.Mock).mockResolvedValue(mockNews);

      const { result } = renderHook(() => useNews());

      await act(async () => {
        await result.current.fetchData('AAPL');
      });

      expect(result.current.data).toEqual(mockNews);
      expect(result.current.loading.isLoading).toBe(false);
    });

    it('should fetch news with custom limit', async () => {
      const mockNews = [];
      (endpoints.fetchNewsAsync as jest.Mock).mockResolvedValue(mockNews);

      const { result } = renderHook(() => useNews());

      await act(async () => {
        await result.current.fetchData('AAPL', 20);
      });

      expect(endpoints.fetchNewsAsync).toHaveBeenCalledWith('AAPL', 20);
    });
  });

  describe('useMarketAnalysis', () => {
    it('should fetch market analysis successfully', async () => {
      const mockMarketAnalysis = {
        timestamp: '2024-01-10T00:00:00Z',
        market_indices: [
          {
            name: 'S&P 500',
            value: 4800,
            change: 50,
            change_percent: 1.05,
          },
        ],
        sector_performance: [
          {
            sector: 'Technology',
            change_percent: 1.5,
            performers: ['AAPL', 'MSFT'],
          },
        ],
        volatility_index: 15.5,
        market_sentiment: 'bullish' as const,
        macroeconomic_indicators: {
          unemployment_rate: 3.7,
          inflation_rate: 3.2,
        },
      };

      (endpoints.fetchMarketAnalysisAsync as jest.Mock).mockResolvedValue(mockMarketAnalysis);

      const { result } = renderHook(() => useMarketAnalysis());

      await act(async () => {
        await result.current.fetchData();
      });

      expect(result.current.data).toEqual(mockMarketAnalysis);
      expect(result.current.loading.isLoading).toBe(false);
    });
  });
});
