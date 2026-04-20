import pytest

import streamlit_app


class _Nav:
    def __init__(self, called: dict[str, bool]):
        self._called = called

    def run(self) -> None:
        self._called["run"] = True


def test_main_unauthenticated_renders_clean_login(monkeypatch):
    monkeypatch.setattr(
        streamlit_app,
        "validate_canonical_auth_config",
        lambda: type("V", (), {"is_valid": True, "errors": (), "warnings": (), "canonical": {"redirect_uri": ""}})(),
    )
    monkeypatch.setattr(streamlit_app, "safe_is_logged_in", lambda: False)
    called = {"login": False}
    monkeypatch.setattr(streamlit_app, "render_clean_login_screen", lambda _v: called.__setitem__("login", True))
    monkeypatch.setattr(streamlit_app, "sync_user_from_oidc", lambda: None)
    monkeypatch.setattr(streamlit_app.st, "stop", lambda: (_ for _ in ()).throw(RuntimeError("stopped")))

    with pytest.raises(RuntimeError, match="stopped"):
        streamlit_app.main()

    assert called["login"] is True


def test_main_authenticated_runs_navigation(monkeypatch):
    validation = type("V", (), {"is_valid": True, "errors": (), "warnings": (), "canonical": {"redirect_uri": ""}})()
    nav_called = {"run": False}

    monkeypatch.setattr(streamlit_app, "validate_canonical_auth_config", lambda: validation)
    monkeypatch.setattr(streamlit_app, "safe_is_logged_in", lambda: True)
    monkeypatch.setattr(streamlit_app, "sync_user_from_oidc", lambda: None)
    monkeypatch.setattr(streamlit_app, "load_user_from_session", lambda: object())
    monkeypatch.setattr(streamlit_app, "load_user_context", lambda _u: type("Ctx", (), {"user": type("U", (), {"display_name": "User", "email": ""})()})())
    monkeypatch.setattr(streamlit_app, "render_shell", lambda _ctx: None)
    monkeypatch.setattr(streamlit_app, "build_pages", lambda _ctx: ["overview"])
    monkeypatch.setattr(streamlit_app.st, "navigation", lambda *_args, **_kwargs: _Nav(nav_called))

    class _SidebarCtx:
        def __enter__(self):
            return None

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(streamlit_app.st, "sidebar", _SidebarCtx())
    monkeypatch.setattr(streamlit_app.st, "caption", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(streamlit_app.st, "button", lambda *_args, **_kwargs: False)

    streamlit_app.main()

    assert nav_called["run"] is True


def test_logout_clears_app_state(monkeypatch):
    called = {"clear": False, "logout": False, "qp": False}

    monkeypatch.setattr(streamlit_app, "clear_auth_session_state", lambda: called.__setitem__("clear", True))
    monkeypatch.setattr(streamlit_app.st, "logout", lambda: called.__setitem__("logout", True))
    monkeypatch.setattr(streamlit_app.st, "query_params", type("QP", (), {"clear": lambda self: called.__setitem__("qp", True)})())

    streamlit_app._logout()

    assert called["clear"] is True
    assert called["logout"] is True
    assert called["qp"] is True
