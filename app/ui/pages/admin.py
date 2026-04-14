from __future__ import annotations

import streamlit as st

from app.core.permissions import can_access_admin
from app.services.sync_runner import run_sync
from app.services.user_context import UserContext


def render(ctx: UserContext) -> None:
    if not can_access_admin(ctx):
        st.error("Admin access required.")
        return

    st.title("Admin")
    project = st.text_input("ADO Project", value="SampleProject")
    if st.button("Run Manual Sync"):
        with st.status("Syncing from Azure DevOps...", expanded=True):
            result = run_sync(project)
            st.write(result)
        st.toast("Sync completed")
