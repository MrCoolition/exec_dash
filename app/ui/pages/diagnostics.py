from __future__ import annotations

import streamlit as st

from app.core.permissions import can_access_admin
from app.services.user_context import UserContext


def render(ctx: UserContext) -> None:
    if not can_access_admin(ctx):
        st.error("Diagnostics access requires admin role.")
        return

    st.title("Diagnostics")
    st.dataframe([
        {"dataset": "work_items", "last_success": "n/a", "status": "unknown"},
        {"dataset": "iterations", "last_success": "n/a", "status": "unknown"},
    ], use_container_width=True)
