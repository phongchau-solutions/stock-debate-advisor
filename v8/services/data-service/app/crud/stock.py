"""Stock CRUD operations."""

from fastcrud import FastCRUD

from app.models.stock import Stock, StockPrice

# Create CRUD instances
stock_crud = FastCRUD(Stock)
stock_price_crud = FastCRUD(StockPrice)
