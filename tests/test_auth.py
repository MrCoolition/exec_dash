from app.services.user_context import UserContext
from app.models.pydantic_models import User


def test_user_context_roles():
    ctx = UserContext(
        user=User(provider="oidc", provider_sub="abc"),
        role_codes={"client_viewer"},
        tenant_slugs=["default"],
    )
    assert "client_viewer" in ctx.role_codes
