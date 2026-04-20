from __future__ import annotations

import streamlit as st

from app.repositories.work_items import count_by_state
from app.services.rollups import overview_rollup
from app.ui.charts import status_mix_chart


def render() -> None:
    st.title("Overview")
    mock_items = [{"state": "Done", "is_overdue": False}, {"state": "Active", "is_overdue": True}]
    rollup = overview_rollup(mock_items)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", rollup["total"])
    c2.metric("Complete", rollup["complete"])
    c3.metric("Overdue", rollup["overdue"])
    c4.metric("Completion", f"{rollup['completion_percent']}%")
    st.altair_chart(status_mix_chart(count_by_state() or [("Done", 1), ("Active", 1)]), width="stretch")
