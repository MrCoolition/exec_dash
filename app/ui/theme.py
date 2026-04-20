from __future__ import annotations

import streamlit as st


COLORS = {
    "navy": "#2a4561",
    "blue": "#2f6fed",
    "blue_soft": "#7ea6f8",
    "teal": "#4d7fb3",
    "panel": "#ffffff",
    "border": "#d9e3f0",
    "text": "#506377",
    "muted": "#7f91a6",
    "soft": "#f6f8fc",
    "green": "#2e8b6f",
    "yellow": "#d3a23c",
    "red": "#cf5c5c",
}


def inject_theme_overrides() -> None:
    st.markdown(
        """
        <style>
        :root {
          --navy:#2a4561; --blue:#2f6fed; --blue-soft:#7ea6f8; --teal:#4d7fb3;
          --panel:#ffffff; --border:#d9e3f0; --text:#506377; --muted:#7f91a6;
          --soft:#f6f8fc; --green:#2e8b6f; --yellow:#d3a23c; --red:#cf5c5c;
        }
        .stApp { background: var(--soft); color: var(--text); }
        .block-container {padding-top: 2.75rem; max-width: 1320px;}
        .topbar, .dashboard-title-block, .dash-kpi, .dash-card, .weekly-hero, .ws-card, .decision-card {
            background: var(--panel); border:1px solid var(--border); border-radius: 14px;
        }
        .topbar {display:flex; gap:16px; justify-content:space-between; align-items:center; padding:14px; margin-bottom:10px;}
        .brand-title {font-size:1.05rem; font-weight:700; color:var(--navy)}
        .brand-copy,.dashboard-meta,.dash-card-copy,.profile-role {color:var(--muted); font-size:.83rem;}
        .search-shell {background:var(--soft); border:1px solid var(--border); border-radius:999px; padding:.45rem .9rem; min-width:280px; color:var(--muted)}
        .toolbar-actions{display:flex; gap:8px} .toolbar-icon{border:1px solid var(--border); border-radius:8px; padding:4px 8px;}
        .profile-shell{display:flex; gap:8px; align-items:center} .profile-avatar{background:var(--blue); color:white; width:30px; height:30px; border-radius:999px; display:flex; align-items:center; justify-content:center; font-size:.78rem;}
        .dashboard-title-block{padding:16px; margin-bottom:10px;} .dashboard-title{font-size:1.25rem; font-weight:700; color:var(--navy);}
        .update-pill,.status-pill{border-radius:999px;padding:.1rem .5rem; font-size:.72rem; border:1px solid var(--border)}
        .dash-kpi{padding:10px 12px} .dash-kpi-name{font-size:.78rem;color:var(--muted)} .dash-kpi-value{font-size:1.3rem;font-weight:700;color:var(--navy)}
        .dash-card{padding:12px; margin-bottom:10px;} .dash-card-title{font-size:.95rem; font-weight:700; color:var(--navy)}
        .dash-card-heading{font-weight:600; color:var(--text)}
        .dash-tag-green,.status-good{background:#e9f6f0;color:var(--green);border-color:#b7dfcf}
        .dash-tag-yellow,.status-warn{background:#fff8ea;color:#9e7618;border-color:#ead9a8}
        .dash-tag-red,.status-bad{background:#ffefef;color:var(--red);border-color:#efc3c3}
        .status-neutral{background:#eff4fb;color:var(--text)}
        .roadmap-grid,.timeline-grid,.workstream-grid{display:grid; gap:10px}
        .roadmap-grid{grid-template-columns:repeat(5,minmax(90px,1fr));}
        .road-band{background:var(--soft);border:1px solid var(--border);padding:8px;border-radius:10px;text-align:center;font-size:.8rem}
        .road-marker{margin-top:5px;font-size:.75rem;color:var(--muted)}
        .milestone-item,.risk-item{border-bottom:1px solid #edf2f8; padding:8px 0}
        .milestone-datebox{display:inline-block; text-align:center; background:var(--soft); border:1px solid var(--border); border-radius:8px; padding:4px 7px; min-width:42px}
        .milestone-day{font-weight:700;color:var(--navy)} .milestone-month{font-size:.72rem;color:var(--muted)}
        .risk-head{display:flex; justify-content:space-between; gap:8px;} .risk-title{font-weight:600} .risk-trend{font-size:.75rem;color:var(--muted)}
        .dash-table table{width:100%; border-collapse:collapse; font-size:.85rem} .dash-table th,.dash-table td{border-bottom:1px solid #edf2f8; padding:6px; text-align:left}
        .weekly-hero{background:linear-gradient(135deg,#213a54,#2a4561); color:white; padding:14px; margin-bottom:10px}
        .weekly-hero-title{font-size:1.2rem;font-weight:700} .weekly-status-dot,.hero-status-dot{width:10px;height:10px;border-radius:999px;display:inline-block;margin-right:6px;}
        .weekly-section-title{font-weight:700;color:var(--navy)} .weekly-section-copy{font-size:.83rem;color:var(--muted)}
        .risk-table table{width:100%; font-size:.83rem} .decision-card{padding:10px} .ws-card{padding:10px;background:var(--soft)}
        </style>
        """,
        unsafe_allow_html=True,
    )
