CREATE TABLE IF NOT EXISTS actors (
    id TEXT PRIMARY KEY,
    payload_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    title TEXT NOT NULL,
    title_zh TEXT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    venue TEXT,
    venue_zh TEXT,
    url TEXT,
    source TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_events_actor_date ON events(actor_id, date DESC);

CREATE TABLE IF NOT EXISTS sns_posts (
    id TEXT PRIMARY KEY,
    actor_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    posted_at TEXT NOT NULL,
    text TEXT NOT NULL,
    text_zh TEXT,
    detail_text TEXT,
    detail_text_zh TEXT,
    url TEXT NOT NULL,
    kind TEXT NOT NULL,
    media_urls_json TEXT NOT NULL,
    source TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sns_actor_posted_at ON sns_posts(actor_id, posted_at DESC);

CREATE TABLE IF NOT EXISTS job_runs (
    job_name TEXT PRIMARY KEY,
    ran_at TEXT NOT NULL,
    meta_json TEXT NOT NULL
);
