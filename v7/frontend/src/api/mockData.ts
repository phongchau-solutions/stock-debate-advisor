/**
 * Mock Data for Development and Testing
 * Used when backend APIs are unavailable
 */

export interface MockDebateHistory {
  debate_id: string;
  symbol: string;
  verdict: 'BUY' | 'HOLD' | 'SELL';
  confidence: number;
  created_at: string;
  duration: number;
}

// Generate mock debate history for last 30 days
export const generateMockDebateHistory = (): MockDebateHistory[] => {
  const symbols = ['MBB', 'VCB', 'TCB', 'ACB', 'HPG', 'FPT', 'VNM', 'GAS'];
  const verdicts: Array<'BUY' | 'HOLD' | 'SELL'> = ['BUY', 'HOLD', 'SELL'];
  const history: MockDebateHistory[] = [];

  const now = new Date();
  
  for (let i = 0; i < 25; i++) {
    const daysAgo = Math.floor(Math.random() * 30);
    const date = new Date(now);
    date.setDate(date.getDate() - daysAgo);

    history.push({
      debate_id: `debate_${i}_${Date.now()}`,
      symbol: symbols[Math.floor(Math.random() * symbols.length)],
      verdict: verdicts[Math.floor(Math.random() * verdicts.length)],
      confidence: Math.floor(Math.random() * 40) + 60, // 60-100
      created_at: date.toISOString(),
      duration: Math.floor(Math.random() * 120) + 30, // 30-150 seconds
    });
  }

  return history.sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
};

// Calculate dashboard stats from history
export const calculateMockStats = (history: MockDebateHistory[]) => {
  const total = history.length;
  const buyCount = history.filter(d => d.verdict === 'BUY').length;
  const holdCount = history.filter(d => d.verdict === 'HOLD').length;
  const sellCount = history.filter(d => d.verdict === 'SELL').length;
  const avgConfidence = total > 0 
    ? Math.round(history.reduce((sum, d) => sum + d.confidence, 0) / total)
    : 0;
  const winRate = total > 0 ? Math.round((buyCount / total) * 100) : 0;

  return {
    total,
    buyCount,
    holdCount,
    sellCount,
    avgConfidence,
    winRate,
  };
};

// Mock available symbols
export const MOCK_SYMBOLS = [
  'MBB', 'VCB', 'TCB', 'ACB', 'HPG', 'FPT', 'VNM', 'GAS',
  'BID', 'SHB', 'CTG', 'BCM', 'MSN', 'KDH', 'PLX', 'NVL',
  'PDR', 'VHM', 'POW', 'VIC', 'VJC', 'SSI', 'HDB', 'STB',
  'SAB', 'GVR', 'SSB', 'TPB', 'MWG', 'VIB'
];

// Mock debate result
export const generateMockDebateResult = (symbol: string) => ({
  symbol,
  debate_id: `debate_${Date.now()}`,
  agents: [
    {
      agent_name: 'Fundamental Analyst',
      agent_type: 'fundamental' as const,
      analysis: `Based on financial reports, ${symbol} shows solid fundamentals with P/E ratio in line with industry average.`,
      confidence: Math.floor(Math.random() * 30) + 65,
      key_points: [
        'Revenue growth: 12% YoY',
        'Debt to equity: 0.45',
        'ROE: 15.2%'
      ]
    },
    {
      agent_name: 'Technical Analyst',
      agent_type: 'technical' as const,
      analysis: `Technical indicators suggest bullish momentum with stock trading above 200-day moving average.`,
      confidence: Math.floor(Math.random() * 30) + 65,
      key_points: [
        'Price above 200-day MA',
        'RSI: 58 (neutral)',
        'Support at key level'
      ]
    },
    {
      agent_name: 'Sentiment Analyst',
      agent_type: 'sentiment' as const,
      analysis: `Market sentiment is positive with increasing institutional interest and positive news flow.`,
      confidence: Math.floor(Math.random() * 30) + 65,
      key_points: [
        'Positive news ratio: 65%',
        'Institutional buying: Strong',
        'Social sentiment: Bullish'
      ]
    }
  ],
  moderator_summary: 'Strong fundamentals combined with positive technicals and sentiment creates a bullish case.',
  judge_decision: {
    recommendation: (['BUY', 'HOLD', 'SELL'] as const)[Math.floor(Math.random() * 3)],
    rationale: 'Multi-factor analysis supports the recommendation',
    confidence_score: Math.floor(Math.random() * 30) + 65,
    key_factors: ['Fundamentals', 'Technical Setup', 'Market Sentiment']
  },
  confidence: Math.floor(Math.random() * 30) + 65,
  timestamp: new Date().toISOString()
});
