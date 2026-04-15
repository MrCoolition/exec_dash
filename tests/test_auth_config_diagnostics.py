from app.core import auth


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
