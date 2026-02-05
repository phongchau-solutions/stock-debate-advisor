"""Stock CRUD operations."""

from fastcrud import FastCRUD

from app.models.stock import Stock, StockPrice
from app.schemas.stock import StockCreate, StockPriceCreate

# Create CRUD instances
stock_crud = FastCRUD(Stock)
stock_price_crud = FastCRUD(StockPrice)
