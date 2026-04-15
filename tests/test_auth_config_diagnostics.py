from app.core import auth
from streamlit.errors import StreamlitAuthError


def test_sync_user_from_oidc_for_logged_out_user(monkeypatch):
    monkeypatch.setattr(auth.st, "user", type("User", (), {"is_logged_in": False})())
    monkeypatch.setattr(auth.st, "session_state", {})

    auth.sync_user_from_oidc()

    assert auth.st.session_state["authenticated"] is False
    assert auth.st.session_state["user_id"] is None
    assert auth.st.session_state["username"] == ""


def test_sync_user_from_oidc_for_logged_in_user(monkeypatch):
    user = type(
        "User",
        (),
        {
            "is_logged_in": True,
            "to_dict": lambda self: {
                "email": "oidc@example.com",
                "name": "OIDC User",
                "sub": "oidc-sub-123",
            },
        },
    )()
    monkeypatch.setattr(auth.st, "user", user)
    monkeypatch.setattr(auth.st, "session_state", {})

    auth.sync_user_from_oidc()

    assert auth.st.session_state["authenticated"] is True
    assert auth.st.session_state["user_id"] == "oidc-sub-123"
    assert auth.st.session_state["username"] == "OIDC User"


def test_load_user_context_uses_auth0_provider():
    user = type(
        "UserObj",
        (),
        {
            "provider_sub": "abc-123",
            "email": "person@example.com",
            "display_name": "Person",
            "roles": "user,admin",
        },
    )()

    ctx = auth.load_user_context(user)

    assert ctx.user.provider == "auth0"
    assert "admin" in ctx.role_codes


def test_ensure_authenticated_user_stops_when_not_authenticated(monkeypatch):
    monkeypatch.setattr(auth.st, "user", type("User", (), {"is_logged_in": False})())
    monkeypatch.setattr(auth.st, "session_state", {})
    monkeypatch.setattr(auth.st, "title", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "button", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(auth.st, "stop", lambda: (_ for _ in ()).throw(RuntimeError("stopped")))

    try:
        auth.ensure_authenticated_user()
    except RuntimeError as exc:
        assert str(exc) == "stopped"


def test_ensure_authenticated_user_returns_oidc_user(monkeypatch):
    user = type(
        "User",
        (),
        {
            "is_logged_in": True,
            "to_dict": lambda self: {
                "email": "oidc@example.com",
                "name": "OIDC User",
                "sub": "oidc-sub-123",
            },
        },
    )()
    monkeypatch.setattr(auth.st, "user", user)
    monkeypatch.setattr(auth.st, "session_state", {})

    auth_user = auth.ensure_authenticated_user()

    assert auth_user.provider_sub == "oidc-sub-123"
    assert auth_user.display_name == "OIDC User"


def test_login_with_auth0_handles_streamlit_auth_error(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "login",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(StreamlitAuthError("bad auth config")),
    )
    captured_errors: list[str] = []
    monkeypatch.setattr(auth.st, "error", lambda msg: captured_errors.append(msg))

    auth.login_with_auth0()

    assert captured_errors
