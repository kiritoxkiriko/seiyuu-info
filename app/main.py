import asyncio
import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.cache_store import build_cache_store
from app.services.scheduler import run_scheduler_loop


@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
    settings = get_settings()
    scheduler_task: asyncio.Task | None = None

    if settings.scheduler_enabled:
        store = build_cache_store(settings)
        await store.init()
        scheduler_task = asyncio.create_task(run_scheduler_loop(store, settings), name="nsy-sync-scheduler")

    try:
        yield
    finally:
        if scheduler_task:
            scheduler_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await scheduler_task


def create_app() -> FastAPI:
    settings = get_settings()
    fastapi_app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    fastapi_app.include_router(health_router)
    fastapi_app.include_router(api_router)
    fastapi_app.mount(
        settings.media_public_prefix,
        StaticFiles(directory=settings.media_root, check_dir=False),
        name="media",
    )
    return fastapi_app


app = create_app()
