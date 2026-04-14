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
