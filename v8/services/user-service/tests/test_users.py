"""Test user endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "User Service"


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test login endpoint."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"firebase_token": "mock_firebase_token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test register endpoint."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "firebase_token": "mock_firebase_token",
            "display_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["display_name"] == "New User"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test get current user endpoint."""
    response = await client.get("/api/v1/user")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_update_current_user(client: AsyncClient):
    """Test update current user endpoint."""
    response = await client.put(
        "/api/v1/user",
        json={
            "display_name": "Updated Name",
            "photo_url": "https://example.com/new-photo.jpg",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Updated Name"
    assert data["photo_url"] == "https://example.com/new-photo.jpg"


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient):
    """Test get user by ID endpoint."""
    user_id = "user_123"
    response = await client.get(f"/api/v1/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert "email" in data
    assert "display_name" in data
