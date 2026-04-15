from app.core import config


def test_load_auth_config_parses_escaped_toml_string(monkeypatch):
    monkeypatch.setattr(
        config.st,
        "secrets",
        {
            "auth": (
                '[auth]\\ndomain = "tenant.auth0.com"\\nclient_id = "id"\\n'
                'client_secret = "secret"\\nredirect_uri = "https://example.com/"'
            )
        },
    )

    auth = config.load_auth_config()

    assert auth["domain"] == "tenant.auth0.com"
    assert auth["server_metadata_url"] == "https://tenant.auth0.com/.well-known/openid-configuration"
    assert auth["cookie_secret"] == "secret"


def test_load_auth_config_maps_legacy_auth0_block(monkeypatch):
    monkeypatch.setattr(
        config.st,
        "secrets",
        {
            "auth0": {
                "domain": "tenant.auth0.com",
                "client_id": "id",
                "client_secret": "secret",
                "redirect_uri": "https://example.com/oauth2callback",
            }
        },
    )

    auth = config.load_auth_config()

    assert auth["redirect_uri"] == "https://example.com/oauth2callback"
    assert auth["client_id"] == "id"
    assert auth["client_secret"] == "secret"
    assert auth["server_metadata_url"] == "https://tenant.auth0.com/.well-known/openid-configuration"


def test_load_auth_config_prefers_database_cookie_secret(monkeypatch):
    monkeypatch.setattr(
        config.st,
        "secrets",
        {
            "auth0": {
                "domain": "tenant.auth0.com",
                "client_id": "id",
                "client_secret": "auth-client-secret",
                "redirect_uri": "https://example.com/oauth2callback",
            },
            "database": {"NOOKIE_PASS": "cookie-from-db"},
        },
    )

    auth = config.load_auth_config()

    assert auth["cookie_secret"] == "cookie-from-db"
