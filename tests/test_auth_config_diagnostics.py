from app.core import auth
from streamlit.errors import StreamlitAuthError


def test_login_with_auth0_handles_streamlit_auth_error(monkeypatch):
    monkeypatch.setattr(
        auth.st,
        "login",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(StreamlitAuthError("bad auth config")),
    )
    captured_errors: list[str] = []
    monkeypatch.setattr(auth.st, "error", lambda msg: captured_errors.append(msg))

    auth.login_with_auth0()

    assert captured_errors
    assert "couldn't complete sign in" in captured_errors[0].lower()
