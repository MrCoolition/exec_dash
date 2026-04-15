# Executive Delivery Dashboard (Streamlit)

Production-oriented scaffold for a Streamlit 1.55 executive delivery platform with:

- Upstream Okta/Auth0 authentication with in-app troubleshooting diagnostics.
- Role and tenant-aware page composition.
- SQLAlchemy-backed data layer for Aiven PostgreSQL.
- Azure DevOps PAT integration wrapper with migration-ready credential abstraction.
- Modular page architecture and service/repository split.

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Notes

- Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` for local development.
- For Streamlit OIDC auth, use `[auth]` plus either inline credentials (`client_id`, `client_secret`, `server_metadata_url`) or a named provider block like `[auth.auth0]`.
- Database config supports either a full `database.url` (`postgresql+psycopg://...`) or Aiven-style `database.AIVEN_*` fields that are assembled into a psycopg URL automatically.
- Do **not** commit real secrets.
