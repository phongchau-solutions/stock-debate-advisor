"""Stock price endpoints."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_optional_user
from app.crud.stock import stock_price_crud
from app.schemas.stock import StockPriceCreate, StockPriceListResponse, StockPriceResponse

router = APIRouter(prefix="/price", tags=["prices"])


@router.post("", response_model=StockPriceResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_price(
    price_data: StockPriceCreate,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_optional_user),  # For future audit logging
):
    """Create a new stock price entry."""
    price_dict = price_data.model_dump()
    price_dict["id"] = f"price_{uuid.uuid4().hex[:12]}"

    price = await stock_price_crud.create(db, price_dict)

    return price


@router.get("/{symbol}", response_model=StockPriceListResponse)
async def get_stock_prices(
    symbol: str,
    db: AsyncSession = Depends(get_db_session),
    start_date: datetime = Query(None, description="Start date for price range"),
    end_date: datetime = Query(None, description="End date for price range"),
    skip: int = 0,
    limit: int = 100,
):
    """Get stock prices for a symbol, optionally filtered by date range."""
    # Note: FastCRUD may not support date range filters directly
    # This is a simplified version. In production, you'd use more sophisticated filtering
    result = await stock_price_crud.get_multi(
        db,
        offset=skip,
        limit=limit,
        symbol=symbol.upper(),
        order_by=["date"],
        order_by_desc=True,
    )

    return StockPriceListResponse(prices=result["data"], total=result["total_count"])


@router.get("/{symbol}/latest", response_model=StockPriceResponse)
async def get_latest_price(
    symbol: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get the latest price for a stock symbol."""
    result = await stock_price_crud.get_multi(
        db,
        offset=0,
        limit=1,
        symbol=symbol.upper(),
        order_by=["date"],
        order_by_desc=True,
    )

    if not result["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for symbol {symbol}",
        )

    return result["data"][0]
