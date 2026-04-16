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
