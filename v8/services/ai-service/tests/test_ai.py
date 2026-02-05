"""Test AI endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_stock(client: AsyncClient):
    """Test stock analysis endpoint."""
    response = await client.post(
        "/api/v1/analyze",
        json={
            "stock_symbol": "AAPL",
            "provider": "gemini",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stock_symbol"] == "AAPL"
    assert "debate_id" in data
    assert data["status"] in ["pending", "running", "completed"]


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient):
    """Test listing agents."""
    response = await client.get("/api/v1/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert data["total"] > 0
    assert len(data["agents"]) > 0


@pytest.mark.asyncio
async def test_judge_debate(client: AsyncClient):
    """Test judge endpoint."""
    response = await client.post(
        "/api/v1/judge",
        json={
            "debate_id": "debate_test123",
            "bull_argument": "AAPL is a great company with strong fundamentals.",
            "bear_argument": "AAPL is overvalued and faces regulatory risks.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["debate_id"] == "debate_test123"
    assert "verdict" in data
    assert "reasoning" in data
    assert "winner" in data
    assert "confidence" in data


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
