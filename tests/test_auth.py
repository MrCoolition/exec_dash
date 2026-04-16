from app.services.user_context import UserContext
from app.models.pydantic_models import User
from app.core import auth


def test_user_context_roles():
    ctx = UserContext(
        user=User(provider="oidc", provider_sub="abc"),
        role_codes={"client_viewer"},
        tenant_slugs=["default"],
    )
    assert "client_viewer" in ctx.role_codes


def test_sync_user_from_oidc_for_logged_out_user(monkeypatch):
    monkeypatch.setattr(auth.st, "user", type("User", (), {"is_logged_in": False})())
    monkeypatch.setattr(auth.st, "session_state", {})

    auth.sync_user_from_oidc()

    assert auth.st.session_state["authenticated"] is False
    assert auth.st.session_state["user_id"] is None
    assert auth.st.session_state["username"] == ""


def test_sync_user_from_oidc_extracts_namespaced_roles(monkeypatch):
    user = type(
        "User",
        (),
        {
            "is_logged_in": True,
            "to_dict": lambda self: {
                "email": "oidc@example.com",
                "name": "OIDC User",
                "sub": "oidc-sub-123",
                "https://example.com/roles": ["admin", "editor"],
            },
        },
    )()
    monkeypatch.setattr(auth.st, "user", user)
    monkeypatch.setattr(auth.st, "session_state", {})

    auth.sync_user_from_oidc()

    assert auth.st.session_state["user_roles"] == ["admin", "editor"]
