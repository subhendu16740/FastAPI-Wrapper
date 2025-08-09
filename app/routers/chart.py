from fastapi import APIRouter, Query, HTTPException
from app.services.coingecko_service import get_market_chart

router = APIRouter(prefix="/chart", tags=["chart"])

@router.get("/{coin_id}")
async def market_chart(coin_id: str, days: int = Query(7, ge=1, le=90)):
    """
    Returns simplified market chart (timestamp_ms, price) for given days (1-90)
    """
    try:
        return await get_market_chart(coin_id, days=days)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
