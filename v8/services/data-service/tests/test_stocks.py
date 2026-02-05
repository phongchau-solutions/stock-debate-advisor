"""Test stock endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_stock(client: AsyncClient):
    """Test creating a stock."""
    response = await client.post(
        "/api/v1/stocks",
        json={
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "market_cap": 2800000000000.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["name"] == "Apple Inc."


@pytest.mark.asyncio
async def test_get_stock(client: AsyncClient):
    """Test getting a stock by symbol."""
    # First create a stock
    await client.post(
        "/api/v1/stocks",
        json={
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "exchange": "NASDAQ",
        },
    )

    # Then get it
    response = await client.get("/api/v1/stocks/MSFT")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "MSFT"
    assert data["name"] == "Microsoft Corporation"


@pytest.mark.asyncio
async def test_list_stocks(client: AsyncClient):
    """Test listing stocks."""
    # Create some stocks
    await client.post(
        "/api/v1/stocks",
        json={"symbol": "GOOGL", "name": "Alphabet Inc."},
    )
    await client.post(
        "/api/v1/stocks",
        json={"symbol": "AMZN", "name": "Amazon.com Inc."},
    )

    # List them
    response = await client.get("/api/v1/stocks")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2
    assert len(data["stocks"]) >= 2


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
