from __future__ import annotations

from datetime import datetime, timezone
import logging
import re
from urllib.parse import urlparse

import streamlit as st


_LOG = logging.getLogger(__name__)
_SENSITIVE_PATTERNS = (
    re.compile(r"(password|passwd|pwd|secret|token|apikey|api_key)\s*[:=]\s*[^\s,;]+", re.IGNORECASE),
    re.compile(r"(bearer\s+)[A-Za-z0-9\-._~+/]+=*", re.IGNORECASE),
)


def _mask(value: str, visible: int = 2) -> str:
    clean = str(value or "")
    if not clean:
        return "(missing)"
    if len(clean) <= visible:
        return "*" * len(clean)
    return f"{clean[:visible]}{'*' * (len(clean) - visible)}"


def _db_auth_diagnostics(exc: Exception) -> dict[str, str] | None:
    message = str(exc)
    lowered = message.lower()
    if "password authentication failed for user" not in lowered:
        return None

    details: dict[str, str] = {
        "error_type": type(exc).__name__,
        "failure": "PostgreSQL rejected credentials (password authentication failed)",
    }

    try:
        quoted_user_start = message.index('user "') + len('user "')
        quoted_user_end = message.index('"', quoted_user_start)
        user = message[quoted_user_start:quoted_user_end]
        details["db_user"] = _mask(user, visible=3)
    except ValueError:
        details["db_user"] = "(unavailable)"

    try:
        host_start = message.index('server at "') + len('server at "')
        host_end = message.index('"', host_start)
        details["db_host"] = message[host_start:host_end]
    except ValueError:
        details["db_host"] = "(unavailable)"

    try:
        port_token = "port "
        port_start = message.index(port_token) + len(port_token)
        port_end = message.index(" failed", port_start)
        details["db_port"] = message[port_start:port_end]
    except ValueError:
        details["db_port"] = "(unavailable)"

    try:
        parsed = urlparse(str(getattr(exc, "dsn", "") or ""))
        if parsed.path:
            details["db_name"] = parsed.path.lstrip("/") or "(missing)"
    except Exception:
        pass

    return details


def _sanitize_error_message(message: str) -> str:
    sanitized = str(message or "").strip()
    if not sanitized:
        return "(no error message)"
    for pattern in _SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\1=***", sanitized)
    if len(sanitized) > 260:
        sanitized = f"{sanitized[:257]}..."
    return sanitized


def _classify_issue(exc: Exception) -> tuple[str, list[str], bool]:
    message = str(exc or "")
    lowered = message.lower()
    kind = type(exc).__name__

    if _db_auth_diagnostics(exc):
        return (
            "infrastructure / database credentials",
            [
                "Database authentication failed before data could load.",
                "This is not a data quality problem in program records.",
            ],
            False,
        )

    data_issue_tokens = (
        "keyerror",
        "missing key",
        "column",
        "schema",
        "invalid literal",
        "nan",
        "none",
        "parse",
        "json",
        "validation",
        "pydantic",
        "valueerror",
        "indexerror",
    )
    if kind in {"KeyError", "ValueError", "TypeError", "IndexError"} or any(token in lowered for token in data_issue_tokens):
        return (
            "data mapping / payload quality",
            [
                "The app received data that did not match expected shape or type.",
                "Check recent upstream sync/import changes and malformed rows.",
            ],
            True,
        )

    return (
        "application logic / unknown",
        [
            "Failure happened inside app execution but cause is not yet classified.",
            "Use the diagnostics block below to inspect stack trace in logs by reference.",
        ],
        False,
    )


def render_internal_error(exc: Exception, context: str) -> None:
    request_id = datetime.now(timezone.utc).strftime("ERR-%Y%m%d-%H%M%S")
    _LOG.exception("Unhandled app error [%s] in %s", request_id, context, exc_info=exc)
    issue_category, issue_notes, likely_data_issue = _classify_issue(exc)
    exc_type = type(exc).__name__
    exc_message = _sanitize_error_message(str(exc))

    st.error("Something went wrong while loading this page.")
    st.caption(f"Reference: {request_id} (UTC)")
    st.info("Please retry. If the issue continues, contact support and include the reference above.")

    st.markdown("### Incident triage")
    st.markdown(f"- **Category:** {issue_category}")
    st.markdown(f"- **Likely data issue:** {'Yes' if likely_data_issue else 'No'}")
    for note in issue_notes:
        st.markdown(f"- {note}")

    db_diag = _db_auth_diagnostics(exc)
    if db_diag:
        st.warning("Database login failed. The app cannot load until DB credentials are corrected.")
        st.markdown("### Self-troubleshooting")
        st.markdown(
            "- Confirm `database.url` (or `AIVEN_*` secrets) uses the current DB username/password.\n"
            "- If password was rotated, update Streamlit secrets and redeploy/restart the app.\n"
            "- Ensure username has access to the configured database and host."
        )

        with st.expander("Diagnostic details", expanded=True):
            st.code(
                "\n".join(
                    (
                        f"reference={request_id}",
                        f"context={context}",
                        f"error_type={db_diag.get('error_type', '(unknown)')}",
                        f"failure={db_diag.get('failure', '(unknown)')}",
                        f"db_host={db_diag.get('db_host', '(unknown)')}",
                        f"db_port={db_diag.get('db_port', '(unknown)')}",
                        f"db_user={db_diag.get('db_user', '(unknown)')}",
                        f"db_name={db_diag.get('db_name', '(unknown)')}",
                    )
                ),
                language="text",
            )
        return

    with st.expander("Diagnostic details", expanded=True):
        st.code(
            "\n".join(
                (
                    f"reference={request_id}",
                    f"context={context}",
                    f"error_type={exc_type}",
                    f"error_message={exc_message}",
                    f"likely_data_issue={str(likely_data_issue).lower()}",
                    f"category={issue_category}",
                )
            ),
            language="text",
        )
