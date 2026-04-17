from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAuthError, StreamlitSecretNotFoundError


st.title("Finishing sign-in…")

try:
    if st.user.is_logged_in:
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
