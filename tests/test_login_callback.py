import pytest

import streamlit_app


def test_oauth_callback_error_detail_for_auth_code(monkeypatch):
    monkeypatch.setattr(streamlit_app.st, "query_params", {"code": "abc", "state": "xyz"})

    detail = streamlit_app._oauth_callback_error_detail()

    assert "Received OAuth callback parameters" in detail


def test_main_renders_auth_troubleshooting_after_oauth_callback(monkeypatch):
    monkeypatch.setattr(streamlit_app, "_safe_user_logged_in", lambda: False)
    monkeypatch.setattr(streamlit_app, "_render_login_screen", lambda: None)
    monkeypatch.setattr(streamlit_app.st, "query_params", {"code": "abc", "state": "xyz"})

    captured_errors: list[str] = []
    captured_troubleshooting: list[str] = []
    monkeypatch.setattr(streamlit_app.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(
        streamlit_app,
        "render_auth_troubleshooting_panel",
        lambda msg=None: captured_troubleshooting.append(msg or ""),
    )
    monkeypatch.setattr(streamlit_app.st, "stop", lambda: (_ for _ in ()).throw(RuntimeError("stopped")))

    with pytest.raises(RuntimeError, match="stopped"):
        streamlit_app.main()

    assert captured_errors
    assert captured_troubleshooting
    assert "Received OAuth callback parameters" in captured_troubleshooting[0]


def test_oauth_callback_error_detail_prefers_provider_error(monkeypatch):
    monkeypatch.setattr(
        streamlit_app.st,
        "query_params",
        {"error": "access_denied", "error_description": "User denied access"},
    )

    detail = streamlit_app._oauth_callback_error_detail()

    assert detail == "access_denied: User denied access"
