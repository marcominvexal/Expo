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
- Production on `main` may still use old Gemini-only Quote ID logic and write subject refs (`QTE-…`, Colt numbers).
- Fix branch `cursor/harden-quote-id-extraction-e4ce` forces **body-only** `I###-##` / `F###-##` and ignores Subject + Gemini partner refs. Merge PR #2 before relying on Streamlit Cloud output.

### Sync order
`run_bot()` opens Sheets first → Gmail IMAP → Gemini → writes rows. All three external creds must work.

### No automated tests
Smoke-check: Gmail login, Gemini ping, `get_funnel_worksheet()`, and `normalize_quote_id("QTE-…", body)` returning `I###-##`.
