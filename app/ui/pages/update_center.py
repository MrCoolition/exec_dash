from __future__ import annotations

import datetime as dt

import streamlit as st

from app.core.permissions import can_edit_updates
from app.services.user_context import UserContext


def render(ctx: UserContext) -> None:
    if not can_edit_updates(ctx):
        st.error("You do not have permission to access Update Center.")
        return

    st.title("Update Center")
    with st.form("weekly_update_form"):
        week_ending = st.date_input("Week Ending", value=dt.date.today())
        executive_summary = st.text_area("Executive Summary")
        accomplishments = st.text_area("Accomplishments")
        submitted = st.form_submit_button("Save Draft")
        if submitted:
            st.toast(f"Draft saved for week ending {week_ending}")
            st.success(f"Saved {len(executive_summary) + len(accomplishments)} characters")
