from __future__ import annotations

import pandas as pd
import streamlit as st


def render_table(rows: list[dict]) -> None:
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
