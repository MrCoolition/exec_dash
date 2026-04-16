from __future__ import annotations

from datetime import datetime, timezone
import logging

import streamlit as st


_LOG = logging.getLogger(__name__)


def render_internal_error(exc: Exception, context: str) -> None:
    request_id = datetime.now(timezone.utc).strftime("ERR-%Y%m%d-%H%M%S")
    _LOG.exception("Unhandled app error [%s] in %s", request_id, context, exc_info=exc)

    st.error("Something went wrong while loading this page.")
    st.caption(f"Reference: {request_id} (UTC)")
    st.info("Please retry. If the issue continues, contact support and include the reference above.")
