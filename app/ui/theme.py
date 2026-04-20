from __future__ import annotations

import streamlit as st


def inject_theme_overrides() -> None:
    st.markdown(
        """
        <style>
        :root { --navy:#0f2d52; --blue:#2563eb; --bg:#f5f7fb; --card:#ffffff; --line:#dbe3f0; }
        .stApp { background: var(--bg); }
        .block-container {padding-top: 2.25rem; max-width: 1260px;}
        div[data-testid="stMetric"] {border: 1px solid var(--line); border-radius: 14px; background: var(--card); padding: .6rem;}
        .hero, .metric-card, .section-bar, .stDataFrame, div[data-testid="stVerticalBlock"] > div:has(> .stTextArea), .empty-state {
            border-radius: 14px;
        }
        .hero { background: linear-gradient(120deg, #163d6b, #1f5ca8); color: #fff; padding: 1rem 1.1rem; margin: .25rem 0 .85rem; }
        .hero h2 { margin: 0 0 .75rem; font-size: 1.35rem; }
        .hero-grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap: .5rem; }
        .hero-chip { background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22); border-radius: 10px; padding: .45rem .55rem; }
        .hero-chip span { display:block; font-size:.74rem; opacity:.9; }
        .section-bar { background:#eaf0fb; border:1px solid var(--line); padding:.5rem .75rem; font-weight:600; margin:.8rem 0 .55rem; }
        .section-subtitle { font-weight:400; color:#345; font-size:.85rem; }
        .metric-card { border:1px solid var(--line); background:var(--card); padding:.65rem .8rem; }
        .metric-title { color:#4a5f7a; font-size:.78rem; }
        .metric-value { color:#102a4e; font-size:1.35rem; font-weight:700; }
        .metric-sub { color:#4a5f7a; font-size:.75rem; }
        .status-pill { border-radius:999px; padding:.1rem .55rem; font-size:.72rem; font-weight:600; border:1px solid transparent; }
        .status-good { background:#e8f7ee; color:#0f7a3c; border-color:#a9e5bf; }
        .status-warn { background:#fff8e8; color:#916100; border-color:#f2d793; }
        .status-bad { background:#feeceb; color:#b42318; border-color:#f4b9b3; }
        .status-neutral { background:#edf2f8; color:#355; border-color:#d2deec; }
        .empty-state { border:1px dashed var(--line); padding:.9rem; color:#50627a; background:#fcfdff; }
        .milestone-line { display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #eef3fa; padding:.35rem 0; }
        @media (max-width: 900px) { .hero-grid { grid-template-columns: 1fr 1fr; } }
        </style>
        """,
        unsafe_allow_html=True,
    )
