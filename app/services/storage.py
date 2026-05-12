from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import hashlib


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
