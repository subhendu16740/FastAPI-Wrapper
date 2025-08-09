from fastapi import APIRouter, HTTPException
from app.services.coingecko_service import get_price_summary

router = APIRouter(prefix="/price", tags=["price"])

@router.get("/{coin_id}")
async def price_summary(coin_id: str):
    try:
        return await get_price_summary(coin_id)
    except Exception as e:
        # This is a simple generic handler — adapt in prod
        raise HTTPException(status_code=502, detail=str(e))
