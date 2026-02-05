from fastapi import APIRouter

from app.api.v1 import companies, prices, stocks

api_router = APIRouter()

api_router.include_router(stocks.router)
api_router.include_router(prices.router)
api_router.include_router(companies.router)
