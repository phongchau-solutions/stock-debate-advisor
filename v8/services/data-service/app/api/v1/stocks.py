"""Stock endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_optional_user
from app.crud.stock import stock_crud
from app.schemas.stock import StockCreate, StockListResponse, StockResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    stock_data: StockCreate,
    db: AsyncSession = Depends(get_db_session),
    user_id: str = Depends(get_optional_user),
):
    """Create a new stock entry."""
    # Check if stock already exists
    existing = await stock_crud.get(db, symbol=stock_data.symbol)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Stock with symbol {stock_data.symbol} already exists",
        )

    stock_dict = stock_data.model_dump()
    stock = await stock_crud.create(db, stock_dict)

    return stock


@router.get("/{symbol}", response_model=StockResponse)
async def get_stock(
    symbol: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get stock by symbol."""
    stock = await stock_crud.get(db, symbol=symbol.upper())

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with symbol {symbol} not found",
        )

    return stock


@router.get("", response_model=StockListResponse)
async def list_stocks(
    db: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100,
):
    """List all stocks."""
    result = await stock_crud.get_multi(
        db,
        offset=skip,
        limit=limit,
        order_by=["symbol"],
    )

    return StockListResponse(stocks=result["data"], total=result["total_count"])


@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock(
    symbol: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a stock."""
    stock = await stock_crud.get(db, symbol=symbol.upper())

    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with symbol {symbol} not found",
        )

    await stock_crud.delete(db, symbol=symbol.upper())
