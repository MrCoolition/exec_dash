from __future__ import annotations

import streamlit as st


def inject_theme_overrides() -> None:
    st.markdown(
        """
        <style>
        .stApp {
          background:
            radial-gradient(1300px 420px at 12% -20%, #f7fbff 0%, transparent 60%),
            linear-gradient(180deg, #f2f7fd 0%, #eef4fb 100%);
          color: #3a526c;
        }
        .block-container { max-width: 1520px; padding-top: 1rem; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #ebf2fb 0%, #e1ecf8 100%); border-right: 1px solid #cfdded; }
        .topbar { display:grid; grid-template-columns:2.1fr 2.3fr auto auto; gap:12px; align-items:center; background:#fff; border:1px solid #d7e4f2; border-radius:16px; padding:14px; margin-bottom:12px; }
        .dashboard-title { font-size: 2rem; font-weight: 800; color: #16314d; line-height: 1.15; }
        .dashboard-title-block { background:#fff; border:1px solid #d7e4f2; border-radius:16px; padding:16px; margin-bottom:12px; }
        .dashboard-meta,.brand-copy,.copy,.profile-role { color:#758ba2; font-size:.84rem; }
        .dash-kpi { border-radius:18px; min-height:126px; background:linear-gradient(180deg,#fff 0%, #f8fbff 100%); border:1px solid #d9e6f3; padding:16px; box-shadow:0 10px 24px rgba(24,48,76,.05); }
        .dash-kpi-name { text-transform:uppercase; letter-spacing:.11em; color:#7a8fa5; font-size:.72rem; font-weight:700; }
        .dash-kpi-value { font-size:2rem; font-weight:800; color:#16314d; margin-top:8px; }
        .dashboard-main-grid { margin-top:8px; }
        .panel-header { margin:10px 0 8px; }
        .heading { font-size:1.02rem; font-weight:700; color:#19324e; }
        .program-grid { display:grid; gap:10px; }
        .program-grid-card { background:#fff; border:1px solid #d7e4f2; border-radius:14px; padding:12px; }
        .program-grid-head { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:6px; }
        .program-grid-title { font-weight:700; color:#19324e; }
        .program-grid-link { margin-top:10px; display:inline-block; background:#2f6fed; color:white; border-radius:999px; padding:8px 14px; font-weight:700; font-size:.8rem; }
        .milestone-item { display:grid; grid-template-columns:auto 1fr; gap:10px; padding:10px 0; border-bottom:1px solid #edf3fb; }
        .milestone-datebox { min-width:52px; border:1px solid #d6e3f2; border-radius:10px; background:#f5f9ff; text-align:center; padding:6px; }
        .priority-badge { display:inline-block; margin-top:6px; border:1px solid #d2e0ef; border-radius:999px; padding:2px 8px; font-size:.72rem; }
        .risk-item { border-bottom:1px solid #edf3fb; padding:10px 0; }
        .risk-head { display:flex; justify-content:space-between; gap:8px; }
        .risk-title { font-weight:700; color:#1a344f; }
        .risk-trend { color:#7a90a8; font-size:.78rem; }
        .road-band { background:#fff; border:1px solid #d7e4f2; border-radius:12px; padding:10px; margin-bottom:8px; }
        .road-band-segment { display:inline-block; margin:4px 5px 0 0; padding:3px 8px; border-radius:999px; border:1px solid #d5e2f0; font-size:.72rem; color:#617994; }
        .road-band-segment.active { background:#2f6fed; color:#fff; border-color:#2f6fed; }
        .road-marker { width:10px; height:10px; border-radius:50%; background:#2f6fed; margin-top:7px; }
        .road-marker-label { font-size:.76rem; color:#6a8199; margin-top:4px; }
        .decision-shell { display:grid; grid-template-columns:repeat(3,minmax(220px,1fr)); gap:10px; }
        .decision-card { background:#fff; border:1px solid #d7e4f2; border-radius:12px; padding:12px; }
        .update-pill,.status-pill { border-radius:999px; padding:3px 8px; border:1px solid #d4e2f0; font-size:.72rem; }
        .dash-tag-green,.status-good{ background:#eaf8f0; color:#23714e; }
        .dash-tag-yellow{ background:#fff8e8; color:#946e16; }
        .dash-tag-red{ background:#fff0f0; color:#b94747; }
        .dash-tag-neutral{ background:#edf4ff; color:#46617d; }
        .weekly-hero { background:linear-gradient(135deg,#10233b,#1b3553); color:#fff; border-radius:18px; padding:18px; border:1px solid rgba(255,255,255,.16); }
        .ws-card { background:#fff; border:1px solid #d9e6f3; border-radius:12px; padding:10px; }
        .ws-bar { height:8px; border-radius:999px; background:#e8eff8; overflow:hidden; }
        .ws-bar span { display:block; height:100%; background:#2f6fed; }
        .timeline-node{ }
        </style>
        """,
        unsafe_allow_html=True,
    )
