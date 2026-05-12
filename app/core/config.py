import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "nsy 情报站 API"
    allowed_origins: list[str]
    data_cache_enabled: bool = False
    database_url: str = "sqlite:///data/nsy.sqlite3"
    d1_binding: str = "DB"
    event_fetch_past_days: int = 183
    event_fetch_future_days: int = 183
    sns_fetch_past_days: int = 183
    event_display_past_days: int = 183
    event_display_future_days: int = 183
    sns_display_past_days: int = 183
    scheduler_enabled: bool = False
    sns_sync_interval_minutes: int = 10
    event_sync_interval_minutes: int = 60
    media_root: str = "data/media"
    media_public_prefix: str = "/media"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:4321")
    return Settings(
        allowed_origins=[origin.strip() for origin in origins.split(",") if origin.strip()],
        data_cache_enabled=_bool_env("DATA_CACHE_ENABLED", default=False),
        database_url=os.getenv("DATABASE_URL", "sqlite:///data/nsy.sqlite3"),
        d1_binding=os.getenv("D1_BINDING", "DB"),
        event_fetch_past_days=_int_env_fallback(["EVENT_FETCH_PAST_DAYS", "EVENT_PAST_DAYS"], default=183),
        event_fetch_future_days=_int_env_fallback(["EVENT_FETCH_FUTURE_DAYS", "EVENT_FUTURE_DAYS"], default=183),
        sns_fetch_past_days=_int_env_fallback(["SNS_FETCH_PAST_DAYS", "SNS_PAST_DAYS"], default=183),
        event_display_past_days=_int_env_fallback(["EVENT_DISPLAY_PAST_DAYS", "EVENT_PAST_DAYS"], default=183),
        event_display_future_days=_int_env_fallback(["EVENT_DISPLAY_FUTURE_DAYS", "EVENT_FUTURE_DAYS"], default=183),
        sns_display_past_days=_int_env_fallback(["SNS_DISPLAY_PAST_DAYS", "SNS_PAST_DAYS"], default=183),
        scheduler_enabled=_bool_env("SCHEDULER_ENABLED", default=False),
        sns_sync_interval_minutes=_int_env("SNS_SYNC_INTERVAL_MINUTES", default=10),
        event_sync_interval_minutes=_int_env("EVENT_SYNC_INTERVAL_MINUTES", default=60),
        media_root=os.getenv("MEDIA_ROOT", "data/media"),
        media_public_prefix=os.getenv("MEDIA_PUBLIC_PREFIX", "/media"),
    )


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _int_env_fallback(names: list[str], default: int) -> int:
    for name in names:
        value = os.getenv(name)
        if value is None:
            continue
        try:
            return int(value)
        except ValueError:
            continue
    return default
