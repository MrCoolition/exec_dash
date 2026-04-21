from app.core import error_reporting


def test_render_internal_error_is_generic(monkeypatch):
    captured_errors: list[str] = []
    captured_captions: list[str] = []
    captured_info: list[str] = []
    captured_markdown: list[str] = []
    captured_code: list[str] = []
    monkeypatch.setattr(error_reporting.st, "error", lambda msg: captured_errors.append(msg))
    monkeypatch.setattr(error_reporting.st, "caption", lambda msg: captured_captions.append(msg))
    monkeypatch.setattr(error_reporting.st, "info", lambda msg: captured_info.append(msg))
    monkeypatch.setattr(error_reporting.st, "markdown", lambda msg: captured_markdown.append(msg))

    class _Expander:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(error_reporting.st, "expander", lambda *args, **kwargs: _Expander())
    monkeypatch.setattr(error_reporting.st, "code", lambda msg, language="text": captured_code.append(msg))

    error_reporting.render_internal_error(RuntimeError("db creds secret=abc"), context="unit")

    assert captured_errors == ["Something went wrong while loading this page."]
    assert captured_captions and captured_captions[0].startswith("Reference: ERR-")
    assert captured_info
    assert any("Incident triage" in line for line in captured_markdown)
    assert captured_code and "secret=***" in captured_code[0]


def test_render_internal_error_classifies_data_issue(monkeypatch):
    captured_markdown: list[str] = []

    monkeypatch.setattr(error_reporting.st, "error", lambda _msg: None)
    monkeypatch.setattr(error_reporting.st, "caption", lambda _msg: None)
    monkeypatch.setattr(error_reporting.st, "info", lambda _msg: None)
    monkeypatch.setattr(error_reporting.st, "warning", lambda _msg: None)
    monkeypatch.setattr(error_reporting.st, "code", lambda _msg, language="text": None)
    monkeypatch.setattr(error_reporting.st, "markdown", lambda msg: captured_markdown.append(msg))

    class _Expander:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(error_reporting.st, "expander", lambda *args, **kwargs: _Expander())

    error_reporting.render_internal_error(KeyError("missing key: owner"), context="unit")

    assert any("Likely data issue:** Yes" in line for line in captured_markdown)
