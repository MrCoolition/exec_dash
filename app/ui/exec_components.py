from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from app.ui.exec_formatters import status_class, status_label


def render_html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def status_tag(status: str | None) -> str:
    return f"<span class='status-pill {escape(status_class(status))}'>{escape(status_label(status))}</span>"


def dashboard_status_tag(status: str | None) -> str:
    css = status_class(status).replace("status", "dash-tag")
    return f"<span class='update-pill {escape(css)}'>{escape(status_label(status))}</span>"


def metric_card(title: str, value: str | int, note: str | None = None) -> str:
    note_html = f"<div class='dash-card-copy'>{escape(note)}</div>" if note else ""
    return (
        "<div class='dash-kpi'>"
        f"<div class='dash-kpi-name'>{escape(title)}</div>"
        f"<div class='dash-kpi-value'>{escape(str(value))}</div>{note_html}"
        "</div>"
    )


def hero_block(title: str, chips: list[tuple[str, str]]) -> None:
    chip_html = "".join(
        f"<span class='update-pill'><strong>{escape(k)}:</strong> {escape(v)}</span>" for k, v in chips
    )
    render_html(
        f"<div class='dashboard-title-block'><div class='dashboard-title'>{escape(title)}</div>"
        f"<div style='margin-top:8px;display:flex;flex-wrap:wrap;gap:6px'>{chip_html}</div></div>"
    )


def section_bar(title: str, subtitle: str | None = None) -> None:
    subtitle_html = f"<div class='dash-card-copy'>{escape(subtitle)}</div>" if subtitle else ""
    render_html(
        f"<div class='dash-card' style='padding:8px 12px'><div class='dash-card-title'>{escape(title)}</div>{subtitle_html}</div>"
    )


def empty_state(message: str) -> None:
    render_html(f"<div class='dash-card'><div class='dash-card-copy'>{escape(message)}</div></div>")


def render_html_table(df: pd.DataFrame, columns: list[str], rename_map: dict[str, str] | None = None) -> None:
    if df.empty:
        empty_state("No records to display.")
        return
    frame = df.loc[:, [c for c in columns if c in df.columns]].copy()
    if rename_map:
        frame = frame.rename(columns=rename_map)
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = "".join(f"<td>{escape('' if pd.isna(v) else str(v))}</td>" for v in row)
        rows.append(f"<tr>{cells}</tr>")
    render_html(f"<div class='dash-card dash-table'><table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>")
