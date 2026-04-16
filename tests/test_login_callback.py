import pytest

import streamlit_app


def test_main_unauthenticated_renders_clean_login(monkeypatch):
    monkeypatch.setattr(streamlit_app, "_safe_user_logged_in", lambda: False)
    called = {"login": False}
    monkeypatch.setattr(streamlit_app, "render_clean_login_screen", lambda: called.__setitem__("login", True))
    monkeypatch.setattr(streamlit_app.st, "stop", lambda: (_ for _ in ()).throw(RuntimeError("stopped")))

    with pytest.raises(RuntimeError, match="stopped"):
        streamlit_app.main()

    assert called["login"] is True


def test_auth_diagnostics_detects_missing_fields(monkeypatch):
    monkeypatch.setattr(streamlit_app, "load_auth_config", lambda: {"client_id": "id"})
    monkeypatch.setattr(streamlit_app.st, "query_params", {})

    missing, callback_failed = streamlit_app._auth_diagnostics()

    assert callback_failed is False
    assert "client_secret" in missing
    assert "redirect_uri" in missing


def test_auth_diagnostics_detects_callback_params(monkeypatch):
    monkeypatch.setattr(
        streamlit_app,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "server_metadata_url": "https://tenant.example.com/.well-known/openid-configuration",
            "redirect_uri": "https://example.com/oauth2callback",
            "cookie_secret": "cookie",
        },
    )
    monkeypatch.setattr(streamlit_app.st, "query_params", {"code": "abc123"})

    missing, callback_failed = streamlit_app._auth_diagnostics()

    assert missing == []
    assert callback_failed is True


def test_record_callback_failure_tracks_unique_markers():
    session_state = {}

    attempts = streamlit_app._record_callback_failure(
        session_state,
        {"code": "abc123", "state": "state-1"},
    )
    assert attempts == 1

    attempts = streamlit_app._record_callback_failure(
        session_state,
        {"code": "abc123", "state": "state-1"},
    )
    assert attempts == 1

    attempts = streamlit_app._record_callback_failure(
        session_state,
        {"code": "xyz999", "state": "state-2"},
    )
    assert attempts == 2


def test_record_callback_failure_ignores_non_callback_requests():
    session_state = {}

    attempts = streamlit_app._record_callback_failure(session_state, {})

    assert attempts == 0
