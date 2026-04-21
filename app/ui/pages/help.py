from __future__ import annotations

from app.ui.exec_reporting_views import render_html
from app.ui.pages.common import ensure_sidebar_state


def render() -> None:
    ensure_sidebar_state(current_page="Help & Support")
    render_html(
        "<div class='panel-header'><div class='eyebrow'>Support</div><div class='heading'>Help & Support</div><div class='copy'>Guidance for executives and program leads.</div></div>"
        "<div class='card'><div class='heading'>How to use this app</div><ul class='mini-list'>"
        "<li>Use <strong>Weekly Updates</strong> to submit the reporting cycle update.</li>"
        "<li>Use <strong>Program One-Pager</strong> for the executive view of a single program.</li>"
        "<li>Use <strong>Impower Portfolio</strong> for cross-program oversight.</li>"
        "</ul></div>"
        "<div class='card'><div class='heading'>Need assistance?</div><div class='copy'>For access or data support, contact PMO Support through your standard support channel.</div></div>"
    )
