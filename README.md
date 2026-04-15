# Executive Delivery Dashboard (Streamlit)

Production-oriented scaffold for a Streamlit 1.55 executive delivery platform with:

- Streamlit OIDC/Auth0 authentication using `st.login()`, `st.user`, and `st.logout()`.
- Role and tenant-aware page composition.
- SQLAlchemy-backed data layer for Aiven PostgreSQL.
- Azure DevOps PAT integration wrapper with migration-ready credential abstraction.
- Modular page architecture and service/repository split.

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Auth0 dashboard settings

Set only these values in your Auth0 Application settings for Streamlit Cloud:

- **Allowed Callback URLs**: `https://exec-dash.streamlit.app/oauth2callback`
- **Allowed Logout URLs**: `https://exec-dash.streamlit.app`
- **Allowed Web Origins**: `https://exec-dash.streamlit.app`

## Notes

- Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` for local development.
- Configure Streamlit OIDC provider settings under `[auth]` / `[auth.auth0]` in secrets for login to work.
- Database config supports either a full `database.url` (`postgresql+psycopg://...`) or Aiven-style `database.AIVEN_*` fields that are assembled into a psycopg URL automatically.
- Do **not** commit real secrets.
