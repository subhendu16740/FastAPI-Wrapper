import json
from typing import Any, Dict, List
from app.config import settings
from app.utils.http_client import get as http_get
from app.utils.cache import cache_get, cache_set
from app import __name__ as package_name
from datetime import datetime
import logging

logger = logging.getLogger(package_name)

async def _fetch_coin_full(coin_id: str) -> Dict[str, Any]:
    url = f"{settings.COINGECKO_BASE}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false",
    }
    resp = await http_get(url, params=params)
    return resp.json()

async def get_price_summary(coin_id: str) -> Dict[str, Any]:
    """
    Returns a compact summary for /price/{coin_id}
    """
    cache_key = f"coin:summary:{coin_id}"
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    raw = await _fetch_coin_full(coin_id)
    market = raw.get("market_data", {})
    current_price = market.get("current_price", {}).get("usd")
    market_cap = market.get("market_cap", {}).get("usd")
    total_volume = market.get("total_volume", {}).get("usd")
    change_24h = market.get("price_change_percentage_24h")
    homepage = None
    links = raw.get("links", {})
    if links:
        hp = links.get("homepage") or []
        if isinstance(hp, list) and len(hp) > 0 and hp[0]:
            homepage = hp[0]

    last_updated_raw = raw.get("last_updated")
    last_updated = None
    if last_updated_raw:
        try:
            last_updated = datetime.fromisoformat(last_updated_raw.replace("Z", "+00:00")).isoformat()
        except Exception:
            last_updated = last_updated_raw

    out = {
        "id": raw.get("id"),
        "symbol": raw.get("symbol"),
        "name": raw.get("name"),
        "homepage": homepage,
        "current_price_usd": current_price,
        "market_cap_usd": market_cap,
        "total_volume_usd": total_volume,
        "price_change_percentage_24h": change_24h,
        "last_updated": last_updated,
    }

    await cache_set(cache_key, json.dumps(out), ex=settings.CACHE_TTL_SECONDS)
    logger.info(f"Cached summary for {coin_id}")
    return out

async def get_market_chart(coin_id: str, days: int = 7) -> Dict[str, Any]:
    """
    Returns simplified market chart: list of {timestamp, price} for last `days`.
    Uses /coins/{id}/market_chart
    """
    cache_key = f"coin:chart:{coin_id}:{days}"
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    url = f"{settings.COINGECKO_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    resp = await http_get(url, params=params)
    data = resp.json()
    prices = data.get("prices", [])
    # prices are [ [timestamp_ms, price], ... ]
    simplified = [{"timestamp_ms": int(ts), "price": float(p)} for ts, p in prices]
    out = {"id": coin_id, "days": days, "prices": simplified}
    await cache_set(cache_key, json.dumps(out), ex=settings.CACHE_TTL_SECONDS)
    return out

async def get_trending() -> Dict[str, Any]:
    """
    Returns simplified trending coins from /search/trending
    """
    cache_key = "coins:trending"
    cached = await cache_get(cache_key)
    if cached:
        return json.loads(cached)

    url = f"{settings.COINGECKO_BASE}/search/trending"
    resp = await http_get(url)
    data = resp.json()
    coins = data.get("coins", [])
    simplified = []
    for entry in coins:
        item = entry.get("item", {})
        simplified.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "symbol": item.get("symbol"),
            "market_cap_rank": item.get("market_cap_rank"),
            "score": entry.get("score")  # trending score
        })
    out = {"trending": simplified}
    await cache_set(cache_key, json.dumps(out), ex=settings.CACHE_TTL_SECONDS)
    return out
