import os
import imaplib
import email
import json
import re
import gspread
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials

# 1. Force reload environment variables (project secrets file first, then .env if present)
load_dotenv("secrets.env", override=True)
load_dotenv(override=True)

# Credentials Check
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = (os.getenv("EMAIL_PASS") or "").replace(" ", "")  # Removes accidental spaces

client = genai.Client(api_key=GEMINI_KEY)

# Google Sheets Setup
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
# Ensure service_account.json is in the same folder!
CREDS = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
G_CLIENT = gspread.authorize(CREDS)
SPREADSHEET_ID = "1jgbUhsKhD2fPH4l4q2kvWCQAfhXYka21KgBnOiTLfkc"
WORKSHEET_GID = 541908909
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={WORKSHEET_GID}"

def extract_thread_dates(body):
    date_patterns = re.findall(r'Sent: .*?, (.*?) [0-9]', body)
    dates = []
    for d_str in date_patterns:
        try:
            clean_date = d_str.split(' at ')[0].strip()
            dates.append(datetime.strptime(clean_date, "%B %d, %Y"))
        except:
            continue
    if not dates:
        return datetime.now(), datetime.now()
    return min(dates), max(dates)

def get_ai_extraction(email_body):
    prompt = f"Extract telecom quote details into a JSON list. Rules: One object per circuit row. Include '$' in NRC/MRC. Email text: {email_body}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={'response_mime_type': 'application/json'}
    )
    return json.loads(response.text)

def run_bot():
    mail = None
    try:
        # Open live Google Sheet tab
        spreadsheet = G_CLIENT.open_by_key(SPREADSHEET_ID)
        sheet = spreadsheet.get_worksheet_by_id(WORKSHEET_GID)
        existing_data = sheet.get_all_records()
        last_s_no = len(existing_data) + 1

        if not EMAIL_USER or not EMAIL_PASS:
            return "Set EMAIL_USER and EMAIL_PASS in secrets.env (use a Gmail App Password)."

        # Secure Gmail Connection
        st.info(f"Attempting login for: {EMAIL_USER}...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        # This is where the error usually happens
        mail.login(EMAIL_USER, EMAIL_PASS)

        mail.select("inbox")
        # Look for UNREAD emails
        _, messages = mail.search(None, 'UNSEEN')

        new_rows = []
        email_ids = messages[0].split()

        if not email_ids:
            return "No new (unread) emails found. Mark a quote email as 'Unread' to test."

        for num in email_ids:
            _, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])

            # Extract body correctly
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            opp_date, prop_date = extract_thread_dates(body)
            tat = (prop_date - opp_date).days
            circuits = get_ai_extraction(body)

            for c in circuits:
                new_rows.append([
                    last_s_no, c.get('Quote ID'), opp_date.strftime('%Y-%m-%d'),
                    c.get('Partner Name'), c.get('End Customer'), c.get('Site A'),
                    c.get('Site A City'), c.get('Site B', '-'), c.get('Site B City', '-'),
                    c.get('Technology'), c.get('Service/Product'), c.get('Capacity / Quantity'),
                    c.get('NRC'), c.get('MRC'), 'Email', prop_date.strftime('%Y-%m-%d'),
                    c.get('Contract Terms'), c.get('Sales Effort By'), c.get('Comments'),
                    'OPEN', 'MEDIUM', c.get('POC'), c.get('Contact Email Address'),
                    tat, c.get('On-Net/Off-Net'), c.get('LM Infra Details'),
                    'Unprotected', '-', '-', 'New Service'
                ])
                last_s_no += 1

        if new_rows:
            sheet.append_rows(new_rows)
            return f"✅ Success! Added {len(new_rows)} rows to the Google Sheet!"

        return "Unread emails processed, but no circuit rows were extracted by Gemini."

    except imaplib.IMAP4.error as e:
        return f"Gmail Login Failed: Make sure your App Password is correct and has no spaces. Error: {e}"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass

# Streamlit UI
st.set_page_config(page_title="Exponentia Sales Bot", page_icon="📞")
st.title("📞 Exponentia Global Live Funnel Bot")

st.markdown(f"""
### Instructions:
1. Make sure you have **Unread** emails in `{EMAIL_USER or 'your Gmail'}`.
2. Click the button below to process them using Gemini AI.
""")

if st.button("🚀 Sync Gmail to Google Sheets"):
    with st.spinner("Talking to Gmail & Gemini..."):
        result = run_bot()
        if result and "Success" in result:
            st.success(result)
        else:
            st.error(result or "Unknown error.")

st.divider()
st.write(f"📊 [View Live Google Sheet]({SHEET_URL})")
