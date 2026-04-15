from app.core import auth


def test_missing_auth_requirements_for_named_provider(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth": {
                "redirect_uri": "https://example.com/oauth2callback",
                "cookie_secret": "cookie",
                "auth0": {
                    "client_id": "id",
                    "client_secret": "secret",
                },
            }
        },
    )
    missing = auth._missing_auth_requirements()
    assert missing == ["[auth.auth0].server_metadata_url"]


def test_missing_auth_requirements_for_inline_provider(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth": {
                "redirect_uri": "https://example.com/oauth2callback",
                "cookie_secret": "cookie",
                "client_id": "id",
            }
        },
    )
    missing = auth._missing_auth_requirements()
    assert missing == ["[auth].client_secret", "[auth].server_metadata_url"]


def test_legacy_auth0_hint_detects_migratable_config(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth0": {
                "domain": "tenant.auth0.com",
                "client_id": "id",
                "client_secret": "secret",
            }
        },
    )

    hint = auth._legacy_auth0_hint()

    assert hint is not None
    assert "[auth]" in hint


def test_legacy_auth0_hint_ignores_incomplete_legacy_config(monkeypatch):
    monkeypatch.setattr(auth.st, "secrets", {"auth0": {"domain": "tenant.auth0.com"}})

    assert auth._legacy_auth0_hint() is None


def test_missing_auth_requirements_accepts_auth_domain_shorthand(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "secrets",
        {
            "auth": (
                '[auth]\\ndomain = "tenant.auth0.com"\\nclient_id = "id"\\n'
                'client_secret = "secret"\\nredirect_uri = "https://example.com/"'
            )
        },
    )

    assert auth._missing_auth_requirements() == []
