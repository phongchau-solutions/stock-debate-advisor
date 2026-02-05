"""Company information endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.crud.stock import stock_crud
from app.schemas.stock import StockListResponse, StockResponse

router = APIRouter(prefix="/company", tags=["companies"])


@router.get("/{symbol}", response_model=StockResponse)
async def get_company_info(
    symbol: str,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get company information by stock symbol.
    Alias for /stocks/{symbol} with focus on company data.
    """
    stock = await stock_crud.get(db, symbol=symbol.upper())

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with symbol {symbol} not found",
        )

    return stock


@router.get("", response_model=StockListResponse)
async def search_companies(
    db: AsyncSession = Depends(get_db_session),
    sector: str = Query(None, description="Filter by sector"),
    industry: str = Query(None, description="Filter by industry"),
    skip: int = 0,
    limit: int = 100,
):
    """
    Search companies with optional filters.
    Can filter by sector, industry, etc.
    """
    # Build filters
    filters = {}
    if sector:
        filters["sector"] = sector
    if industry:
        filters["industry"] = industry

    result = await stock_crud.get_multi(
        db,
        offset=skip,
        limit=limit,
        **filters,
        order_by=["symbol"],
    )

    return StockListResponse(stocks=result["data"], total=result["total_count"])
