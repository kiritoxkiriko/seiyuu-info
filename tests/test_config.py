from app.core.config import get_settings


def test_settings_support_separate_fetch_and_display_windows(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("EVENT_FETCH_PAST_DAYS", "240")
    monkeypatch.setenv("EVENT_FETCH_FUTURE_DAYS", "120")
    monkeypatch.setenv("SNS_FETCH_PAST_DAYS", "90")
    monkeypatch.setenv("EVENT_DISPLAY_PAST_DAYS", "30")
    monkeypatch.setenv("EVENT_DISPLAY_FUTURE_DAYS", "60")
    monkeypatch.setenv("SNS_DISPLAY_PAST_DAYS", "14")

    settings = get_settings()

    assert settings.event_fetch_past_days == 240
    assert settings.event_fetch_future_days == 120
    assert settings.sns_fetch_past_days == 90
    assert settings.event_display_past_days == 30
    assert settings.event_display_future_days == 60
    assert settings.sns_display_past_days == 14

    get_settings.cache_clear()


def test_settings_keep_backward_compatible_time_window_names(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.delenv("EVENT_FETCH_PAST_DAYS", raising=False)
    monkeypatch.delenv("EVENT_FETCH_FUTURE_DAYS", raising=False)
    monkeypatch.delenv("SNS_FETCH_PAST_DAYS", raising=False)
    monkeypatch.delenv("EVENT_DISPLAY_PAST_DAYS", raising=False)
    monkeypatch.delenv("EVENT_DISPLAY_FUTURE_DAYS", raising=False)
    monkeypatch.delenv("SNS_DISPLAY_PAST_DAYS", raising=False)
    monkeypatch.setenv("EVENT_PAST_DAYS", "45")
    monkeypatch.setenv("EVENT_FUTURE_DAYS", "75")
    monkeypatch.setenv("SNS_PAST_DAYS", "15")

    settings = get_settings()

    assert settings.event_fetch_past_days == 45
    assert settings.event_display_past_days == 45
    assert settings.event_fetch_future_days == 75
    assert settings.event_display_future_days == 75
    assert settings.sns_fetch_past_days == 15
    assert settings.sns_display_past_days == 15

    get_settings.cache_clear()
