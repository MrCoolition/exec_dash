from app.models.pydantic_models import User
from app.services.user_context import UserContext
from app.ui import pages


class FakePage:
    def __init__(self, render_fn, **kwargs):
        self.render_fn = render_fn
        self.kwargs = kwargs


def _ctx(*roles: str) -> UserContext:
    return UserContext(user=User(provider="oidc", provider_sub="x"), role_codes=set(roles), tenant_slugs=["t1"])


def test_weekly_updates_hidden_for_non_editors(monkeypatch):
    monkeypatch.setattr(pages.st, "Page", FakePage)
    built = pages.build_pages(_ctx("client_viewer"))
    weekly = next(page for page in built if page.kwargs.get("title") == "Weekly Updates")
    assert weekly.kwargs.get("visibility") == "hidden"


def test_weekly_updates_visible_for_editors(monkeypatch):
    monkeypatch.setattr(pages.st, "Page", FakePage)
    built = pages.build_pages(_ctx("program_owner"))
    weekly = next(page for page in built if page.kwargs.get("title") == "Weekly Updates")
    assert weekly.kwargs.get("visibility") == "default"
