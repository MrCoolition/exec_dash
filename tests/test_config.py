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


def test_validate_canonical_auth_config_warns_on_cookie_placeholder_and_rejects_provider_placeholders():
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
    assert any("auth.auth0.client_id appears to be a placeholder" in err for err in result.errors)
    assert any("too short" in err for err in result.errors)
    assert any("auth.cookie_secret appears to be a placeholder" in warning for warning in result.warnings)


def test_load_config_prefers_aiven_components_over_database_url(monkeypatch):
    class _StubStreamlit:
        secrets = {
            "database": {
                "url": "postgresql://stale:stale@old-host:5432/old-db",
                "AIVEN_HOST": "fresh-host",
                "AIVEN_USER": "fresh-user",
                "AIVEN_PASSWORD": "fresh-password",
                "AIVEN_DB": "fresh-db",
                "AIVEN_PORT": "25060",
            },
            "azure_devops": {},
        }

    monkeypatch.setattr(config, "st", _StubStreamlit)
    loaded = config.load_config()
    assert loaded.database.url == "postgresql://fresh-user:fresh-password@fresh-host:25060/fresh-db"


def test_load_config_accepts_aiven_namespace(monkeypatch):
    class _StubStreamlit:
        secrets = {
            "database": {
                "url": "postgresql://stale:stale@old-host:5432/old-db",
            },
            "aiven": {
                "host": "cluster-host",
                "user": "cluster-user",
                "password": "secret!pass",
                "db": "cluster-db",
                "port": "15956",
                "ca_pem": "-----BEGIN CERTIFICATE-----\nabc\n-----END CERTIFICATE-----",
            },
            "azure_devops": {},
        }

    monkeypatch.setattr(config, "st", _StubStreamlit)
    loaded = config.load_config()
    assert loaded.database.url == "postgresql://cluster-user:secret%21pass@cluster-host:15956/cluster-db"
    assert loaded.database.ca_pem == "-----BEGIN CERTIFICATE-----\nabc\n-----END CERTIFICATE-----"
