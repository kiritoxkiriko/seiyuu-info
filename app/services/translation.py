import os
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class TranslationConfig:
    provider: str
    deepl_api_key: str | None
    deepl_api_url: str


class Translator:
    def __init__(self, config: TranslationConfig | None = None):
        self.config = config or TranslationConfig(
            provider=os.getenv("TRANSLATION_PROVIDER", "none"),
            deepl_api_key=os.getenv("DEEPL_API_KEY"),
            deepl_api_url=os.getenv("DEEPL_API_URL", "https://api-free.deepl.com/v2/translate"),
        )

    async def to_zh(self, text: str | None) -> str | None:
        if not text:
            return text
        if self.config.provider == "mock":
            return f"中文：{text}"
        if self.config.provider == "deepl" and self.config.deepl_api_key:
            try:
                return await self._deepl(text)
            except httpx.HTTPError:
                return text
        return text

    async def _deepl(self, text: str) -> str:
        headers = {"Authorization": f"DeepL-Auth-Key {self.config.deepl_api_key}"}
        async with httpx.AsyncClient(timeout=12.0, headers=headers) as client:
            response = await client.post(
                self.config.deepl_api_url,
                data={
                    "text": text,
                    "target_lang": "ZH-HANS",
                },
            )
            response.raise_for_status()
        translations = response.json().get("translations", [])
        if not translations:
            return text
        return translations[0].get("text", text)
