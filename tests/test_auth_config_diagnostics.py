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
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
            "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
            "cookie_secret": "super-secret-value",
        },
    )
    monkeypatch.setattr(
        auth.st,
        "login",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(StreamlitAuthError("bad auth config")),
    )
    captured_errors: list[str] = []
    diagnostics_errors: list[str] = []
    monkeypatch.setattr(auth.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(auth, "render_auth_troubleshooting_panel", lambda msg=None: diagnostics_errors.append(msg or ""))

    auth.login_with_auth0()

    assert captured_errors
    assert diagnostics_errors == ["bad auth config"]


def test_login_with_auth0_blocks_invalid_config_before_redirect(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {"client_id": "abc", "client_secret": "def"},
    )
    login_called = {"value": False}
    monkeypatch.setattr(
        auth.st,
        "login",
        lambda *_args, **_kwargs: login_called.__setitem__("value", True),
    )
    captured_errors: list[str] = []
    diagnostics_errors: list[str] = []
    monkeypatch.setattr(auth.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(auth, "render_auth_troubleshooting_panel", lambda msg=None: diagnostics_errors.append(msg or ""))

    auth.login_with_auth0()

    assert captured_errors
    assert "Missing required keys:" in captured_errors[0]
    assert diagnostics_errors
    assert login_called["value"] is False


def test_login_with_auth0_blocks_legacy_only_secrets_shape(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
            "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
            "cookie_secret": "cookie-secret",
        },
    )
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth0": {
                "client_id": "id",
                "client_secret": "secret",
                "domain": "example.auth0.com",
                "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
            }
        },
    )
    login_called = {"value": False}
    monkeypatch.setattr(
        auth.st,
        "login",
        lambda *_args, **_kwargs: login_called.__setitem__("value", True),
    )
    captured_errors: list[str] = []
    monkeypatch.setattr(auth.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(auth, "render_auth_troubleshooting_panel", lambda *_args, **_kwargs: None)

    auth.login_with_auth0()

    assert captured_errors
    assert "[auth] section" in captured_errors[0]
    assert login_called["value"] is False


def test_login_with_auth0_allows_canonical_streamlit_secrets_shape(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
            "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
            "cookie_secret": "cookie-secret",
        },
    )
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth": {
                "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
                "cookie_secret": "cookie-secret",
                "auth0": {
                    "client_id": "id",
                    "client_secret": "secret",
                    "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
                },
            }
        },
    )
    login_called = {"value": False}
    monkeypatch.setattr(
        auth.st,
        "login",
        lambda *_args, **_kwargs: login_called.__setitem__("value", True),
    )
    monkeypatch.setattr(auth.st, "error", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth, "render_auth_troubleshooting_panel", lambda *_args, **_kwargs: None)

    auth.login_with_auth0()

    assert login_called["value"] is True


def test_login_with_auth0_blocks_whitespace_secrets_before_redirect(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
            "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
            "cookie_secret": "cookie-secret",
        },
    )
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth": {
                "redirect_uri": " https://exec-dash.streamlit.app/oauth2callback ",
                "cookie_secret": "cookie-secret",
                "auth0": {
                    "client_id": "id",
                    "client_secret": " secret ",
                    "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
                },
            }
        },
    )
    login_called = {"value": False}
    monkeypatch.setattr(auth.st, "login", lambda *_args, **_kwargs: login_called.__setitem__("value", True))
    captured_errors: list[str] = []
    monkeypatch.setattr(auth.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(auth, "render_auth_troubleshooting_panel", lambda *_args, **_kwargs: None)

    auth.login_with_auth0()

    assert captured_errors
    assert "contains leading/trailing whitespace" in captured_errors[0]
    assert login_called["value"] is False


def test_login_with_auth0_blocks_placeholder_values_before_redirect(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
            "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
            "cookie_secret": "cookie-secret",
        },
    )
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth": {
                "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
                "cookie_secret": "cookie-secret",
                "auth0": {
                    "client_id": "<YOUR_CLIENT_ID>",
                    "client_secret": "<YOUR_CLIENT_SECRET>",
                    "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
                },
            }
        },
    )
    login_called = {"value": False}
    monkeypatch.setattr(auth.st, "login", lambda *_args, **_kwargs: login_called.__setitem__("value", True))
    captured_errors: list[str] = []
    monkeypatch.setattr(auth.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(auth, "render_auth_troubleshooting_panel", lambda *_args, **_kwargs: None)

    auth.login_with_auth0()

    assert captured_errors
    assert "appears to be a placeholder value" in captured_errors[0]
    assert login_called["value"] is False
