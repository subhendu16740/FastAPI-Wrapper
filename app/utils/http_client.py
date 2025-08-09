import asyncio
import httpx
from typing import Optional, Dict, Any
from app.config import settings

_client: Optional[httpx.AsyncClient] = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS)
    return _client

async def get(url: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
    """
    Simple retry wrapper around httpx AsyncClient.get
    """
    client = get_client()
    last_exc = None
    for attempt in range(settings.HTTP_RETRIES + 1):
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp
        except Exception as exc:
            last_exc = exc
            # backoff
            await asyncio.sleep(settings.HTTP_RETRY_BACKOFF * (2 ** attempt))
    # if we reach here, all retries failed
    raise last_exc
