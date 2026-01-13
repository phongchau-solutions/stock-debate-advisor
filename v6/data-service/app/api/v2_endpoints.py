"""
FastAPI endpoints for the new data models
Provides REST API access to all data: company info, financial reports, prices, news
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from app.db.database import get_db_session
from app.db import models
from app.services.integrated_data_service import IntegratedDataService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["data"])


# ============================================================================
# COMPANY INFO ENDPOINTS
# ============================================================================

@router.get("/company/{symbol}")
async def get_company_info(symbol: str, db: Session = Depends(get_db_session)):
    """Get company information."""
    try:
        company = db.query(models.CompanyInfo).filter(
            models.CompanyInfo.symbol == symbol
        ).first()
        
        if not company:
            raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
        
        return {
            'symbol': company.symbol,
            'name': company.name,
            'english_name': company.english_name,
            'industry': company.industry,
            'sector': company.sector,
            'market_cap': company.market_cap,
            'market_cap_usd': company.market_cap_usd,
            'employees': company.employees,
            'website': company.website,
            'description': company.description,
            'updated_at': company.updated_at.isoformat() if company.updated_at else None,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FINANCIAL REPORTS ENDPOINTS
# ============================================================================

@router.get("/financials/quarterly/{symbol}")
async def get_quarterly_reports(
    symbol: str,
    limit: int = Query(8, le=20),
    db: Session = Depends(get_db_session)
):
    """Get quarterly financial reports."""
    try:
        reports = db.query(models.QuarterlyFinancialReport).filter(
            models.QuarterlyFinancialReport.symbol == symbol
        ).order_by(
            desc(models.QuarterlyFinancialReport.period_end_date)
        ).limit(limit).all()
        
        if not reports:
            raise HTTPException(status_code=404, detail=f"No quarterly reports found for {symbol}")
        
        return {
            'symbol': symbol,
            'data_type': 'quarterly',
            'report_count': len(reports),
            'reports': [
                {
                    'period_end_date': r.period_end_date.isoformat(),
                    'fiscal_year': r.fiscal_year,
                    'fiscal_quarter': r.fiscal_quarter,
                    'revenue': r.revenue,
                    'operating_income': r.operating_income,
                    'net_income': r.net_income,
                    'eps': r.eps,
                    'total_assets': r.total_assets,
                    'total_equity': r.total_equity,
                    'operating_cash_flow': r.operating_cash_flow,
                    'free_cash_flow': r.free_cash_flow,
                    'updated_at': r.updated_at.isoformat() if r.updated_at else None,
                }
                for r in reports
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quarterly reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financials/annual/{symbol}")
async def get_annual_reports(
    symbol: str,
    limit: int = Query(5, le=20),
    db: Session = Depends(get_db_session)
):
    """Get annual financial reports."""
    try:
        reports = db.query(models.AnnualFinancialReport).filter(
            models.AnnualFinancialReport.symbol == symbol
        ).order_by(
            desc(models.AnnualFinancialReport.fiscal_year)
        ).limit(limit).all()
        
        if not reports:
            raise HTTPException(status_code=404, detail=f"No annual reports found for {symbol}")
        
        return {
            'symbol': symbol,
            'data_type': 'annual',
            'report_count': len(reports),
            'reports': [
                {
                    'fiscal_year': r.fiscal_year,
                    'period_end_date': r.period_end_date.isoformat(),
                    'revenue': r.revenue,
                    'operating_income': r.operating_income,
                    'net_income': r.net_income,
                    'eps': r.eps,
                    'total_assets': r.total_assets,
                    'total_equity': r.total_equity,
                    'operating_cash_flow': r.operating_cash_flow,
                    'free_cash_flow': r.free_cash_flow,
                    'updated_at': r.updated_at.isoformat() if r.updated_at else None,
                }
                for r in reports
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching annual reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/financials/metrics/{symbol}")
async def get_financial_metrics(
    symbol: str,
    limit: int = Query(1, le=100),
    db: Session = Depends(get_db_session)
):
    """Get financial metrics."""
    try:
        metrics = db.query(models.FinancialMetrics).filter(
            models.FinancialMetrics.symbol == symbol
        ).order_by(
            desc(models.FinancialMetrics.metric_date)
        ).limit(limit).all()
        
        if not metrics:
            raise HTTPException(status_code=404, detail=f"No metrics found for {symbol}")
        
        return {
            'symbol': symbol,
            'data_type': 'metrics',
            'metric_count': len(metrics),
            'metrics': [
                {
                    'metric_date': m.metric_date.isoformat(),
                    'pe_ratio': m.pe_ratio,
                    'pb_ratio': m.pb_ratio,
                    'ps_ratio': m.ps_ratio,
                    'roe': m.roe,
                    'roa': m.roa,
                    'roic': m.roic,
                    'gross_margin': m.gross_margin,
                    'operating_margin': m.operating_margin,
                    'net_margin': m.net_margin,
                    'current_ratio': m.current_ratio,
                    'debt_to_equity': m.debt_to_equity,
                }
                for m in metrics
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# STOCK PRICE ENDPOINTS
# ============================================================================

@router.get("/prices/{symbol}")
async def get_stock_prices(
    symbol: str,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db_session)
):
    """Get historical stock prices."""
    try:
        prices = db.query(models.StockPrice).filter(
            models.StockPrice.symbol == symbol
        ).order_by(
            desc(models.StockPrice.price_date)
        ).limit(limit).all()
        
        if not prices:
            raise HTTPException(status_code=404, detail=f"No prices found for {symbol}")
        
        return {
            'symbol': symbol,
            'data_type': 'prices',
            'record_count': len(prices),
            'prices': [
                {
                    'date': p.price_date.isoformat(),
                    'open': p.open_price,
                    'high': p.high_price,
                    'low': p.low_price,
                    'close': p.close_price,
                    'adj_close': p.adj_close_price,
                    'volume': p.volume,
                }
                for p in prices
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dividends/{symbol}")
async def get_dividends(
    symbol: str,
    db: Session = Depends(get_db_session)
):
    """Get dividend history."""
    try:
        dividends = db.query(models.Dividend).filter(
            models.Dividend.symbol == symbol
        ).order_by(
            desc(models.Dividend.ex_date)
        ).all()
        
        if not dividends:
            raise HTTPException(status_code=404, detail=f"No dividends found for {symbol}")
        
        return {
            'symbol': symbol,
            'data_type': 'dividends',
            'record_count': len(dividends),
            'dividends': [
                {
                    'ex_date': d.ex_date.isoformat(),
                    'payment_date': d.payment_date.isoformat() if d.payment_date else None,
                    'dividend_per_share': d.dividend_per_share,
                    'dividend_type': d.dividend_type,
                }
                for d in dividends
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dividends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NEWS ENDPOINTS
# ============================================================================

@router.get("/news/{symbol}")
async def get_company_news(
    symbol: str,
    limit: int = Query(50, le=500),
    days: int = Query(30, le=365),
    source: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """Get company news."""
    try:
        query = db.query(models.CompanyNews).filter(
            and_(
                models.CompanyNews.symbol == symbol,
                models.CompanyNews.crawled_at >= datetime.now() - timedelta(days=days),
                models.CompanyNews.is_archived == 0
            )
        )
        
        if source:
            query = query.filter(models.CompanyNews.source == source)
        
        news = query.order_by(
            desc(models.CompanyNews.published_at)
        ).limit(limit).all()
        
        if not news:
            raise HTTPException(status_code=404, detail=f"No news found for {symbol}")
        
        return {
            'symbol': symbol,
            'data_type': 'news',
            'query_days': days,
            'article_count': len(news),
            'articles': [
                {
                    'title': n.title,
                    'url': n.url,
                    'source': n.source,
                    'source_name': n.source_name,
                    'published_at': n.published_at.isoformat() if n.published_at else None,
                    'crawled_at': n.crawled_at.isoformat(),
                    'sentiment_score': n.sentiment_score,
                    'sentiment_label': n.sentiment_label,
                    'keywords': n.keywords,
                    'content_length': n.content_length,
                }
                for n in news
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/sources")
async def get_news_sources(db: Session = Depends(get_db_session)):
    """Get available news sources."""
    try:
        from sqlalchemy import func
        sources = db.query(
            models.CompanyNews.source,
            models.CompanyNews.source_name,
            func.count(models.CompanyNews.id).label('article_count')
        ).group_by(
            models.CompanyNews.source,
            models.CompanyNews.source_name
        ).all()
        
        return {
            'sources': [
                {
                    'source': s.source,
                    'source_name': s.source_name,
                    'article_count': s.article_count
                }
                for s in sources
            ]
        }
    
    except Exception as e:
        logger.error(f"Error fetching sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BULK DATA ENDPOINTS
# ============================================================================

@router.get("/data/{symbol}")
async def get_all_data(
    symbol: str,
    include_news: bool = Query(True),
    price_limit: int = Query(100, le=1000),
    news_limit: int = Query(50, le=500),
    db: Session = Depends(get_db_session)
):
    """Get all available data for a symbol."""
    try:
        service = IntegratedDataService(db)
        
        # Fetch all data
        company = db.query(models.CompanyInfo).filter(
            models.CompanyInfo.symbol == symbol
        ).first()
        
        if not company:
            raise HTTPException(status_code=404, detail=f"Company {symbol} not found")
        
        quarterly = db.query(models.QuarterlyFinancialReport).filter(
            models.QuarterlyFinancialReport.symbol == symbol
        ).order_by(desc(models.QuarterlyFinancialReport.period_end_date)).limit(8).all()
        
        annual = db.query(models.AnnualFinancialReport).filter(
            models.AnnualFinancialReport.symbol == symbol
        ).order_by(desc(models.AnnualFinancialReport.fiscal_year)).limit(5).all()
        
        metrics = db.query(models.FinancialMetrics).filter(
            models.FinancialMetrics.symbol == symbol
        ).order_by(desc(models.FinancialMetrics.metric_date)).first()
        
        prices = db.query(models.StockPrice).filter(
            models.StockPrice.symbol == symbol
        ).order_by(desc(models.StockPrice.price_date)).limit(price_limit).all()
        
        dividends = db.query(models.Dividend).filter(
            models.Dividend.symbol == symbol
        ).order_by(desc(models.Dividend.ex_date)).all()
        
        news = []
        if include_news:
            news = db.query(models.CompanyNews).filter(
                and_(
                    models.CompanyNews.symbol == symbol,
                    models.CompanyNews.is_archived == 0
                )
            ).order_by(
                desc(models.CompanyNews.published_at)
            ).limit(news_limit).all()
        
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'company': {
                'name': company.name,
                'sector': company.sector,
                'industry': company.industry,
                'market_cap': company.market_cap,
            },
            'summary': {
                'quarterly_reports': len(quarterly),
                'annual_reports': len(annual),
                'has_metrics': metrics is not None,
                'price_records': len(prices),
                'dividend_records': len(dividends),
                'news_count': len(news),
            },
            'data': {
                'quarterly_reports': len(quarterly),
                'annual_reports': len(annual),
                'stock_prices': len(prices),
                'dividends': len(dividends),
                'news_articles': len(news),
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching all data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PIPELINE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/pipeline/logs")
async def get_pipeline_logs(
    limit: int = Query(100, le=1000),
    pipeline_name: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """Get pipeline execution logs."""
    try:
        query = db.query(models.DataPipelineLog)
        
        if pipeline_name:
            query = query.filter(models.DataPipelineLog.pipeline_name == pipeline_name)
        
        if status:
            query = query.filter(models.DataPipelineLog.status == status)
        
        logs = query.order_by(
            desc(models.DataPipelineLog.created_at)
        ).limit(limit).all()
        
        return {
            'log_count': len(logs),
            'logs': [
                {
                    'pipeline_name': log.pipeline_name,
                    'pipeline_type': log.pipeline_type,
                    'symbol': log.symbol,
                    'status': log.status,
                    'records_processed': log.records_processed,
                    'records_failed': log.records_failed,
                    'duration_seconds': log.duration_seconds,
                    'started_at': log.started_at.isoformat() if log.started_at else None,
                    'completed_at': log.completed_at.isoformat() if log.completed_at else None,
                }
                for log in logs
            ]
        }
    
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
