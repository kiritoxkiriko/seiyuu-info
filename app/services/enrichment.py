from app.schemas.voice_actor import Event, SnsPost
from app.services.translation import Translator


async def translate_events(events: list[Event]) -> list[Event]:
    translator = Translator()
    translated: list[Event] = []
    for event in events:
        translated.append(
            event.model_copy(
                update={
                    "title_zh": event.title_zh or await translator.to_zh(event.title),
                    "venue_zh": event.venue_zh or await translator.to_zh(event.venue),
                }
            )
        )
    return translated


async def translate_posts(posts: list[SnsPost]) -> list[SnsPost]:
    translator = Translator()
    translated: list[SnsPost] = []
    for post in posts:
        detail_text = post.detail_text or post.text
        translated.append(
            post.model_copy(
                update={
                    "text_zh": post.text_zh or await translator.to_zh(post.text),
                    "detail_text": detail_text,
                    "detail_text_zh": post.detail_text_zh or await translator.to_zh(detail_text),
                }
            )
        )
    return translated
