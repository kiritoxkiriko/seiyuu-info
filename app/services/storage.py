from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import hashlib

import httpx


@dataclass(frozen=True)
class StoredImagePath:
    public_url: str
    file_path: Path


class LocalImageStorage:
    def __init__(self, root: Path, public_prefix: str = "/media"):
        self.root = root
        self.public_prefix = public_prefix.rstrip("/")

    def path_for(self, owner_id: str, source_url: str) -> StoredImagePath:
        digest = hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:16]
        suffix = Path(urlparse(source_url).path).suffix or ".jpg"
        filename = f"{digest}{suffix}"
        file_path = self.root / owner_id / filename
        public_url = f"{self.public_prefix}/{owner_id}/{filename}"
        return StoredImagePath(public_url=public_url, file_path=file_path)

    async def store_remote_image(self, owner_id: str, source_url: str, client: httpx.AsyncClient | None = None) -> StoredImagePath:
        path = self.path_for(owner_id, source_url)
        if path.file_path.exists():
            return path

        close_client = client is None
        http_client = client or httpx.AsyncClient(
            follow_redirects=True,
            timeout=20,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                ),
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            },
        )
        try:
            response = await http_client.get(source_url)
            response.raise_for_status()
            path.file_path.parent.mkdir(parents=True, exist_ok=True)
            path.file_path.write_bytes(response.content)
            return path
        finally:
            if close_client:
                await http_client.aclose()
