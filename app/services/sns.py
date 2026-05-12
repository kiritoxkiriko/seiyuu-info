from app.schemas.voice_actor import SnsPost


VISIBLE_KINDS = {"original", "quote"}
VISIBLE_PLATFORMS = {"x", "youtube", "website"}


def filter_relevant_posts(posts: list[SnsPost]) -> list[SnsPost]:
    return sorted(
        (post for post in posts if post.kind in VISIBLE_KINDS and post.platform in VISIBLE_PLATFORMS),
        key=lambda post: post.posted_at,
        reverse=True,
    )
