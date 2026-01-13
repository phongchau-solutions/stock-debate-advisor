import { useAtom } from 'jotai';
import { useCallback } from 'react';
import {
  debateResultAtom,
  debateLoadingAtom,
  financialDataAtom,
  financialLoadingAtom,
  companyInfoAtom,
  companyLoadingAtom,
  newsAtom,
  newsLoadingAtom,
  marketAnalysisAtom,
  marketLoadingAtom,
  fetchDebateAsync,
  fetchFinancialDataAsync,
  fetchCompanyInfoAsync,
  fetchNewsAsync,
  fetchMarketAnalysisAsync,
  fetchComprehensiveAnalysisAsync,
  DebateRequest,
} from '../api/endpoints';

/**
 * Hook to run debate
 */
export const useDebate = () => {
  const [result, setResult] = useAtom(debateResultAtom);
  const [loading, setLoading] = useAtom(debateLoadingAtom);

  const runDebate = useCallback(
    async (params: DebateRequest) => {
      setLoading({ isLoading: true, error: null });
      try {
        const data = await fetchDebateAsync(params);
        setResult(data);
        return data;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setLoading({ isLoading: false, error: errorMessage });
        throw error;
      } finally {
        setLoading((prev) => ({ ...prev, isLoading: false }));
      }
    },
    [setLoading, setResult]
  );

  return { result, loading, runDebate };
};

/**
 * Hook to fetch financial data
 */
export const useFinancialData = () => {
  const [data, setData] = useAtom(financialDataAtom);
  const [loading, setLoading] = useAtom(financialLoadingAtom);

  const fetchData = useCallback(
    async (symbol: string) => {
      setLoading({ isLoading: true, error: null });
      try {
        const financialData = await fetchFinancialDataAsync(symbol);
        setData(financialData);
        return financialData;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setLoading({ isLoading: false, error: errorMessage });
        throw error;
      } finally {
        setLoading((prev) => ({ ...prev, isLoading: false }));
      }
    },
    [setLoading, setData]
  );

  return { data, loading, fetchData };
};

/**
 * Hook to fetch company info
 */
export const useCompanyInfo = () => {
  const [data, setData] = useAtom(companyInfoAtom);
  const [loading, setLoading] = useAtom(companyLoadingAtom);

  const fetchData = useCallback(
    async (symbol: string) => {
      setLoading({ isLoading: true, error: null });
      try {
        const companyData = await fetchCompanyInfoAsync(symbol);
        setData(companyData);
        return companyData;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setLoading({ isLoading: false, error: errorMessage });
        throw error;
      } finally {
        setLoading((prev) => ({ ...prev, isLoading: false }));
      }
    },
    [setLoading, setData]
  );

  return { data, loading, fetchData };
};

/**
 * Hook to fetch news
 */
export const useNews = () => {
  const [data, setData] = useAtom(newsAtom);
  const [loading, setLoading] = useAtom(newsLoadingAtom);

  const fetchData = useCallback(
    async (symbol: string, limit?: number) => {
      setLoading({ isLoading: true, error: null });
      try {
        const newsData = await fetchNewsAsync(symbol, limit);
        setData(newsData);
        return newsData;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setLoading({ isLoading: false, error: errorMessage });
        throw error;
      } finally {
        setLoading((prev) => ({ ...prev, isLoading: false }));
      }
    },
    [setLoading, setData]
  );

  return { data, loading, fetchData };
};

/**
 * Hook to fetch market analysis
 */
export const useMarketAnalysis = () => {
  const [data, setData] = useAtom(marketAnalysisAtom);
  const [loading, setLoading] = useAtom(marketLoadingAtom);

  const fetchData = useCallback(
    async () => {
      setLoading({ isLoading: true, error: null });
      try {
        const analysisData = await fetchMarketAnalysisAsync();
        setData(analysisData);
        return analysisData;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setLoading({ isLoading: false, error: errorMessage });
        throw error;
      } finally {
        setLoading((prev) => ({ ...prev, isLoading: false }));
      }
    },
    [setLoading, setData]
  );

  return { data, loading, fetchData };
};

/**
 * Hook to fetch comprehensive analysis (all endpoints)
 */
export const useComprehensiveAnalysis = () => {
  const [, setFinancialData] = useAtom(financialDataAtom);
  const [, setCompanyInfo] = useAtom(companyInfoAtom);
  const [, setNews] = useAtom(newsAtom);
  const [loading, setLoading] = useAtom(financialLoadingAtom);

  const fetchData = useCallback(
    async (symbol: string) => {
      setLoading({ isLoading: true, error: null });
      try {
        const { financial, company, news } = await fetchComprehensiveAnalysisAsync(symbol);
        setFinancialData(financial);
        setCompanyInfo(company);
        setNews(news);
        return { financial, company, news };
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        setLoading({ isLoading: false, error: errorMessage });
        throw error;
      } finally {
        setLoading((prev) => ({ ...prev, isLoading: false }));
      }
    },
    [setLoading, setFinancialData, setCompanyInfo, setNews]
  );

  return { loading, fetchData };
};
