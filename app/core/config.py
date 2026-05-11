import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "nsy 情报站 API"
    allowed_origins: list[str]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:4321")
    return Settings(allowed_origins=[origin.strip() for origin in origins.split(",") if origin.strip()])
