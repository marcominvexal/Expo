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

4. Run the app:

   ```bash
   streamlit run main.py
   ```

## Security

Do not commit `secrets.env`, `.env`, or `service_account.json`. They are listed in `.gitignore`.
