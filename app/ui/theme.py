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
        .block-container { max-width: 1520px; padding-top: 2.75rem; }
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
        .priority-badge { display:inline-block; margin-top:6px; border:1px solid #d2e0ef; border-radius:999px; padding:4px 11px; font-size:.72rem; font-weight:700; }
        .priority-low { background:#eaf8f0; color:#23714e; border-color:#d7ebdf; }
        .priority-medium { background:#fff8e8; color:#946e16; border-color:#f1e3bf; }
        .priority-high { background:#fff0f0; color:#b94747; border-color:#f3d4d4; }
        .priority-critical { background:#fde9ea; color:#9f2229; border-color:#efc8cb; }
        .priority-neutral { background:#edf4ff; color:#46617d; }
        .risk-item { border-bottom:1px solid #edf3fb; padding:10px 0; }
        .risk-card { border:1px solid #d9e4f2; border-radius:14px; padding:12px; margin-bottom:10px; background:#fff; }
        .risk-head { display:flex; justify-content:space-between; gap:8px; }
        .risk-title { font-weight:700; color:#1a344f; }
        .risk-trend { color:#7a90a8; font-size:.78rem; }
        .risk-meta-row { display:flex; justify-content:space-between; gap:10px; margin-top:10px; }
        .risk-meta { margin-top:6px; }
        .risk-trend-worse { color:#df3c3c; font-weight:700; }
        .risk-trend-watch { color:#b98318; font-weight:700; }
        .risk-trend-stable { color:#768a9f; font-weight:700; }
        .roadmap-shell { background:#fff; border:1px solid #d7e4f2; border-radius:16px; padding:12px; }
        .road-quarter-row { display:flex; gap:14px; margin-bottom:10px; }
        .road-quarter { color:#8b9db1; font-size:.95rem; font-weight:600; }
        .road-quarter.active { color:#264fbe; font-weight:800; }
        .road-band { padding:10px 0; margin-bottom:10px; }
        .road-band-title { font-weight:800; color:#1a344f; margin-bottom:7px; font-size:1.02rem; }
        .road-band-track { position:relative; display:grid; grid-template-columns:repeat(5,1fr); border-radius:999px; overflow:hidden; }
        .road-band-segment { display:block; padding:11px 0; text-align:center; font-weight:700; font-size:1rem; color:#3d5782; background:#d6dde8; }
        .road-band-segment:nth-child(1) { background:#aebbe8; color:#3754ce; }
        .road-band-segment:nth-child(2) { background:#c0b1e4; color:#6942cc; }
        .road-band-segment:nth-child(3) { background:#3050b5; color:#fff; }
        .road-band-segment:nth-child(4) { background:#abd9ba; color:#1a854f; }
        .road-band-segment:nth-child(5) { background:#d3dae6; color:#7d90a9; }
        .road-band-segment.active { box-shadow: inset 0 0 0 3px rgba(255,255,255,.35); }
        .road-marker { position:absolute; top:-8px; transform:translateX(-50%); width:14px; height:52px; border-radius:4px; background:#2f6fed; }
        .road-marker-label { font-size:1rem; color:#1f4eca; margin-top:6px; font-weight:700; text-align:center; }
        .road-progress { margin-top:4px; font-size:.85rem; }
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
