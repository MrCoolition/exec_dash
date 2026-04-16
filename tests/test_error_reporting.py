from app.core import error_reporting


def test_render_internal_error_is_generic(monkeypatch):
    captured_errors: list[str] = []
    captured_captions: list[str] = []
    captured_info: list[str] = []
    monkeypatch.setattr(error_reporting.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(error_reporting.st, "caption", lambda msg: captured_captions.append(msg))
    monkeypatch.setattr(error_reporting.st, "info", lambda msg: captured_info.append(msg))

    error_reporting.render_internal_error(RuntimeError("db creds secret=abc"), context="unit")

    assert captured_errors == ["Something went wrong while loading this page."]
    assert captured_captions and captured_captions[0].startswith("Reference: ERR-")
    assert captured_info
