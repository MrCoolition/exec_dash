from types import SimpleNamespace

from app.core import error_reporting
from app.core.config import AdoConfig, AppConfig, DatabaseConfig


def test_classify_root_cause_detects_auth_issue():
    exc = RuntimeError("OIDC login failed due to invalid token")
    assert error_reporting._classify_root_cause(exc) == "Authentication or OIDC provider configuration mismatch"


def test_build_runtime_snapshot_includes_expected_flags(monkeypatch):
    monkeypatch.setattr(
        error_reporting,
        "load_auth_config",
        lambda: {
            "redirect_uri": "https://exec-dash.streamlit.app/oauth2callback",
            "server_metadata_url": "https://example.auth0.com/.well-known/openid-configuration",
            "client_id": "abcd1234efgh",
            "cookie_secret": "cookie-secret",
        },
    )
    monkeypatch.setattr(
        error_reporting,
        "load_config",
        lambda: AppConfig(
            database=DatabaseConfig(url="postgresql+psycopg://user:pass@example:5432/db", sslmode="require", ca_pem="pem"),
            ado=AdoConfig(organization="org", pat="pat"),
        ),
    )
    monkeypatch.setattr(
        error_reporting,
        "st",
        SimpleNamespace(secrets={"auth": {"auth0": {"client_id": "id"}}}),
    )

    snapshot = error_reporting._build_runtime_snapshot()

    assert snapshot["db_scheme"] == "postgresql+psycopg"
    assert snapshot["db_ca_present"] == "yes"
    assert snapshot["has_[auth]"] == "yes"
    assert snapshot["has_[auth.auth0]"] == "yes"
    assert snapshot["auth_cookie_secret_present"] == "yes"
