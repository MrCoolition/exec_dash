from __future__ import annotations

from app.services.user_context import UserContext


ADMIN_ROLES = {"platform_admin"}
# In our current auth setup, many tenants run in an "all authenticated users can
# edit weekly updates" mode without granular Auth0 role claims in the token.
# Keep explicit editor roles, but also allow the baseline authenticated role.
EDITOR_ROLES = {"platform_admin", "program_owner", "user"}


def require_any_role(ctx: UserContext, roles: set[str]) -> None:
    if not roles.intersection(ctx.role_codes):
        raise PermissionError("Insufficient role privileges")


def can_access_admin(ctx: UserContext) -> bool:
    return bool(ADMIN_ROLES.intersection(ctx.role_codes))


def can_edit_updates(ctx: UserContext) -> bool:
    return bool(EDITOR_ROLES.intersection(ctx.role_codes))
