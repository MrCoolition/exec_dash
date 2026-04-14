from app.core.permissions import can_access_admin, can_edit_updates
from app.models.pydantic_models import User
from app.services.user_context import UserContext


def _ctx(*roles: str) -> UserContext:
    return UserContext(user=User(provider="oidc", provider_sub="x"), role_codes=set(roles), tenant_slugs=["t1"])


def test_admin_permissions():
    assert can_access_admin(_ctx("platform_admin"))
    assert not can_access_admin(_ctx("client_viewer"))


def test_update_permissions():
    assert can_edit_updates(_ctx("program_owner"))
    assert not can_edit_updates(_ctx("client_viewer"))
