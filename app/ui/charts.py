from __future__ import annotations

import altair as alt
import pandas as pd


def status_mix_chart(rows: list[tuple[str, int]]) -> alt.Chart:
    df = pd.DataFrame(rows, columns=["state", "count"])
    return alt.Chart(df).mark_bar().encode(x="state:N", y="count:Q", color="state:N")
