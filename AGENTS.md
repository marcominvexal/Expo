# AGENTS.md

## Cursor Cloud specific instructions

ExponentiaBot is a single-product **Python + Streamlit** app (`streamlit_app.py`). It syncs unread Gmail quote emails → Gemini extraction → Google Sheets funnel. No local DB, no test suite, no lint config.

### Environment
- Use `.venv/bin/...` for all commands (deps installed by the update script).
- **Secrets layout:**
  - `secrets.env` (gitignored): `EMAIL_USER`, `EMAIL_PASS` (Gmail app password, spaces OK — code strips them).
  - `GEMINI_API_KEY`: Cursor secret / env var (read via `env_or_secret`).
  - Google Sheets: `service_account.json` in repo root (gitignored) **or** full JSON in `GCP_SERVICE_ACCOUNT_JSON` / Streamlit `[gcp_service_account]`. The Cursor secret name alone is not enough if it only holds a short path string — the file must contain the full JSON with `private_key`.
  - Share the funnel Google Sheet with the service account `client_email` from that JSON (Editor access).

### Run (dev)
```bash
.venv/bin/streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```
Health: `curl http://localhost:8501/_stcore/health`. Open via Desktop pane (`localhost:8501`), not public internet.

### Quote ID gotcha (critical)
- Quote IDs come from the email **body only**: one prefix letter **F–Z** + `###-##` (e.g. `I835-26`, `F780-23`, `G101-26`). Subject lines and Gemini partner refs (`QTE-…`, Colt numbers, PID/BID/SP) are ignored.
- The allowed letters live in one place: `QUOTE_ID_PREFIX_CLASS` in `streamlit_app.py`. Change it there, then update the Gemini prompt rule and the dashboard rules panel text to match.
- A wider range means partner refs shaped like `P123-26` can match in the full-body fallback; explicit `Quote ID:` labels and IDs near "Add & archive" take priority.

### Sync order
`run_bot()` opens Sheets first → Gmail IMAP → Gemini → writes rows. All three external creds must work.

### No automated tests
Smoke-check: Gmail login, Gemini ping, `get_funnel_worksheet()`, and `normalize_quote_id("QTE-…", body)` returning the body's `F###-##`…`Z###-##` ID (or `-` if none).
