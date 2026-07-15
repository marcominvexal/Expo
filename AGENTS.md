# AGENTS.md

## Cursor Cloud specific instructions

ExponentiaBot is a single-product **Python + Streamlit** app (entrypoint `streamlit_app.py`; `mian.py` is a dead legacy placeholder). It reads unread Gmail quote emails over IMAP, extracts structured circuit rows with Google Gemini, and appends them to a Google Sheet. There is no local datastore, no test suite, and no lint config — all persistence/compute lives in three external SaaS APIs (Gmail IMAP, Gemini, Google Sheets).

### Environment
- Dependencies are installed by the update script into a virtualenv at `.venv/` (both `.venv/` and `service_account.json` are gitignored). Always invoke tools via `.venv/bin/...` (e.g. `.venv/bin/streamlit`, `.venv/bin/python`).

### Running the app (dev)
- `.venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0` (see also `render.yaml`'s start command). Health check: `curl http://localhost:8501/_stcore/health`.

### Non-obvious gotcha: the credential gate blocks the UI
- At page load `streamlit_app.py` calls `google_credentials_configured()` and, if it fails, `st.stop()` — so the UI renders **only an error** unless Google service-account credentials are present. Credentials are read from `service_account.json` in the repo root, a `[gcp_service_account]` block in `.streamlit/secrets.toml`, or `GCP_SERVICE_ACCOUNT*` env vars.
- This gate only validates the *format* of the key (it does not contact Google). A syntactically valid **dummy** `service_account.json` (any locally generated RSA key) is enough to render the full dashboard for UI/dev work.
- Any button that performs real work still needs real credentials: `GEMINI_API_KEY`, `EMAIL_USER`, `EMAIL_PASS` (Gmail app password), and a real service account whose `client_email` is shared on the target sheet (`SPREADSHEET_ID` is hardcoded in `streamlit_app.py`). With only dummy creds, clicking "Sync Gmail to Google Sheets" fails at the Google auth boundary (`invalid_grant`), which is expected.

### Testing
- No automated tests exist. Core business logic (currency/technology normalization, partner resolution, and Pakistan-holiday-aware TAT working-day math using `holidays.json`) is in pure functions in `streamlit_app.py` and can be exercised directly, but importing the module runs Streamlit module-level code, so ensure a (dummy is fine) `service_account.json` exists first to avoid the `st.stop()` gate.
