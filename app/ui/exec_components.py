from __future__ import annotations

import streamlit as st

from app.ui.exec_formatters import format_date, status_class, status_label


def render_html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def status_tag(status: str | None) -> str:
    return f"<span class='status-pill {status_class(status)}'>{status_label(status)}</span>"


def metric_card(title: str, value: str, subtitle: str | None = None) -> None:
    subtitle_html = f"<div class='metric-sub'>{subtitle}</div>" if subtitle else ""
    render_html(
        f"""
        <div class='metric-card'>
            <div class='metric-title'>{title}</div>
            <div class='metric-value'>{value}</div>
            {subtitle_html}
        </div>
        """
    )


def section_bar(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f"<div class='section-subtitle'>{subtitle}</div>" if subtitle else ""
    render_html(f"<div class='section-bar'><div>{title}</div>{subtitle_html}</div>")


def hero_block(title: str, chips: list[tuple[str, str]]) -> None:
    chips_html = "".join([f"<div class='hero-chip'><span>{k}</span><strong>{v}</strong></div>" for k, v in chips])
    render_html(f"<div class='hero'><h2>{title}</h2><div class='hero-grid'>{chips_html}</div></div>")


def empty_state(message: str) -> None:
    render_html(f"<div class='empty-state'>{message}</div>")


def milestone_line(item: dict) -> str:
    name = item.get("milestone_name") or "Milestone"
    date_text = format_date(item.get("forecast_date") or item.get("planned_date"))
    tag = status_tag(item.get("status"))
    return f"<div class='milestone-line'><div><strong>{name}</strong><br/><small>{date_text}</small></div>{tag}</div>"
