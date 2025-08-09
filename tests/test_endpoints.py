import pytest
from httpx import AsyncClient
from app.main import app
from unittest import mock
import asyncio

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/")
        assert r.status_code == 200
        assert "docs" in r.json()

# Use monkeypatch to stub coingecko service to avoid network calls
@pytest.mark.asyncio
async def test_price_summary(monkeypatch):
    async def fake_get_price_summary(coin_id):
        return {
            "id": coin_id,
            "symbol": "btc",
            "name": "Bitcoin",
            "current_price_usd": 42000,
            "market_cap_usd": 800000000000,
            "last_updated": "2025-08-09T00:00:00Z"
        }
    monkeypatch.setattr("app.services.coingecko_service.get_price_summary", fake_get_price_summary)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/price/bitcoin")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == "bitcoin"
        assert data["current_price_usd"] == 42000

@pytest.mark.asyncio
async def test_trending(monkeypatch):
    async def fake_trending():
        return {"trending": [{"id": "bitcoin", "name": "Bitcoin"}]}
    monkeypatch.setattr("app.services.coingecko_service.get_trending", fake_trending)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/trending/")
        assert r.status_code == 200
        assert "trending" in r.json()
