from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAuthError, StreamlitSecretNotFoundError


st.title("Finishing sign-in…")


def _safe_is_logged_in() -> bool:
    try:
        return bool(st.user.is_logged_in)
    except Exception:
        return False


try:
    callback_error = str(st.query_params.get("error", "")).strip()
    callback_description = str(st.query_params.get("error_description", "")).strip()

    if callback_error:
        st.error("Sign-in callback returned an error.")
        st.caption(callback_description or callback_error)
    elif _safe_is_logged_in():
        st.success("Sign-in complete. Redirecting to Exec Dash…")
        st.switch_page("streamlit_app.py")
    else:
        st.info("Continue to the app to complete sign-in.")
        if st.button("Continue", type="primary"):
            st.switch_page("streamlit_app.py")
except (StreamlitAuthError, StreamlitSecretNotFoundError):
    st.error("Unable to access the sign-in session right now. Please retry from the main app.")
    if st.button("Back to app"):
        st.switch_page("streamlit_app.py")
except Exception:
    st.error("Sign-in callback could not be processed. Please retry from the main app.")
    if st.button("Back to app"):
        st.switch_page("streamlit_app.py")
