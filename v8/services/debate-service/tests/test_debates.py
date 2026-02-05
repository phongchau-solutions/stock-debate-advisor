import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_debate(client: AsyncClient):
    """Test creating a debate."""
    response = await client.post(
        "/api/v1/debates",
        json={
            "symbol": "AAPL",
            "timeframe": "1_month"
        },
        headers={"Authorization": "Bearer mock_token"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["timeframe"] == "1_month"
    assert data["status"] == "pending"
    assert "id" in data
