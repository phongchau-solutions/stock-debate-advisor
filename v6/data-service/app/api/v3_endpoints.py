"""
FastAPI endpoints for local JSON data (company_info, financial_reports, ohlc_prices)
Provides REST API access to stock data from data_store directory.
"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from app.services.local_data_service import LocalDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["data"])

# Initialize service
data_service = LocalDataService()


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get("/stocks/list")
async def list_all_stocks() -> Dict[str, Any]:
    """
    List all available stocks with basic information.
    
    Returns:
        Dictionary with stock list and summaries
    
    Example:
        GET /api/v1/stocks/list
    """
    try:
        stocks = data_service.get_all_stocks_summary()
        return {
            'status': 'success',
            'total_stocks': len(stocks),
            'stocks': stocks
        }
    except Exception as e:
        logger.error(f"Error listing stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/search")
async def search_stocks(
    query: str = Query(..., min_length=1, description="Search query (symbol or company name)"),
    limit: int = Query(10, ge=1, le=30, description="Maximum number of results")
) -> Dict[str, Any]:
    """
    Search for stocks by symbol or company name.
    
    Args:
        query: Search term (e.g., 'ACB', 'Bank', 'MBB')
        limit: Maximum results to return (default: 10, max: 30)
    
    Returns:
        Dictionary with search results
    
    Example:
        GET /api/v1/stocks/search?query=ACB
        GET /api/v1/stocks/search?query=Bank&limit=20
    """
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = data_service.search_companies(query, limit)
        return {
            'status': 'success',
            'query': query,
            'result_count': len(results),
            'results': results
        }
    except Exception as e:
        logger.error(f"Error searching stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMPANY INFO ENDPOINTS
# ============================================================================

@router.get("/company/{symbol}")
async def get_company_info(symbol: str) -> Dict[str, Any]:
    """
    Get company information by stock symbol.
    
    Args:
        symbol: Stock symbol (e.g., 'ACB', 'ACB.VN', 'MBB')
    
    Returns:
        Company information (name, sector, market cap, website, etc.)
    
    Example:
        GET /api/v1/company/ACB
        GET /api/v1/company/MBB.VN
    """
    try:
        company = data_service.get_company_info(symbol)
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company info not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': company
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FINANCIAL REPORTS ENDPOINTS
# ============================================================================

@router.get("/financials/{symbol}")
async def get_all_financial_reports(symbol: str) -> Dict[str, Any]:
    """
    Get all financial reports for a stock (quarterly, annual, metrics, dividends, splits).
    
    Args:
        symbol: Stock symbol (e.g., 'ACB', 'ACB.VN')
    
    Returns:
        Complete financial data including:
        - Quarterly financial statements
        - Annual financial statements
        - Financial metrics (PE ratio, dividend yield, etc.)
        - Dividend history
        - Stock split history
    
    Example:
        GET /api/v1/financials/ACB
    """
    try:
        reports = data_service.get_financial_reports(symbol)
        if not reports:
            raise HTTPException(
                status_code=404,
                detail=f"Financial reports not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': reports
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching financial reports for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financials/quarterly/{symbol}")
async def get_quarterly_reports(
    symbol: str,
    limit: int = Query(8, ge=1, le=20, description="Max quarters to return")
) -> Dict[str, Any]:
    """
    Get quarterly financial reports for a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'ACB')
        limit: Maximum number of quarters to return (default: 8, max: 20)
    
    Returns:
        Quarterly financial statements with revenue, net income, assets, cash flow, etc.
    
    Example:
        GET /api/v1/financials/quarterly/ACB
        GET /api/v1/financials/quarterly/MBB?limit=12
    """
    try:
        quarterly = data_service.get_quarterly_reports(symbol, limit)
        if not quarterly:
            raise HTTPException(
                status_code=404,
                detail=f"Quarterly reports not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': quarterly
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quarterly reports for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financials/annual/{symbol}")
async def get_annual_reports(
    symbol: str,
    limit: int = Query(10, ge=1, le=20, description="Max years to return")
) -> Dict[str, Any]:
    """
    Get annual financial reports for a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'ACB')
        limit: Maximum number of years to return (default: 10, max: 20)
    
    Returns:
        Annual financial statements with revenue, net income, assets, etc.
    
    Example:
        GET /api/v1/financials/annual/ACB
        GET /api/v1/financials/annual/MBB?limit=5
    """
    try:
        annual = data_service.get_annual_reports(symbol, limit)
        if not annual:
            raise HTTPException(
                status_code=404,
                detail=f"Annual reports not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': annual
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching annual reports for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financials/metrics/{symbol}")
async def get_financial_metrics(symbol: str) -> Dict[str, Any]:
    """
    Get financial metrics for a stock (PE ratio, dividend yield, debt-to-equity, etc.).
    
    Args:
        symbol: Stock symbol (e.g., 'ACB')
    
    Returns:
        Financial metrics including valuation and performance ratios
    
    Example:
        GET /api/v1/financials/metrics/ACB
    """
    try:
        metrics = data_service.get_financial_metrics(symbol)
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"Financial metrics not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': metrics
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching metrics for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DIVIDEND & SPLIT ENDPOINTS
# ============================================================================

@router.get("/dividends/{symbol}")
async def get_dividends(symbol: str) -> Dict[str, Any]:
    """
    Get dividend history for a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'ACB')
    
    Returns:
        Dividend records with ex-date, amount, and currency
    
    Example:
        GET /api/v1/dividends/ACB
    """
    try:
        dividends = data_service.get_dividends(symbol)
        if not dividends:
            raise HTTPException(
                status_code=404,
                detail=f"Dividend data not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': dividends
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dividends for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/splits/{symbol}")
async def get_stock_splits(symbol: str) -> Dict[str, Any]:
    """
    Get stock split history for a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'ACB')
    
    Returns:
        Stock split records with ex-date and split ratio
    
    Example:
        GET /api/v1/splits/ACB
    """
    try:
        splits = data_service.get_stock_splits(symbol)
        if not splits:
            raise HTTPException(
                status_code=404,
                detail=f"Stock split data not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': splits
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching splits for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRICE DATA ENDPOINTS
# ============================================================================

@router.get("/prices/{symbol}")
async def get_ohlc_prices(
    symbol: str,
    limit: int = Query(249, ge=1, le=249, description="Max price records to return")
) -> Dict[str, Any]:
    """
    Get OHLC (Open, High, Low, Close) price data for a stock.
    
    Args:
        symbol: Stock symbol (e.g., 'ACB')
        limit: Maximum number of days to return (default: 249, max: 249)
    
    Returns:
        Daily OHLC price data with volume and change percentage
    
    Example:
        GET /api/v1/prices/ACB
        GET /api/v1/prices/ACB?limit=30
    """
    try:
        prices = data_service.get_ohlc_prices(symbol, limit)
        if not prices:
            raise HTTPException(
                status_code=404,
                detail=f"Price data not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': prices
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prices for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NEWS ENDPOINTS
# ============================================================================

@router.get("/news/{symbol}")
async def get_news(symbol: str) -> Dict[str, Any]:
    """
    Get news data for a stock (if available).
    
    Args:
        symbol: Stock symbol (e.g., 'MBB')
    
    Returns:
        News articles with date, title, source, and URL
    
    Example:
        GET /api/v1/news/MBB
    """
    try:
        news = data_service.get_news_data(symbol)
        if not news:
            raise HTTPException(
                status_code=404,
                detail=f"News data not found for symbol: {symbol}"
            )
        
        return {
            'status': 'success',
            'data': news
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMBINED DATA ENDPOINTS
# ============================================================================

@router.get("/stock/{symbol}/full")
async def get_full_stock_data(symbol: str) -> Dict[str, Any]:
    """
    Get complete data for a stock including company info, financials, and prices.
    
    Args:
        symbol: Stock symbol (e.g., 'ACB')
    
    Returns:
        Complete stock data bundle
    
    Example:
        GET /api/v1/stock/ACB/full
    """
    try:
        company = data_service.get_company_info(symbol)
        financials = data_service.get_financial_reports(symbol)
        prices = data_service.get_ohlc_prices(symbol, 249)
        news = data_service.get_news_data(symbol)
        
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Stock not found: {symbol}"
            )
        
        return {
            'status': 'success',
            'symbol': symbol,
            'company_info': company,
            'financial_reports': financials,
            'ohlc_prices': prices,
            'news_data': news
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching full stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
