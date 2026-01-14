# Sample stock data for demonstration
# This can be loaded into DynamoDB on deployment

## Stock Symbols
- MBB (Militarybank)
- VNM (Vinamilk)
- VCB (Vietcombank)
- TCB (Techcombank)
- FPT (FPT Software)

## Data Structure
{
  "symbol": "MBB",
  "timestamp": "2024-01-15T10:30:00",
  "prices": {
    "current": 28.5,
    "high_52w": 35.2,
    "low_52w": 18.4
  },
  "fundamentals": {
    "pe_ratio": 12.3,
    "market_cap": "45B",
    "eps": 2.32,
    "dividend_yield": 3.5
  },
  "technical": {
    "rsi": 52,
    "macd": "positive",
    "sma_200": 26.8
  }
}
