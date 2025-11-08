from __future__ import annotations

from typing import Any, Dict, List, Optional, cast

from integrations.zstock_adapter import ZStock, MultiAssetZStock
from integrations.news_crawler import NewsCrawler
from integrations.sentiment_analyzer import FinancialSentimentAnalyzer

from .base_agent import AgentOutput, BaseAgent


class CrawlerAgent(BaseAgent):
    """Enhanced crawler agent using proven zstock patterns.

    Uses the successful zstock architecture for reliable financial data access.
    Provides OHLC prices, fundamentals, and market context for comprehensive analysis.
    """

    def __init__(self):
        super().__init__(name="crawler_agent", deterministic=True)
        self.news_crawler = NewsCrawler()
        self.sentiment_analyzer = FinancialSentimentAnalyzer()

    def process(self, inputs: Dict[str, Any], session_id: Optional[str] = None) -> AgentOutput:
        """Fetch comprehensive financial data using proven zstock patterns.

        Expected inputs:
        - tickers: List[str] - Stock symbols to analyze
        - start_date: str - Start date (YYYY-MM-DD) 
        - end_date: str - End date (YYYY-MM-DD)
        - period: str - 'quarterly' or 'annual' for fundamentals
        - include_market: bool - Include market indices for context
        """

        tickers: List[str] = inputs.get("tickers", [])
        start_date: str = inputs.get("start_date", "2024-10-01")
        end_date: str = inputs.get("end_date", "2024-11-01") 
        period: str = inputs.get("period", "quarterly")
        include_market: bool = inputs.get("include_market", True)

        source_ids: List[str] = []
        
        # Use MultiAssetZStock for portfolio analysis
        if len(tickers) > 1:
            portfolio = MultiAssetZStock(tickers, source='VIETCAP')
            
            # Get price histories
            try:
                price_histories = portfolio.history(start=start_date, end=end_date)
                close_matrix = portfolio.get_close_prices()
                
                prices_data: Dict[str, Any] = {
                    "individual_histories": {
                        symbol: {
                            "records": len(df),
                            "latest_close": float(df['close'].iloc[-1]) if not df.empty else None,
                            "data": cast(List[Dict[str, Any]], df.to_dict('records')) if len(df) <= 100 else "truncated"
                        } for symbol, df in price_histories.items()
                    },
                    "correlation_matrix": cast(Dict[str, Any], close_matrix.corr().to_dict()) if not close_matrix.empty else {},
                    "price_matrix_shape": close_matrix.shape if not close_matrix.empty else (0, 0)
                }
                source_ids.extend([f"zstock:prices:{s}" for s in tickers])
                
            except Exception as e:
                prices_data = {"error": str(e)}
            
            # Get fundamentals for each symbol
            fundamentals_data = {}
            for ticker in tickers:
                try:
                    stock = ZStock(ticker, source='VIETCAP')
                    ratios = stock.finance.ratios(period=period)
                    
                    if not ratios.empty:
                        latest = ratios.iloc[-1]
                        fundamentals_data[ticker] = {
                            "quarters_available": len(ratios),
                            "latest_ratios": {
                                "revenue": latest.get('revenue'),
                                "net_profit": latest.get('netProfit'),
                                "roe": latest.get('roe'),
                                "pe": latest.get('pe'),
                                "pb": latest.get('pb'),
                                "eps": latest.get('eps')
                            },
                            "trend_data": cast(List[Dict[str, Any]], ratios.tail(5).to_dict('records')) if len(ratios) > 1 else []
                        }
                        source_ids.append(f"zstock:fundamentals:{ticker}")
                    else:
                        fundamentals_data[ticker] = {"error": "No fundamental data available"}
                        
                except Exception as e:
                    fundamentals_data[ticker] = {"error": str(e)}
        
        else:
            # Single symbol analysis
            if tickers:
                symbol = tickers[0]
                stock = ZStock(symbol, source='VIETCAP')
                
                # Price data
                try:
                    price_history = stock.quote.history(start=start_date, end=end_date)
                    prices_data: Dict[str, Any] = {
                        "symbol": symbol,
                        "records": len(price_history),
                        "latest_close": float(price_history['close'].iloc[-1]) if not price_history.empty else None,
                        "data": cast(List[Dict[str, Any]], price_history.tail(50).to_dict('records')) if not price_history.empty else []
                    }
                    source_ids.append(f"zstock:prices:{symbol}")
                except Exception as e:
                    prices_data = {"error": str(e)}
                
                # Fundamental data
                try:
                    ratios = stock.finance.ratios(period=period)
                    balance_sheet = stock.finance.balance_sheet(period=period)
                    
                    fundamentals_data: Dict[str, Dict[str, Any]] = {
                        symbol: {
                            "ratios_quarters": len(ratios),
                            "balance_sheet_items": len(balance_sheet.columns) if not balance_sheet.empty else 0,
                            "latest_ratios": cast(Dict[str, Any], ratios.iloc[-1].to_dict()) if not ratios.empty else {},
                            "key_metrics": {
                                "revenue": ratios.iloc[-1].get('revenue') if not ratios.empty else None,
                                "roe": ratios.iloc[-1].get('roe') if not ratios.empty else None,
                                "pe": ratios.iloc[-1].get('pe') if not ratios.empty else None
                            }
                        }
                    }
                    source_ids.append(f"zstock:fundamentals:{symbol}")
                except Exception as e:
                    fundamentals_data = {symbol: {"error": str(e)}}
            else:
                prices_data = {"error": "No tickers provided"}
                fundamentals_data = {}

        # News and sentiment analysis
        news_data: Dict[str, Any] = {}
        sentiment_data: Dict[str, Any] = {}
        include_news = inputs.get("include_news", True)
        
        if include_news and tickers:
            try:
                # Get news for the symbols
                crawl_results = self.news_crawler.crawl_news_for_symbols(tickers, days_back=7, max_articles_per_source=10)
                
                # Flatten news items from all sources
                all_news_items: List[Any] = []
                vneconomy_items = crawl_results.get("vneconomy", [])
                wsj_items = crawl_results.get("wsj", [])
                if isinstance(vneconomy_items, list):
                    all_news_items.extend(vneconomy_items)
                if isinstance(wsj_items, list):
                    all_news_items.extend(wsj_items)
                
                # Analyze sentiment of collected news
                if all_news_items:
                    sentiment_analysis = self.sentiment_analyzer.analyze_news_batch(all_news_items)
                    
                    news_data: Dict[str, Any] = {
                        "total_articles": len(all_news_items),
                        "sources": [str(getattr(item, 'source', 'Unknown')) for item in all_news_items],
                        "by_source": {
                            "vneconomy": len(crawl_results.get("vneconomy", [])),
                            "wsj": len(crawl_results.get("wsj", []))
                        },
                        "summary": crawl_results.get("summary", {}),
                        "latest_articles": [
                            {
                                "title": str(getattr(item, 'title', '')),
                                "source": str(getattr(item, 'source', '')),
                                "url": str(getattr(item, 'url', '')),
                                "symbols_mentioned": getattr(item, 'symbols_mentioned', [])
                            } for item in all_news_items[:5]  # Top 5 articles
                        ]
                    }
                    
                    sentiment_data = sentiment_analysis
                    source_ids.extend([f"news:{item.source}" for item in all_news_items[:5]])
                else:
                    news_data: Dict[str, Any] = {"message": "No news articles found for symbols", "crawl_summary": crawl_results.get("summary", {})}
                    sentiment_data = {"message": "No sentiment analysis available"}
                    
            except Exception as e:
                news_data = {"error": str(e)}
                sentiment_data = {"error": str(e)}
        else:
            news_data = {"message": "News analysis disabled"}
            sentiment_data = {"message": "Sentiment analysis disabled"}

        # Market context (indices)
        market_data: Dict[str, Any] = {}
        if include_market:
            try:
                # Use first stock's client to get market indices
                if tickers:
                    stock = ZStock(tickers[0], source='VIETCAP') 
                    indices = stock.client.get_indexes(['VNINDEX', 'VN30'])
                    
                    market_data: Dict[str, Any] = {
                        "indices": {
                            name: {
                                "available": len(cast(List[Any], data)) > 0 if isinstance(data, list) else bool(data),
                                "latest_close": cast(List[Any], data)[0]['c'][-1] if (isinstance(data, list) and 
                                                                   len(cast(List[Any], data)) > 0 and 
                                                                   isinstance(cast(List[Any], data)[0], dict) and 
                                                                   'c' in cast(List[Any], data)[0] and 
                                                                   cast(List[Any], data)[0]['c']) else None
                            } for name, data in indices.get('data', {}).items() if name != 'error'
                        }
                    }
                    source_ids.append("zstock:market:indices")
            except Exception as e:
                market_data = {"error": str(e)}

        # Assemble comprehensive payload following zstock success patterns
        payload: Dict[str, Any] = {
            "provider": "zstock_vietcap_with_sentiment",
            "analysis_type": "multi_asset" if len(tickers) > 1 else "single_asset",
            "symbols": tickers,
            "period": period,
            "date_range": {"start": start_date, "end": end_date},
            "prices": prices_data,
            "fundamentals": fundamentals_data,
            "market_context": market_data,
            "news_analysis": news_data,
            "sentiment_analysis": sentiment_data,
            "data_quality": {
                "symbols_processed": len(tickers),
                "price_data_available": "error" not in prices_data,
                "fundamentals_available": all("error" not in v for v in fundamentals_data.values()),
                "market_data_available": "error" not in market_data,
                "news_data_available": "error" not in news_data,
                "sentiment_data_available": "error" not in sentiment_data
            }
        }
        
        prov = self._make_provenance(session_id, source_ids=source_ids)
        return AgentOutput(agent_name=self.name, payload=payload, provenance=prov)
