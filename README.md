# Executive Delivery Dashboard (Streamlit)

Production-oriented scaffold for a Streamlit 1.55 executive delivery platform with:

- Native OIDC authentication flow (`st.login`, `st.logout`).
- Role and tenant-aware page composition.
- SQLAlchemy/Alembic-backed data layer for Aiven PostgreSQL.
- Azure DevOps PAT integration wrapper with migration-ready credential abstraction.
- Modular page architecture and service/repository split.

## Local run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Database migrations

```bash
alembic upgrade head
```

## Notes

- Copy `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` for local development.
- Do **not** commit real secrets.
