"""
FastAPI application for Data Service.
Provides REST API for financial data retrieval and management.
"""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

from app.db.database import get_db_session, engine
import os
import json
from app.db import models
from app.clients.yahoo_finance_client import YahooFinanceClient
from app.services.financial_data_service import FinancialDataService
from app.api import v2_endpoints

# Create tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Debate Data Service",
    description="Comprehensive data service for financial data, news, and analysis using Yahoo Finance API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v2 API routes
app.include_router(v2_endpoints.router)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Local data mode
LOCAL_DATA_MODE = os.getenv("LOCAL_DATA_MODE", "false").lower() == "true"

# Clients and Services
yahoo_client = YahooFinanceClient()
financial_service = FinancialDataService(cache_dir=Path(__file__).parent.parent / 'data' / 'financial')


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Data Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}



@app.get("/api/v1/financial/{symbol}")
async def get_financial_data(
    symbol: str,
    db: Session = Depends(get_db_session)
):
    """Get financial data for a symbol."""
    if LOCAL_DATA_MODE:
        # Serve from local file if available
        file_path = os.path.join(os.path.dirname(__file__), "../data/financial", f"{symbol}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            raise HTTPException(status_code=404, detail=f"Local data file not found for {symbol}")
    try:
        # Try to get from database first
        latest_data = db.query(models.FinancialData).filter(
            models.FinancialData.symbol == symbol
        ).order_by(models.FinancialData.created_at.desc()).first()
        # If no data or data is old (>24 hours), fetch new data
        if not latest_data or (datetime.utcnow() - latest_data.created_at).total_seconds() > 86400:
            logger.info(f"Fetching fresh financial data for {symbol} from Yahoo Finance")
            data = financial_service.fetch_and_cache(symbol)
            # Store in database
            for data_type in ['info', 'prices', 'quarterly', 'annual', 'metrics', 'dividends', 'splits']:
                if data.get(data_type) and data[data_type]:
                    financial_record = models.FinancialData(
                        symbol=symbol,
                        data_type=data_type,
                        data=data[data_type]
                    )
                    db.add(financial_record)
            db.commit()
            return data
        # Return cached data
        logger.info(f"Returning cached financial data for {symbol}")
        result = {}
        records = db.query(models.FinancialData).filter(
            models.FinancialData.symbol == symbol
        ).order_by(models.FinancialData.created_at.desc()).limit(10).all()
        for record in records:
            result[record.data_type] = record.data
        return result
    except Exception as e:
        logger.error(f"Error fetching financial data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/news/{symbol}")
async def get_news(
    symbol: str,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db_session)
):
    """Get news articles for a symbol."""
    if LOCAL_DATA_MODE:
        file_path = os.path.join(os.path.dirname(__file__), "../data/news", f"{symbol}.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
                # Optionally limit articles
                if "articles" in data:
                    data["articles"] = data["articles"][:limit]
                return data
        else:
            raise HTTPException(status_code=404, detail=f"Local news file not found for {symbol}")
    try:
        # Get from database
        articles = db.query(models.NewsArticle).filter(
            models.NewsArticle.symbol == symbol
        ).order_by(models.NewsArticle.created_at.desc()).limit(limit).all()
        # If no recent articles, crawl new ones
        if not articles or (datetime.utcnow() - articles[0].created_at).total_seconds() > 3600:
            logger.info(f"Crawling fresh news for {symbol}")
            new_articles = news_crawler.crawl_all_sources(symbol, max_per_source=5)
            
            for article in new_articles:
                news_record = models.NewsArticle(
                    symbol=article['symbol'],
                    title=article['title'],
                    url=article['url'],
                    content=article['content'],
                    source=article['source'],
                    published_at=article['published_at']
                )
                db.add(news_record)
            
            db.commit()
            articles = new_articles
        else:
            # Convert SQLAlchemy objects to dicts
            articles = [
                {
                    'id': a.id,
                    'symbol': a.symbol,
                    'title': a.title,
                    'url': a.url,
                    'content': a.content,
                    'source': a.source,
                    'published_at': a.published_at.isoformat() if a.published_at else None,
                    'sentiment_score': a.sentiment_score,
                }
                for a in articles
            ]
        
        return {"symbol": symbol, "count": len(articles), "articles": articles}
        
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/prices/{symbol}")
async def get_price_data(
    symbol: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db_session)
):
    """Get historical price data for a symbol."""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        prices = db.query(models.PriceData).filter(
            models.PriceData.symbol == symbol,
            models.PriceData.date >= start_date
        ).order_by(models.PriceData.date.desc()).all()
        
        price_list = [
            {
                'date': p.date.isoformat(),
                'open': p.open_price,
                'high': p.high_price,
                'low': p.low_price,
                'close': p.close_price,
                'volume': p.volume,
            }
            for p in prices
        ]
        
        return {"symbol": symbol, "days": days, "count": len(price_list), "prices": price_list}
        
    except Exception as e:
        logger.error(f"Error fetching price data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/crawl/{symbol}")
async def trigger_crawl(symbol: str, db: Session = Depends(get_db_session)):
    """Manually trigger a data crawl for a symbol."""
    try:
        logger.info(f"Triggering manual crawl for {symbol}")
        
        # Fetch financial data
        financial_data = financial_service.fetch_and_cache(symbol)
        
        # Crawl news
        news_articles = news_crawler.crawl_all_sources(symbol, max_per_source=5)
        
        # Store in database
        for data_type in ['balance_sheet', 'income_statement', 'cash_flow', 'metrics']:
            if financial_data.get(data_type):
                financial_record = models.FinancialData(
                    symbol=symbol,
                    data_type=data_type,
                    data=financial_data[data_type]
                )
                db.add(financial_record)
        
        for article in news_articles:
            news_record = models.NewsArticle(
                symbol=article['symbol'],
                title=article['title'],
                url=article['url'],
                content=article['content'],
                source=article['source'],
                published_at=article['published_at']
            )
            db.add(news_record)
        
        db.commit()
        
        return {
            "status": "success",
            "symbol": symbol,
            "financial_records": len([k for k in financial_data.keys() if financial_data.get(k)]),
            "news_articles": len(news_articles)
        }
        
    except Exception as e:
        logger.error(f"Error in manual crawl: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/company/{symbol}")
async def get_company_info(symbol: str, db: Session = Depends(get_db_session)):
    """Get company information."""
    try:
        company = db.query(models.CompanyInfo).filter(
            models.CompanyInfo.symbol == symbol
        ).first()
        
        if not company:
            # Fetch from Yahoo Finance
            data = yahoo_client.get_ticker_info(symbol)
            company = models.CompanyInfo(
                symbol=symbol,
                name=data.get('longName', ''),
                industry=data.get('industry', ''),
                sector=data.get('sector', ''),
                market_cap=data.get('marketCap'),
                description=data.get('longBusinessSummary', '')
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        
        return {
            'symbol': company.symbol,
            'name': company.name,
            'industry': company.industry,
            'sector': company.sector,
            'market_cap': company.market_cap,
            'description': company.description,
        }
        
    except Exception as e:
        logger.error(f"Error fetching company info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
