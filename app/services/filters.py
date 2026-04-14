from __future__ import annotations

import streamlit as st


def render_global_filters(tenant_options: list[str]) -> dict[str, str]:
    tenant = st.selectbox("Tenant", tenant_options, key="tenant", accept_new_options=False)
    timeframe = st.segmented_control("Timeframe", ["7d", "30d", "90d"], key="timeframe", default="30d")
    return {"tenant": tenant, "timeframe": timeframe}
