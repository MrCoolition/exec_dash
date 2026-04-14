from app.core import config


def test_resolve_provider_named_auth0():
    auth = {
        "redirect_uri": "https://example.com/oauth2callback",
        "cookie_secret": "x",
        "auth0": {
            "client_id": "id",
            "client_secret": "secret",
            "server_metadata_url": "https://x/.well-known/openid-configuration",
        },
    }

    assert config._resolve_auth_provider(auth) == "auth0"


def test_resolve_provider_single_inline_auth():
    auth = {
        "redirect_uri": "https://example.com/oauth2callback",
        "cookie_secret": "x",
        "client_id": "id",
        "client_secret": "secret",
        "server_metadata_url": "https://x/.well-known/openid-configuration",
    }

    assert config._resolve_auth_provider(auth) is None


def test_resolve_provider_legacy_auth0_requires_client_credentials(monkeypatch):
    monkeypatch.setattr(config.st, "secrets", {"auth0": {"domain": "x"}})
    assert config._resolve_auth_provider({}) is None


def test_resolve_provider_legacy_auth0_with_client_credentials(monkeypatch):
    monkeypatch.setattr(
        config.st,
        "secrets",
        {"auth0": {"domain": "x", "client_id": "id", "client_secret": "secret"}},
    )
    assert config._resolve_auth_provider({}) is None
