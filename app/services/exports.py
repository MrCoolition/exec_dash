from __future__ import annotations

import io

import pandas as pd


def to_csv_bytes(rows: list[dict]) -> bytes:
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")


def to_xlsx_bytes(rows: list[dict]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
        pd.DataFrame(rows).to_excel(writer, index=False)
    return buf.getvalue()
