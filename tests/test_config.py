from app.core import config


def test_validate_canonical_auth_config_accepts_canonical_shape():
    result = config.validate_canonical_auth_config(
        {
            "auth": {
                "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
                "cookie_secret": "cookie-secret",
                "auth0": {
                    "client_id": "client-id",
                    "client_secret": "client-secret",
                    "server_metadata_url": "https://tenant.us.auth0.com/.well-known/openid-configuration",
                },
            }
        }
    )

    assert result.is_valid is True
    assert result.errors == ()


def test_validate_canonical_auth_config_rejects_legacy_auth0_only():
    result = config.validate_canonical_auth_config(
        {
            "auth0": {
                "client_id": "client-id",
                "client_secret": "client-secret",
                "domain": "tenant.us.auth0.com",
            }
        }
    )

    assert result.is_valid is False
    assert any("auth.redirect_uri" in err for err in result.errors)
    assert any("Legacy [auth0] block" in warning for warning in result.warnings)


def test_validate_canonical_auth_config_rejects_non_root_callback_path():
    result = config.validate_canonical_auth_config(
        {
            "auth": {
                "redirect_uri": "https://exec-dash.streamlit.app/~+/oauth2callback",
                "cookie_secret": "cookie-secret",
                "auth0": {
                    "client_id": "client-id",
                    "client_secret": "client-secret",
                    "server_metadata_url": "https://tenant.us.auth0.com/.well-known/openid-configuration",
                },
            }
        }
    )

    assert result.is_valid is False
    assert any("multipage route" in err for err in result.errors)


def test_validate_canonical_auth_config_rejects_placeholder_and_short_secret_values():
    result = config.validate_canonical_auth_config(
        {
            "auth": {
                "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
                "cookie_secret": "<LONG_RANDOM_SECRET>",
                "auth0": {
                    "client_id": "YOUR_CLIENT_ID",
                    "client_secret": "short",
                    "server_metadata_url": "https://tenant.us.auth0.com/.well-known/openid-configuration",
                },
            }
        }
    )

    assert result.is_valid is False
    assert any("placeholder" in err for err in result.errors)
    assert any("too short" in err for err in result.errors)
