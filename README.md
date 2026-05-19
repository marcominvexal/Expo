# ExponentiaBot

Sales funnel automation for **Exponentia Global**: sync unread Gmail quote emails to Google Sheets using Gemini AI.

## Features

- Reads unread quote emails via Gmail (IMAP)
- Extracts circuit rows with Gemini 2.5 Flash (strict JSON schema)
- Appends rows to the live Google Sheets funnel
- Streamlit UI for one-click sync

## Setup

1. Install Python 3.12+ and dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create `secrets.env` (not committed) with:

   ```
   GEMINI_API_KEY=your_key
   EMAIL_USER=your@gmail.com
   EMAIL_PASS=your_gmail_app_password
   ```

3. Place `service_account.json` in the project root and share your Google Sheet with the service account email.

4. Run the app locally:

   ```bash
   streamlit run streamlit_app.py
   ```

## Deploy

### Vercel (this repo)

Vercel only hosts the static info page in `public/`. The Streamlit app **cannot** run on Vercel serverless (no `main.py` entrypoint).

After pushing, Vercel should build without the Python entrypoint error.

### Streamlit Community Cloud (recommended for the live app)

1. Push this repo to GitHub.
2. Open [share.streamlit.io](https://share.streamlit.io) → **New app** → select the repo.
3. Set **Main file path** to `streamlit_app.py`.
4. Under **Secrets**, paste TOML like `.streamlit/secrets.toml.example` (Gemini + Gmail + `[gcp_service_account]` from your JSON file). Share the Google Sheet with the service account `client_email`.

5. Open your app URL (e.g. `https://exponentiabot-xxxxx.streamlit.app`).

### Render (alternative)

Use the included `render.yaml`, set env vars in the dashboard, and add `service_account.json` via a secret file mount or env.

## Security

Do not commit `secrets.env`, `.env`, or `service_account.json`. They are listed in `.gitignore`.
