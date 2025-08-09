from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import Optional

class Settings(BaseSettings):
    API_TITLE: str = "Crypto API Framework"
    API_VERSION: str = "1.0.0"

    COINGECKO_BASE: AnyHttpUrl = "https://api.coingecko.com/api/v3"
    REDIS_URL: Optional[str] = None  # e.g. redis://redis:6379
    CACHE_TTL_SECONDS: int = 300

    # HTTP client settings
    HTTP_TIMEOUT_SECONDS: int = 15
    HTTP_RETRIES: int = 2
    HTTP_RETRY_BACKOFF: float = 0.5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
