"""
FastAPI application for Analysis Service.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import requests

from app.analyzers.fundamental_analyzer import FundamentalAnalyzer
from app.analyzers.technical_analyzer import TechnicalAnalyzer
from app.analyzers.sentiment_analyzer import SentimentAnalyzer
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="Stock Debate Analysis Service",
    description="Analysis service for fundamental, technical, and sentiment analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Analyzers
fundamental_analyzer = FundamentalAnalyzer()
technical_analyzer = TechnicalAnalyzer()
sentiment_analyzer = SentimentAnalyzer()

# Data service URL
DATA_SERVICE_URL = "http://data-service:8001"  # Docker internal network


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Analysis Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/v1/analyze/{symbol}")
async def analyze_stock(symbol: str):
    """
    Perform comprehensive analysis on a stock.
    Fetches data from data-service and runs all analyzers.
    """
    try:
        logger.info(f"Starting comprehensive analysis for {symbol}")
        
        # Fetch financial data from data-service
        financial_data = await _fetch_financial_data(symbol)
        
        # Fetch price data from data-service
        price_data = await _fetch_price_data(symbol)
        
        # Fetch news data from data-service
        news_data = await _fetch_news_data(symbol)
        
        # Run analyses
        result = {
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Fundamental analysis
        try:
            logger.info(f"Running fundamental analysis for {symbol}")
            result["fundamental"] = fundamental_analyzer.analyze(financial_data)
        except Exception as e:
            logger.error(f"Fundamental analysis failed: {e}")
            result["fundamental"] = {"error": str(e)}
        
        # Technical analysis
        try:
            logger.info(f"Running technical analysis for {symbol}")
            if price_data:
                df = pd.DataFrame(price_data)
                result["technical"] = technical_analyzer.analyze(df)
            else:
                result["technical"] = {"error": "No price data available"}
        except Exception as e:
            logger.error(f"Technical analysis failed: {e}")
            result["technical"] = {"error": str(e)}
        
        # Sentiment analysis
        try:
            logger.info(f"Running sentiment analysis for {symbol}")
            result["sentiment"] = sentiment_analyzer.analyze(news_data)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            result["sentiment"] = {"error": str(e)}
        
        # Generate combined recommendation
        result["combined_recommendation"] = _generate_combined_recommendation(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/fundamental/{symbol}")
async def analyze_fundamental(symbol: str):
    """Perform fundamental analysis only."""
    try:
        financial_data = await _fetch_financial_data(symbol)
        result = fundamental_analyzer.analyze(financial_data)
        return {"symbol": symbol, "analysis": result}
    except Exception as e:
        logger.error(f"Error in fundamental analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/technical/{symbol}")
async def analyze_technical(symbol: str, days: int = 30):
    """Perform technical analysis only."""
    try:
        price_data = await _fetch_price_data(symbol, days)
        if not price_data:
            raise ValueError("No price data available")
        
        df = pd.DataFrame(price_data)
        result = technical_analyzer.analyze(df)
        return {"symbol": symbol, "analysis": result}
    except Exception as e:
        logger.error(f"Error in technical analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sentiment/{symbol}")
async def analyze_sentiment(symbol: str):
    """Perform sentiment analysis only."""
    try:
        news_data = await _fetch_news_data(symbol)
        result = sentiment_analyzer.analyze(news_data)
        return {"symbol": symbol, "analysis": result}
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions to fetch data from data-service

async def _fetch_financial_data(symbol: str) -> Dict[str, Any]:
    """Fetch financial data from data-service."""
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/api/v1/financial/{symbol}", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        logger.warning("Data service not available, using demo data")
        return _demo_financial_data()
    except Exception as e:
        logger.error(f"Error fetching financial data: {e}")
        return _demo_financial_data()


async def _fetch_price_data(symbol: str, days: int = 30) -> list:
    """Fetch price data from data-service."""
    try:
        response = requests.get(
            f"{DATA_SERVICE_URL}/api/v1/prices/{symbol}",
            params={"days": days},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("prices", [])
    except requests.exceptions.ConnectionError:
        logger.warning("Data service not available, using demo data")
        return _demo_price_data()
    except Exception as e:
        logger.error(f"Error fetching price data: {e}")
        return _demo_price_data()


async def _fetch_news_data(symbol: str) -> list:
    """Fetch news data from data-service."""
    try:
        response = requests.get(f"{DATA_SERVICE_URL}/api/v1/news/{symbol}", timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("articles", [])
    except requests.exceptions.ConnectionError:
        logger.warning("Data service not available, using demo data")
        return []
    except Exception as e:
        logger.error(f"Error fetching news data: {e}")
        return []


def _generate_combined_recommendation(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Generate combined recommendation from all analyses."""
    scores = []
    ratings = []
    
    # Extract scores
    if "fundamental" in analysis and "overall_score" in analysis["fundamental"]:
        fund_score = analysis["fundamental"]["overall_score"]["score"]
        scores.append(fund_score)
        ratings.append(analysis["fundamental"]["overall_score"]["rating"])
    
    if "technical" in analysis and "overall_score" in analysis["technical"]:
        tech_score = analysis["technical"]["overall_score"]["score"]
        scores.append(tech_score)
        ratings.append(analysis["technical"]["overall_score"]["rating"])
    
    if "sentiment" in analysis and "overall_score" in analysis["sentiment"]:
        sent_score = analysis["sentiment"]["overall_score"]["score"]
        scores.append(sent_score)
        ratings.append(analysis["sentiment"]["overall_score"]["rating"])
    
    if not scores:
        return {
            "overall_score": 50.0,
            "recommendation": "Hold",
            "confidence": "Low",
            "summary": "Insufficient data for combined analysis"
        }
    
    # Calculate weighted average (fundamental 40%, technical 35%, sentiment 25%)
    weights = [0.40, 0.35, 0.25]
    weighted_score = sum(s * w for s, w in zip(scores, weights[:len(scores)])) / sum(weights[:len(scores)])
    
    # Determine recommendation
    if weighted_score >= 70:
        recommendation = "Strong Buy"
    elif weighted_score >= 60:
        recommendation = "Buy"
    elif weighted_score >= 45:
        recommendation = "Hold"
    elif weighted_score >= 35:
        recommendation = "Sell"
    else:
        recommendation = "Strong Sell"
    
    # Generate summary
    summary = f"Combined analysis from {len(scores)} methodologies: "
    summary += ", ".join(ratings)
    
    return {
        "overall_score": round(weighted_score, 2),
        "recommendation": recommendation,
        "confidence": "High" if len(scores) == 3 else "Medium",
        "summary": summary,
        "individual_scores": {
            "fundamental": scores[0] if len(scores) > 0 else None,
            "technical": scores[1] if len(scores) > 1 else None,
            "sentiment": scores[2] if len(scores) > 2 else None,
        }
    }


# Demo data functions

def _demo_financial_data() -> Dict[str, Any]:
    """Return demo financial data."""
    return {
        "metrics": {
            "roe": 18.5,
            "roa": 8.2,
            "netProfitMargin": 12.5,
            "grossMargin": 35.0,
            "operatingMargin": 15.0,
        },
        "ratios": {
            "currentRatio": 1.8,
            "quickRatio": 1.2,
            "debtToEquity": 0.6,
            "debtToAssets": 0.35,
            "pe": 14.5,
            "pb": 2.2,
            "assetTurnover": 1.1,
        }
    }


def _demo_price_data() -> list:
    """Return demo price data."""
    import numpy as np
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    base_price = 58000
    
    prices = []
    for i, date in enumerate(dates):
        price = base_price + np.random.randn() * 1000 + i * 100
        prices.append({
            "date": date.isoformat(),
            "open": price - 200,
            "high": price + 500,
            "low": price - 500,
            "close": price,
            "volume": int(3000000 + np.random.randn() * 500000)
        })
    
    return prices


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
