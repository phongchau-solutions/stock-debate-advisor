"""
Data cache service for storing and retrieving stock data from database.
Reduces API calls and improves PoC demo performance.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import json
import uuid

from services.database import (
    get_session,
    StockPrice,
    StockFinancials,
    NewsArticle,
    DebateSession,
    AgentAnalysis,
    DebateTranscript
)

logger = logging.getLogger(__name__)


class DataCacheService:
    """Service for caching stock data and debate results."""
    
    def __init__(self, db_path: str = "data/debate_cache.db"):
        """
        Initialize cache service.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        from services.database import create_database
        create_database(db_path)
        logger.info(f"DataCacheService initialized with db: {db_path}")
    
    def cache_stock_prices(self, symbol: str, ohlcv_df: pd.DataFrame, data_source: str):
        """
        Cache OHLCV price data.
        
        Args:
            symbol: Stock symbol
            ohlcv_df: DataFrame with OHLCV data (index: datetime)
            data_source: Source of data (vietcap, yfinance, synthetic)
        """
        session = get_session(self.db_path)
        
        try:
            # Delete existing data for this symbol
            session.query(StockPrice).filter(StockPrice.symbol == symbol).delete()
            
            # Insert new data
            for date, row in ohlcv_df.iterrows():
                price = StockPrice(
                    symbol=symbol,
                    date=date,
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=int(row['volume']),
                    data_source=data_source
                )
                session.add(price)
            
            session.commit()
            logger.info(f"Cached {len(ohlcv_df)} price records for {symbol}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cache prices for {symbol}: {e}")
        finally:
            session.close()
    
    def get_cached_prices(
        self, 
        symbol: str, 
        days: int = 30,
        max_age_hours: int = 24
    ) -> Optional[pd.DataFrame]:
        """
        Get cached price data if available and fresh.
        
        Args:
            symbol: Stock symbol
            days: Number of days needed
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            DataFrame with OHLCV data or None if cache miss
        """
        session = get_session(self.db_path)
        
        try:
            # Check if we have recent data
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            prices = session.query(StockPrice).filter(
                StockPrice.symbol == symbol,
                StockPrice.created_at >= cutoff_time
            ).order_by(StockPrice.date.desc()).limit(days).all()
            
            if not prices or len(prices) < days * 0.7:  # Need at least 70% of requested days
                logger.info(f"Cache miss for {symbol} (found {len(prices)}/{days} days)")
                return None
            
            # Convert to DataFrame
            data = []
            for price in prices:
                data.append({
                    'open': price.open,
                    'high': price.high,
                    'low': price.low,
                    'close': price.close,
                    'volume': price.volume
                })
            
            df = pd.DataFrame(data, index=[p.date for p in prices])
            df = df.sort_index()
            
            logger.info(f"Cache hit for {symbol}: {len(df)} days")
            return df
            
        except Exception as e:
            logger.error(f"Failed to get cached prices for {symbol}: {e}")
            return None
        finally:
            session.close()
    
    def cache_financials(self, symbol: str, financials: Dict[str, Any]):
        """
        Cache financial ratios and metrics.
        
        Args:
            symbol: Stock symbol
            financials: Dictionary with financial data
        """
        session = get_session(self.db_path)
        
        try:
            # Update or create
            existing = session.query(StockFinancials).filter(
                StockFinancials.symbol == symbol
            ).first()
            
            if existing:
                # Update existing
                existing.pe = financials.get('pe')
                existing.pb = financials.get('pb')
                existing.roe = financials.get('roe')
                existing.roa = financials.get('roa')
                existing.eps = financials.get('eps')
                existing.dividend_yield = financials.get('dividend_yield')
                existing.revenue = financials.get('revenue')
                existing.net_income = financials.get('net_income')
                existing.market_cap = financials.get('market_cap')
                existing.data_source = financials.get('source', financials.get('data_source'))
                existing.is_synthetic = financials.get('source') == 'synthetic'
                existing.last_updated = datetime.utcnow()
            else:
                # Create new
                financial = StockFinancials(
                    symbol=symbol,
                    pe=financials.get('pe'),
                    pb=financials.get('pb'),
                    roe=financials.get('roe'),
                    roa=financials.get('roa'),
                    eps=financials.get('eps'),
                    dividend_yield=financials.get('dividend_yield'),
                    revenue=financials.get('revenue'),
                    net_income=financials.get('net_income'),
                    market_cap=financials.get('market_cap'),
                    data_source=financials.get('source', financials.get('data_source')),
                    is_synthetic=financials.get('source') == 'synthetic'
                )
                session.add(financial)
            
            session.commit()
            logger.info(f"Cached financials for {symbol}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cache financials for {symbol}: {e}")
        finally:
            session.close()
    
    def get_cached_financials(
        self, 
        symbol: str,
        max_age_hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached financial data if available and fresh.
        
        Args:
            symbol: Stock symbol
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            Dictionary with financial data or None if cache miss
        """
        session = get_session(self.db_path)
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            financial = session.query(StockFinancials).filter(
                StockFinancials.symbol == symbol,
                StockFinancials.last_updated >= cutoff_time
            ).first()
            
            if not financial:
                logger.info(f"Cache miss for {symbol} financials")
                return None
            
            logger.info(f"Cache hit for {symbol} financials")
            return financial.to_dict()
            
        except Exception as e:
            logger.error(f"Failed to get cached financials for {symbol}: {e}")
            return None
        finally:
            session.close()
    
    def cache_news(self, symbol: str, articles: List[Dict[str, Any]]):
        """
        Cache news articles.
        
        Args:
            symbol: Stock symbol
            articles: List of article dictionaries
        """
        session = get_session(self.db_path)
        
        try:
            # Delete old news (keep last 50 per symbol)
            old_news = session.query(NewsArticle).filter(
                NewsArticle.symbol == symbol
            ).order_by(NewsArticle.created_at.desc()).offset(50).all()
            
            for article in old_news:
                session.delete(article)
            
            # Insert new articles
            for article in articles:
                news = NewsArticle(
                    symbol=symbol,
                    title=article.get('title', ''),
                    url=article.get('url', ''),
                    source=article.get('source', ''),
                    published_date=article.get('published_date'),
                    content=article.get('content', ''),
                    is_demo=article.get('is_demo', False)
                )
                session.add(news)
            
            session.commit()
            logger.info(f"Cached {len(articles)} news articles for {symbol}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to cache news for {symbol}: {e}")
        finally:
            session.close()
    
    def get_cached_news(
        self, 
        symbol: str,
        max_articles: int = 10,
        max_age_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get cached news articles.
        
        Args:
            symbol: Stock symbol
            max_articles: Maximum number of articles to return
            max_age_hours: Maximum age of cache in hours
            
        Returns:
            List of article dictionaries
        """
        session = get_session(self.db_path)
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            articles = session.query(NewsArticle).filter(
                NewsArticle.symbol == symbol,
                NewsArticle.created_at >= cutoff_time
            ).order_by(NewsArticle.created_at.desc()).limit(max_articles).all()
            
            result = [article.to_dict() for article in articles]
            logger.info(f"Retrieved {len(result)} cached news articles for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get cached news for {symbol}: {e}")
            return []
        finally:
            session.close()
    
    def create_debate_session(
        self, 
        symbol: str, 
        period_days: int,
        rounds: int,
        data_source: str
    ) -> str:
        """
        Create a new debate session record.
        
        Args:
            symbol: Stock symbol
            period_days: Analysis period
            rounds: Number of debate rounds
            data_source: Source of data
            
        Returns:
            Session ID
        """
        session = get_session(self.db_path)
        session_id = str(uuid.uuid4())
        
        try:
            debate = DebateSession(
                session_id=session_id,
                symbol=symbol,
                period_days=period_days,
                rounds=rounds,
                status='running',
                data_source=data_source
            )
            session.add(debate)
            session.commit()
            logger.info(f"Created debate session {session_id} for {symbol}")
            return session_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create debate session: {e}")
            return session_id
        finally:
            session.close()
    
    def complete_debate_session(
        self,
        session_id: str,
        final_decision: str,
        final_confidence: float,
        transcript: List[Dict[str, Any]]
    ):
        """
        Mark debate session as complete and save results.
        
        Args:
            session_id: Session ID
            final_decision: Final recommendation (buy, hold, sell)
            final_confidence: Confidence level
            transcript: Complete debate transcript
        """
        session = get_session(self.db_path)
        
        try:
            # Update session
            debate = session.query(DebateSession).filter(
                DebateSession.session_id == session_id
            ).first()
            
            if debate:
                debate.status = 'completed'
                debate.final_decision = final_decision
                debate.final_confidence = final_confidence
                debate.completed_at = datetime.utcnow()
            
            # Save transcript
            transcript_record = DebateTranscript(
                session_id=session_id,
                transcript_json=json.dumps(transcript)
            )
            session.add(transcript_record)
            
            session.commit()
            logger.info(f"Completed debate session {session_id}")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to complete debate session: {e}")
        finally:
            session.close()
    
    def save_agent_analysis(
        self,
        session_id: str,
        agent_name: str,
        round_number: int,
        analysis: Dict[str, Any]
    ):
        """
        Save individual agent analysis.
        
        Args:
            session_id: Debate session ID
            agent_name: Agent name
            round_number: Round number
            analysis: Analysis dictionary
        """
        session = get_session(self.db_path)
        
        try:
            agent_analysis = AgentAnalysis(
                session_id=session_id,
                agent_name=agent_name,
                round_number=round_number,
                signal=analysis.get('signal', analysis.get('bias', analysis.get('sentiment_label'))),
                confidence=analysis.get('confidence', 0),
                rationale=analysis.get('rationale', ''),
                indicators=analysis.get('indicators', {})
            )
            session.add(agent_analysis)
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save agent analysis: {e}")
        finally:
            session.close()
    
    def get_recent_debates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent debate sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of debate session dictionaries
        """
        session = get_session(self.db_path)
        
        try:
            debates = session.query(DebateSession).order_by(
                DebateSession.started_at.desc()
            ).limit(limit).all()
            
            return [debate.to_dict() for debate in debates]
            
        except Exception as e:
            logger.error(f"Failed to get recent debates: {e}")
            return []
        finally:
            session.close()
