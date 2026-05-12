from datetime import datetime, timezone

from workers import WorkerEntrypoint
import asgi

from app.core.config import get_settings
from app.main import app
from app.services.cache_store import build_cache_store
from app.services.scheduler import run_scheduled_syncs


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)

    async def scheduled(self, controller, env, ctx):
        settings = get_settings()
        if not settings.scheduler_enabled:
            return
        store = build_cache_store(settings, env)
        await store.init()
        scheduled_time = getattr(controller, "scheduledTime", None)
        now = datetime.fromtimestamp(scheduled_time / 1000, tz=timezone.utc) if scheduled_time else datetime.now(timezone.utc)
        await run_scheduled_syncs(store, settings, now=now)
