from fastapi import APIRouter, HTTPException
from app.services.coingecko_service import get_trending

router = APIRouter(prefix="/trending", tags=["trending"])

@router.get("/")
async def trending_coins():
    try:
        return await get_trending()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
