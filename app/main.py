from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import logging

from app.config import settings
from app.routers import price, chart, trending

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crypto_api")

app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION, description="Wrapper around CoinGecko that returns filtered crypto payloads.")

# CORS for development convenience
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Include routers
app.include_router(price.router)
app.include_router(chart.router)
app.include_router(trending.router)

@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

@app.get("/docs-json", include_in_schema=False)
async def openapi_json():
    """
    Return OpenAPI JSON. (Custom path as requested)
    The interactive Swagger UI is still available at /docs by FastAPI default.
    """
    return JSONResponse(get_openapi(title=app.title, version=app.version, description=app.description, routes=app.routes))

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Crypto API Framework running", "docs": "/docs", "openapi": "/docs-json"}

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Crypto API Framework")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping Crypto API Framework")
