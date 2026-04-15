from app.core import auth
from tests.test_config import _as_mapping_section


def test_extract_identity_from_headers(monkeypatch):
    headers = {
        "x-auth-request-email": "person@example.com",
        "x-auth-request-user": "Person Example",
        "x-user-roles": "admin, client_viewer",
    }
    context = type("Ctx", (), {"headers": headers})()
    monkeypatch.setattr(auth.st, "context", context)

    identity, rows = auth._extract_identity_from_headers()

    assert identity["email"] == "person@example.com"
    assert identity["display_name"] == "Person Example"
    assert identity["roles"] == "admin,client_viewer"
    assert any(row["status"] == "ok" for row in rows)


def test_extract_identity_from_secrets(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {"identity": {"email": "fallback@example.com", "display_name": "Fallback User"}},
    )

    identity, rows = auth._extract_identity_from_secrets()

    assert identity["email"] == "fallback@example.com"
    assert identity["provider_sub"] == "fallback@example.com"
    assert rows[0]["status"] == "ok"


def test_extract_identity_from_secrets_accepts_mapping_sections(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "identity": _as_mapping_section(
                {"email": "mapped@example.com", "display_name": "Mapped User"}
            )
        },
    )

    identity, rows = auth._extract_identity_from_secrets()

    assert identity["email"] == "mapped@example.com"
    assert identity["provider_sub"] == "mapped@example.com"
    assert rows[0]["status"] == "ok"


def test_extract_identity_from_streamlit_user(monkeypatch):
    user = type(
        "OidcUser",
        (),
        {
            "is_logged_in": True,
            "email": "oidc@example.com",
            "name": "OIDC User",
            "sub": "oidc-sub-123",
        },
    )()
    monkeypatch.setattr(auth.st, "user", user)

    identity, rows = auth._extract_identity_from_streamlit_user()

    assert identity["email"] == "oidc@example.com"
    assert identity["display_name"] == "OIDC User"
    assert identity["provider_sub"] == "oidc-sub-123"
    assert rows[0]["status"] == "ok"


def test_load_user_context_uses_okta_auth0_provider():
    user = type(
        "UserObj",
        (),
        {
            "provider_sub": "abc-123",
            "email": "person@example.com",
            "display_name": "Person",
            "roles": "client_viewer,admin",
        },
    )()

    ctx = auth.load_user_context(user)

    assert ctx.user.provider == "okta-auth0"
    assert "admin" in ctx.role_codes


def test_oidc_login_readiness_reports_missing_cookie_secret(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "server_metadata_url": "https://tenant/.well-known/openid-configuration",
            "redirect_uri": "https://example.com/callback",
        },
    )

    ready, reason = auth._oidc_login_readiness()

    assert not ready
    assert "cookie_secret" in reason


def test_oidc_login_readiness_rejects_invalid_metadata_url(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "server_metadata_url": "tenant.example.com",
            "redirect_uri": "https://example.com/oauth2callback",
            "cookie_secret": "cookie",
        },
    )

    ready, reason = auth._oidc_login_readiness()

    assert not ready
    assert "server_metadata_url" in reason


def test_oidc_login_readiness_rejects_invalid_redirect_uri(monkeypatch):
    monkeypatch.setattr(
        auth,
        "load_auth_config",
        lambda: {
            "client_id": "id",
            "client_secret": "secret",
            "server_metadata_url": "https://tenant/.well-known/openid-configuration",
            "redirect_uri": "https://example.com/auth/callback",
            "cookie_secret": "cookie",
        },
    )

    ready, reason = auth._oidc_login_readiness()

    assert not ready
    assert "redirect_uri" in reason


def test_ensure_authenticated_user_does_not_call_login_when_oidc_not_ready(monkeypatch):
    monkeypatch.setattr(auth, "_extract_identity_from_headers", lambda: ({}, []))
    monkeypatch.setattr(auth, "_extract_identity_from_streamlit_user", lambda: ({}, []))
    monkeypatch.setattr(auth, "_extract_identity_from_secrets", lambda: ({}, []))
    monkeypatch.setattr(auth, "_render_auth_troubleshooting", lambda _rows: None)
    monkeypatch.setattr(auth, "_oidc_login_readiness", lambda: (False, "missing config"))

    monkeypatch.setattr(auth.st, "title", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "error", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "write", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "warning", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "button", lambda *_args, **_kwargs: False)

    called = {"login": False}

    def _login():
        called["login"] = True

    monkeypatch.setattr(auth.st, "login", _login)
    monkeypatch.setattr(auth.st, "stop", lambda: (_ for _ in ()).throw(RuntimeError("stopped")))

    try:
        auth.ensure_authenticated_user()
    except RuntimeError as exc:
        assert str(exc) == "stopped"

    assert called["login"] is False


def test_ensure_authenticated_user_handles_streamlit_auth_error(monkeypatch):
    monkeypatch.setattr(auth, "_extract_identity_from_headers", lambda: ({}, []))
    monkeypatch.setattr(auth, "_extract_identity_from_streamlit_user", lambda: ({}, []))
    monkeypatch.setattr(auth, "_extract_identity_from_secrets", lambda: ({}, []))
    monkeypatch.setattr(auth, "_render_auth_troubleshooting", lambda _rows: None)
    monkeypatch.setattr(auth, "_oidc_login_readiness", lambda: (True, ""))

    monkeypatch.setattr(auth.st, "title", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "error", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "write", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "warning", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "caption", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(auth.st, "button", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        auth.st,
        "login",
        lambda: (_ for _ in ()).throw(auth.StreamlitAuthError("missing cookie_secret")),
    )
    monkeypatch.setattr(auth.st, "stop", lambda: (_ for _ in ()).throw(RuntimeError("stopped")))

    try:
        auth.ensure_authenticated_user()
    except RuntimeError as exc:
        assert str(exc) == "stopped"
