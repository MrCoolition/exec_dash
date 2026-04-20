# Executive Delivery Dashboard (Streamlit)

Production-oriented scaffold for a Streamlit executive delivery platform with:

- Streamlit native OIDC/Auth0 authentication using `st.login()`, `st.user`, and `st.logout()`.
- Role and tenant-aware page composition.
- psycopg2-backed data layer for PostgreSQL with connection pooling.
- Azure DevOps PAT integration wrapper with migration-ready credential abstraction.
- `st.navigation(...)`-based page architecture.

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Auth0 + Streamlit OIDC requirements

### Callback architecture

- Streamlit handles OAuth callback processing at the built-in root callback endpoint: `/oauth2callback`.
- Do **not** add a custom callback page in `pages/`.
- This app uses `st.navigation(...)`, so `pages/` is not part of runtime routing.

### Auth0 dashboard settings (Regular Web Application)

Set these values in Auth0 for the production deployment:

- **Application Type**: `Regular Web Application`
- **Allowed Callback URLs**: `https://exec-dash.streamlit.app/oauth2callback`
- **Allowed Logout URLs**: `https://exec-dash.streamlit.app`
- **Allowed Web Origins**: `https://exec-dash.streamlit.app`

### Streamlit secrets shape

Runtime auth supports only canonical Streamlit OIDC secrets:

```toml
[auth]
redirect_uri = "https://exec-dash.streamlit.app/oauth2callback"
cookie_secret = "<LONG_RANDOM_SECRET>"

[auth.auth0]
client_id = "<AUTH0_CLIENT_ID>"
client_secret = "<AUTH0_CLIENT_SECRET>"
server_metadata_url = "https://<AUTH0_TENANT_DOMAIN>/.well-known/openid-configuration"
```

## Notes

- Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` for local development.
- Database config supports either `database.url` (`postgresql://...`) or Aiven-style `database.AIVEN_*` fields that are assembled into a psycopg URL automatically.
- Do **not** commit real secrets.
