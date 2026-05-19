import os
import imaplib
import email
from email.utils import parseaddr
import json
import re
import gspread
import streamlit as st
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials

# Local secrets (Streamlit Cloud uses st.secrets instead)
load_dotenv("secrets.env", override=True)
load_dotenv(override=True)

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_ID = "1jgbUhsKhD2fPH4l4q2kvWCQAfhXYka21KgBnOiTLfkc"
WORKSHEET_GID = 541908909
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid={WORKSHEET_GID}"


def env_or_secret(key, default=None):
    """Read from environment (local) or Streamlit Cloud secrets."""
    value = os.getenv(key)
    if value:
        return value
    try:
        return st.secrets[key]
    except Exception:
        return default


def load_google_credentials():
    """Local file, JSON env var, or [gcp_service_account] in Streamlit secrets."""
    try:
        if "gcp_service_account" in st.secrets:
            return Credentials.from_service_account_info(
                dict(st.secrets["gcp_service_account"]), scopes=SCOPE
            )
    except Exception:
        pass

    raw = env_or_secret("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        data = json.loads(raw) if isinstance(raw, str) else dict(raw)
        return Credentials.from_service_account_info(data, scopes=SCOPE)

    if os.path.isfile("service_account.json"):
        return Credentials.from_service_account_file("service_account.json", scopes=SCOPE)

    raise FileNotFoundError(
        "Google credentials missing. Add service_account.json locally or "
        "gcp_service_account in Streamlit Cloud secrets (see README)."
    )


@st.cache_resource
def get_gspread_client():
    return gspread.authorize(load_google_credentials())


@st.cache_resource
def get_genai_client():
    key = env_or_secret("GEMINI_API_KEY")
    if not key:
        raise ValueError("Set GEMINI_API_KEY in secrets.env or Streamlit secrets.")
    return genai.Client(api_key=key)


_COMMERCIAL_HINTS = (
    "nrc", "mrc", "commercial", "quote id", "circuit", "mbps", "gbps",
    "monthly", "one-time", "one time", "otc", "pricing", "proposal",
    "contract term", "usd", "$", "rate",
)

_DATE_PARSE_FORMATS = (
    "%B %d, %Y",
    "%b %d, %Y",
    "%d %B %Y",
    "%d %b %Y",
    "%a, %b %d, %Y",
    "%A, %B %d, %Y",
)


def parse_email_date(date_str):
    if not date_str:
        return None
    clean = re.sub(r"\s+", " ", date_str.split(" at ")[0].strip())
    clean = re.sub(r"^\w+day,?\s+", "", clean, flags=re.IGNORECASE)
    for fmt in _DATE_PARSE_FORMATS:
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            continue
    return None


def is_team_sender(from_line, email_user):
    """Exponentia mailbox or domain — commercials sent from team."""
    if not from_line:
        return False
    _, addr = parseaddr(from_line)
    addr = (addr or "").lower().strip()
    user = (email_user or "").lower().strip()
    if user and (addr == user or user in from_line.lower()):
        return True
    return is_exponentia_email(addr) or is_exponentia_name(from_line)


def looks_like_commercials(text):
    """Heuristic: team reply that likely contains pricing / quote table."""
    if not text:
        return False
    lowered = text.lower()
    return sum(1 for hint in _COMMERCIAL_HINTS if hint in lowered) >= 2


def extract_thread_messages(body):
    """Parse forwarded thread into dated messages with sender role."""
    messages = []
    for chunk in re.split(r"(?i)(?=From:\s*)", body):
        chunk = chunk.strip()
        if not chunk:
            continue

        from_line = ""
        body_text = chunk
        if re.match(r"(?i)From:\s*", chunk):
            header_end = chunk.find("\n")
            if header_end == -1:
                from_line = re.sub(r"(?i)^From:\s*", "", chunk).strip()
                body_text = ""
            else:
                from_line = re.sub(r"(?i)^From:\s*", "", chunk[:header_end]).strip()
                body_text = chunk[header_end + 1 :]

        sent_match = re.search(
            r"Sent:\s*(?:\w+day,?\s+)?(.*?)(?:\s+\d{1,2}:\d{2}(?:\s*[AP]M)?|\s+\d{4})",
            body_text,
            re.IGNORECASE,
        )
        if not sent_match:
            sent_match = re.search(r"Sent: .*?, (.*?) \d", body_text)

        if not sent_match:
            continue

        sent_at = parse_email_date(sent_match.group(1))
        if not sent_at:
            continue

        messages.append(
            {
                "date": sent_at,
                "from": from_line,
                "body": body_text,
            }
        )

    return messages


def extract_thread_dates(body, email_user):
    """
    Opportunity date: first partner email for this RFQ (RFQ received).
    Proposal date: when Exponentia sends commercials / pricing to the customer.
    """
    messages = extract_thread_messages(body)
    for msg in messages:
        msg["is_team"] = is_team_sender(msg["from"], email_user)
        msg["is_partner"] = bool(msg["from"]) and not msg["is_team"]

    if not messages:
        now = datetime.now()
        return now, now

    messages.sort(key=lambda m: m["date"])

    partner_messages = [m for m in messages if m["is_partner"]]
    if partner_messages:
        opportunity_date = partner_messages[0]["date"]
    else:
        opportunity_date = messages[0]["date"]

    team_after_opp = [
        m for m in messages
        if m["is_team"] and m["date"].date() >= opportunity_date.date()
    ]
    commercial_replies = [m for m in team_after_opp if looks_like_commercials(m["body"])]

    if commercial_replies:
        proposal_date = commercial_replies[0]["date"]
    elif team_after_opp:
        proposal_date = team_after_opp[0]["date"]
    else:
        proposal_date = opportunity_date

    if proposal_date.date() < opportunity_date.date():
        proposal_date = opportunity_date

    return opportunity_date, proposal_date


def calculate_tat(opportunity_date, proposal_date):
    """Days from RFQ receipt to commercials sent, excluding the receipt day."""
    delta_days = (proposal_date.date() - opportunity_date.date()).days
    return max(0, delta_days - 1)


def parse_currency_number(value):
    if value is None:
        return None
    text = str(value).strip()
    if text in ("", "-"):
        return None
    cleaned = re.sub(r"[^\d.\-]", "", text.replace(",", ""))
    if not cleaned or cleaned in (".", "-", "-."):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


SHEET_DATE_FORMAT = "%d-%B-%Y"  # e.g. 19-May-2026
# Column indices (0-based) for Opportunity Date (C) and Proposal Date (P)
SHEET_DATE_COLUMN_INDICES = (2, 15)

_DATE_PARSE_FORMATS = (
    SHEET_DATE_FORMAT,
    "%B, %d' %y",
    "%B %d, %Y",
    "%Y-%m-%d",
    "%B-%d-%Y",
    "%B-%d-%y",
    "%b-%d-%y",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%d-%b-%Y",
    "%d %B %Y",
)


def col_index_to_letter(index):
    """Convert 0-based column index to sheet letter (0 -> A, 15 -> P)."""
    n = index + 1
    letters = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def parse_sheet_date_value(value):
    """Parse a sheet cell into datetime, or None if not a date."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        try:
            return datetime(1899, 12, 30) + timedelta(days=float(value))
        except (ValueError, OverflowError):
            return None

    text = str(value).strip()
    if not text or text == "-":
        return None

    if re.fullmatch(r"\d+(\.\d+)?", text):
        try:
            return datetime(1899, 12, 30) + timedelta(days=float(text))
        except (ValueError, OverflowError):
            pass

    for fmt in _DATE_PARSE_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def format_sheet_date(value):
    """Format dates for the sheet as dd-Month-yyyy (e.g. 19-May-2026)."""
    if value is None:
        return "-"
    parsed = value if isinstance(value, datetime) else parse_sheet_date_value(value)
    if parsed is not None:
        return parsed.strftime(SHEET_DATE_FORMAT)
    text = str(value).strip()
    return text if text else "-"


def get_funnel_worksheet():
    spreadsheet = get_gspread_client().open_by_key(SPREADSHEET_ID)
    return spreadsheet.get_worksheet_by_id(WORKSHEET_GID)


def reformat_existing_sheet_dates():
    """Rewrite Opportunity and Proposal date columns to dd-Month-yyyy for all rows."""
    sheet = get_funnel_worksheet()
    all_values = sheet.get_all_values()
    if not all_values:
        return "Sheet is empty — nothing to update."

    batch = []
    updated_cells = 0

    for row_idx, row in enumerate(all_values):
        if row_idx == 0:
            continue
        row_num = row_idx + 1
        for col_idx in SHEET_DATE_COLUMN_INDICES:
            if col_idx >= len(row):
                continue
            raw = row[col_idx]
            parsed = parse_sheet_date_value(raw)
            if parsed is None:
                continue
            formatted = format_sheet_date(parsed)
            if str(raw).strip() == formatted:
                continue
            col_letter = col_index_to_letter(col_idx)
            batch.append({"range": f"{col_letter}{row_num}", "values": [[formatted]]})
            updated_cells += 1

    if not batch:
        return "All dates already use dd-Month-yyyy (e.g. 19-May-2026)."

    sheet.batch_update(batch, value_input_option="USER_ENTERED")
    row_nums = set()
    for item in batch:
        digits = "".join(ch for ch in item["range"] if ch.isdigit())
        if digits:
            row_nums.add(int(digits))
    return (
        f"Updated {updated_cells} date cell(s) across {len(row_nums)} row(s) "
        "to dd-Month-yyyy (e.g. 19-May-2026)."
    )


def format_currency(value):
    """Format NRC/MRC for the sheet as $1,234.00 (or numeric when parseable)."""
    num = parse_currency_number(value)
    if num is not None:
        return num
    text = str(value).strip() if value is not None else "-"
    if not text or text == "-":
        return "-"
    if "$" in text:
        return text
    return f"${text}"


MEDIA_FIBER = "Fiber"
MEDIA_WIRELESS = "Wireless"
ALLOWED_MEDIA = {MEDIA_FIBER, MEDIA_WIRELESS}

EXPONENTIA_NAMES = (
    "exponentia global",
    "exponentia",
    "exponentiaglobal",
    "exponentia global llc",
)
EXPONENTIA_EMAIL_DOMAINS = (
    "exponentiaglobal.com",
    "exponentia.com",
)


def normalize_media(value, lm_infra=None):
    """Restrict Media column to Fiber or Wireless only."""
    combined = " ".join(
        str(part or "")
        for part in (value, lm_infra)
    ).lower()

    wireless_hints = (
        "wireless", "radio", "microwave", "wifi", "wi-fi", "lte", "5g", "4g",
        "fixed wireless", "airfiber",
    )
    fiber_hints = (
        "fiber", "fibre", "ftth", "fttx", "fttp", "dark fiber", "pon", "gpon",
    )

    if any(h in combined for h in wireless_hints):
        return MEDIA_WIRELESS
    if any(h in combined for h in fiber_hints):
        return MEDIA_FIBER

    text = str(value or "").strip()
    if text in ALLOWED_MEDIA:
        return text
    if text.lower() in ("fiber", "fibre"):
        return MEDIA_FIBER
    if text.lower() == "wireless":
        return MEDIA_WIRELESS

    return MEDIA_FIBER


def is_exponentia_name(value):
    if not value:
        return False
    normalized = re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()
    return any(name in normalized or normalized in name for name in EXPONENTIA_NAMES)


def is_exponentia_email(email_address):
    if not email_address:
        return False
    address = email_address.lower().strip()
    return any(domain in address for domain in EXPONENTIA_EMAIL_DOMAINS)


def partner_from_email_sender(email_from):
    """Partner is the external entity who emailed Exponentia (From header)."""
    if not email_from:
        return None

    display_name, email_address = parseaddr(email_from)
    display_name = (display_name or "").strip().strip('"').strip("'")
    email_address = (email_address or "").strip().lower()

    if is_exponentia_email(email_address) or is_exponentia_name(display_name):
        return None

    if display_name and not is_exponentia_name(display_name):
        return display_name

    if email_address and "@" in email_address:
        domain_label = email_address.split("@")[-1].split(".")[0]
        generic_mailboxes = {"gmail", "yahoo", "hotmail", "outlook", "live", "icloud"}
        if domain_label and domain_label not in generic_mailboxes and not is_exponentia_name(domain_label):
            return domain_label.replace("-", " ").replace("_", " ").title()

    return None


def normalize_partner_name(partner, email_from=None):
    """
    Partner Name = channel partner who emails Exponentia (not End Customer, not Exponentia).
    """
    partner = (partner or "").strip()

    if partner and not is_exponentia_name(partner):
        return partner

    sender_partner = partner_from_email_sender(email_from)
    if sender_partner:
        return sender_partner

    return "-"


def extract_contract_term_labels(text):
    """Find distinct contract terms like 12/24/36 months in a single string."""
    if not text:
        return []
    labels = []
    seen = set()
    for match in re.finditer(
        r"\b(12|24|36|48|60)\s*(?:month|months|mo\.?|mths?)\b",
        str(text),
        re.IGNORECASE,
    ):
        label = f"{match.group(1)} Months"
        key = match.group(1)
        if key not in seen:
            seen.add(key)
            labels.append(label)
    return labels


def split_currency_values(value):
    """Pull multiple $ amounts from one cell (e.g. multi-term pricing columns)."""
    if value is None:
        return []
    text = str(value).strip()
    if not text or text == "-":
        return []
    amounts = re.findall(r"\$[\d,]+(?:\.\d{2})?", text)
    if not amounts:
        amounts = re.findall(r"(?<!\d)(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})(?!\d)", text)
    return amounts


def expand_circuits_by_contract_terms(circuits):
    """
    One sheet row per contract term. When a table row lists 12/24/36 month
    pricing together, split into separate entries with matching NRC/MRC when possible.
    """
    expanded = []
    for circuit in circuits:
        terms = extract_contract_term_labels(circuit.get("Contract Terms", ""))
        if len(terms) <= 1:
            expanded.append(circuit)
            continue

        mrc_values = split_currency_values(circuit.get("MRC"))
        nrc_values = split_currency_values(circuit.get("NRC"))

        for index, term in enumerate(terms):
            row = dict(circuit)
            row["Contract Terms"] = term
            if index < len(mrc_values):
                row["MRC"] = mrc_values[index]
            if index < len(nrc_values):
                row["NRC"] = nrc_values[index]
            expanded.append(row)

    return expanded


def get_ai_extraction(email_body):
    prompt = f"""
    You are an expert telecom data verification entity. Extract quoting matrix rows into clean structured objects.

    CRITICAL ALIGNMENT RULES:
    1. Quote ID: Must look for a clean tracking identifier format matching expressions like 'I698-26' or 'F780-23'. Do NOT extract subject titles or overall RFQ names.
    2. Capacity / Quantity: Must explicitly state the metric unit. E.g., change '50' or '20' into '50 Mbps' or '20 Gbps'.
    3. Strict Tech/Service Mapping: You MUST conform to this relational taxonomy precisely:
       - If Service is DIA or BIA -> Technology MUST be 'Internet'
       - If Service is L2VPN or MPLS -> Technology MUST be 'Ethernet'
       - If Service is IPLC, IEPL, EoSDH, DPLC, or DEPL -> Technology MUST be 'TDM'
       - If Service is Colocation + PWR -> Technology MUST be 'Datacenter'
       - If Service is Cross Connects, Equipment, or Field Support -> Technology MUST be 'Managed Services / Hardware'
    4. Media: MUST be exactly 'Fiber' or 'Wireless' only (no other values). Use 'Fiber' for fiber/FTTH/ethernet over fiber; use 'Wireless' for radio/microwave/fixed wireless/LTE.
    5. Partner Name vs End Customer (these are DIFFERENT columns — do not confuse them):
       - Partner Name: The external company that EMAILS Exponentia Global to request a quote (channel partner, reseller, agent).
         Example: 'Noor Data Network'. MUST NEVER be 'Exponentia Global' (we are the provider).
       - End Customer: The final client organization the partner is quoting for (brought by the partner to Exponentia).
         Example: 'Baker Hughes'. A partner can bring many different end customers.
       - Do NOT put End Customer into Partner Name. Do NOT put Exponentia Global into Partner Name.
    6. Contract Terms — one row per term (CRITICAL for pricing tables):
       - If a single table row shows multiple contract terms (e.g. columns or cells for
         12 month, 24 month, 36 month), you MUST output a SEPARATE object for EACH term.
       - Do NOT combine 12/24/36 into one object or one Contract Terms field.
       - Each object keeps the same circuit details (Quote ID, sites, technology, service,
         capacity, partner, end customer, etc.) but exactly ONE Contract Terms value
         (e.g. '12 Months', '24 Months', '36 Months').
       - NRC and MRC must be the values for THAT term only (from that column/cell), not
         a combined list of all terms.

    EMAIL THREAD FOR PROCESSING:
    {email_body}
    """

    response = get_genai_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': {
                'type': 'ARRAY',
                'items': {
                    'type': 'OBJECT',
                    'properties': {
                        'Quote ID': {'type': 'STRING'},
                        'Partner Name': {'type': 'STRING'},
                        'End Customer': {'type': 'STRING'},
                        'Site A': {'type': 'STRING'},
                        'Site A City': {'type': 'STRING'},
                        'Site B': {'type': 'STRING'},
                        'Site B City': {'type': 'STRING'},
                        'Technology': {'type': 'STRING'},
                        'Service/Product': {'type': 'STRING'},
                        'Capacity / Quantity': {'type': 'STRING'},
                        'NRC': {'type': 'STRING'},
                        'MRC': {'type': 'STRING'},
                        'Contract Terms': {'type': 'STRING'},
                        'Sales Effort By': {'type': 'STRING'},
                        'Comments': {'type': 'STRING'},
                        'POC': {'type': 'STRING'},
                        'Contact Email Address': {'type': 'STRING'},
                        'On-Net/Off-Net': {'type': 'STRING'},
                        'LM Infra Details': {'type': 'STRING'},
                        'Media': {'type': 'STRING'},
                    },
                    'required': [
                        'Quote ID', 'Partner Name', 'Technology', 'Service/Product',
                        'Capacity / Quantity', 'NRC', 'MRC', 'Media'
                    ]
                }
            }
        }
    )
    return json.loads(response.text)


def run_bot():
    mail = None
    try:
        sheet = get_funnel_worksheet()
        existing_data = sheet.get_all_records()
        last_s_no = len(existing_data) + 1

        email_user = env_or_secret("EMAIL_USER")
        email_pass = (env_or_secret("EMAIL_PASS") or "").replace(" ", "")
        if not email_user or not email_pass:
            return "Set EMAIL_USER and EMAIL_PASS in secrets.env or Streamlit Cloud secrets."

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        mail.select("inbox")
        _, messages = mail.search(None, 'UNSEEN')

        new_rows = []
        email_ids = messages[0].split()

        if not email_ids:
            return "No unread items found. Mark a quote email thread as 'Unread' to test."

        for num in email_ids:
            _, data = mail.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            email_from = msg.get("From", "")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode(errors='ignore')
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')

            opp_date, prop_date = extract_thread_dates(body, email_user)
            tat = calculate_tat(opp_date, prop_date)

            circuits = expand_circuits_by_contract_terms(get_ai_extraction(body))

            for c in circuits:
                lm_infra = c.get('LM Infra Details', '-')
                media = normalize_media(c.get('Media'), lm_infra)
                end_customer = c.get('End Customer', '-')
                partner_name = normalize_partner_name(c.get('Partner Name'), email_from)
                new_rows.append([
                    last_s_no, c.get('Quote ID', '-'), format_sheet_date(opp_date),
                    partner_name, end_customer, c.get('Site A', '-'),
                    c.get('Site A City', '-'), c.get('Site B', '-'), c.get('Site B City', '-'),
                    c.get('Technology', '-'), c.get('Service/Product', '-'), c.get('Capacity / Quantity', '-'),
                    format_currency(c.get('NRC')), format_currency(c.get('MRC')), 'Email', format_sheet_date(prop_date),
                    c.get('Contract Terms', '-'), c.get('Sales Effort By', '-'), c.get('Comments', '-'),
                    'OPEN', 'MEDIUM', c.get('POC', '-'), c.get('Contact Email Address', '-'),
                    tat, c.get('On-Net/Off-Net', '-'), lm_infra,
                    'Unprotected', media, '-', 'New Service'
                ])
                last_s_no += 1

        if new_rows:
            sheet.append_rows(new_rows)
            first_row = len(existing_data) + 2
            last_row = first_row + len(new_rows) - 1
            sheet.format(
                f"L{first_row}:M{last_row}",
                {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}},
            )
            try:
                from gspread.utils import ValidationConditionType
                sheet.add_validation(
                    f"AB{first_row}:AB{last_row}",
                    ValidationConditionType.one_of_list,
                    [MEDIA_FIBER, MEDIA_WIRELESS],
                    strict=True,
                    showCustomUi=True,
                )
            except Exception:
                pass
            return f"✅ Success! Processed and added {len(new_rows)} structured rows to the Funnel."

        return "Unread emails processed, but no circuit rows were extracted by Gemini."

    except imaplib.IMAP4.error as e:
        return f"Gmail Login Failed: Make sure your App Password is correct and has no spaces. Error: {e}"
    except Exception as e:
        return f"Operational Error: {str(e)}"
    finally:
        if mail:
            try:
                mail.logout()
            except Exception:
                pass

# Streamlit Setup
LOGO_URL = "https://exponentiaglobal.com/wp-content/uploads/2023/09/1-1.png"
SITE_URL = "https://exponentiaglobal.com/"
INVEXAL_LOGO = "https://invexal.com/wp-content/uploads/2023/07/Invexal-Logo-01-1.png"
GEMINI_LOGO = "https://upload.wikimedia.org/wikipedia/commons/8/8a/Google_Gemini_logo.svg"
GMAIL_LOGO = "https://www.gstatic.com/images/branding/product/2x/gmail_2020q4_48dp.png"
SHEETS_LOGO = "https://www.gstatic.com/images/branding/product/2x/sheets_2020q4_48dp.png"

st.set_page_config(
    page_title="Exponentia Sales Bot",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def inject_custom_css():
    import streamlit.components.v1 as components

    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui.css")
    try:
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
    except OSError:
        return
    # Inject into parent document (Streamlit 1.5x iframes block scoped <style> in markdown)
    components.html(
        f"""
        <script>
        (function() {{
            const doc = window.parent.document;
            let el = doc.getElementById("exp-bot-styles");
            if (!el) {{
                el = doc.createElement("style");
                el.id = "exp-bot-styles";
                doc.head.appendChild(el);
            }}
            el.textContent = {json.dumps(css)};
            let bg = doc.getElementById("exp-bot-bg");
            if (!bg) {{
                bg = doc.createElement("div");
                bg.id = "exp-bot-bg";
                bg.className = "exp-bg-orbs";
                bg.innerHTML = "<span class=\\"orb-a\\"></span><span class=\\"orb-b\\"></span><span class=\\"orb-c\\"></span>";
                doc.body.prepend(bg);
            }}
            let particles = doc.getElementById("exp-bot-particles");
            if (!particles) {{
                particles = doc.createElement("div");
                particles.id = "exp-bot-particles";
                particles.className = "exp-bg-particles";
                doc.body.prepend(particles);
            }}
            if (particles.childElementCount === 0) {{
                const colors = ["#67e8f9", "#38bdf8", "#60a5fa", "#3b82f6", "#22d3ee"];
                for (let i = 0; i < 50; i++) {{
                    const p = doc.createElement("span");
                    p.className = "particle";
                    const size = 2 + Math.random() * 5;
                    const left = Math.random() * 100;
                    const delay = Math.random() * 22;
                    const duration = 14 + Math.random() * 20;
                    const color = colors[i % colors.length];
                    p.style.cssText = [
                        "left:" + left + "%",
                        "width:" + size + "px",
                        "height:" + size + "px",
                        "background:" + color,
                        "color:" + color,
                        "animation-duration:" + duration + "s," + (2 + Math.random() * 3) + "s",
                        "animation-delay:" + delay + "s," + (Math.random() * 2) + "s",
                    ].join(";");
                    particles.appendChild(p);
                }}
            }}
        }})();
        </script>
        """,
        height=0,
    )
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

inject_custom_css()

hero_left, hero_right = st.columns([1.1, 2.2], gap="large")
with hero_left:
    st.image(LOGO_URL, width=160)
with hero_right:
    st.markdown(
        f"""
        <div class="hero-shell">
            <p class="hero-sub hero-kicker">Exponentia Global</p>
            <h1 class="hero-title">Live Sales Funnel Bot</h1>
            <p class="hero-sub">Sync unread quote emails to your funnel sheet with Gemini-powered extraction.</p>
            <div class="powered-by">
                <span class="powered-label">Powered by</span>
                <div class="powered-logos">
                    <img src="{INVEXAL_LOGO}" alt="Invexal" class="partner-logo logo-invexal" title="Invexal" />
                    <img src="{GEMINI_LOGO}" alt="Google Gemini" class="partner-logo logo-gemini" title="Gemini AI" />
                    <img src="{GMAIL_LOGO}" alt="Gmail" class="partner-logo logo-gmail" title="Gmail" />
                    <img src="{SHEETS_LOGO}" alt="Google Sheets" class="partner-logo logo-sheets" title="Google Sheets" />
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<a class="site-link" href="{SITE_URL}" target="_blank">↗ exponentiaglobal.com</a>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="glass-card">
        <p class="card-label">Automation</p>
        <p class="card-heading">Process unread quote threads</p>
        <p class="card-body">Mark a quote email as <strong>Unread</strong> in Gmail, then run sync. The bot extracts circuits, applies your tech/service rules, and appends rows to the live funnel.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

sync_col, format_col, info_col = st.columns([1.2, 1, 1])
with sync_col:
    if st.button("Sync Gmail to Google Sheets"):
        with st.spinner("Analyzing emails with Gemini…"):
            result = run_bot()
            if result and "Success" in result:
                st.success(result)
            else:
                st.error(result or "Unknown error.")
with format_col:
    if st.button("Reformat sheet dates"):
        with st.spinner("Updating existing date cells…"):
            result = reformat_existing_sheet_dates()
            if result and "Updated" in result:
                st.success(result)
            elif result and "already" in result:
                st.info(result)
            else:
                st.warning(result or "No dates updated.")
with info_col:
    st.markdown(
        """
        <div class="glass-card" style="margin-top:0;padding:1.25rem 1.5rem;">
            <p class="card-label">Quick tips</p>
            <p class="card-body" style="margin:0;">
            • Use a Gmail <strong>App Password</strong><br>
            • Share the sheet with your service account<br>
            • Quote IDs like <code>I698-26</code> parse best
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f"""
    <div class="sheet-link-wrap">
        <a href="{SHEET_URL}" target="_blank">Open Live Google Sheet →</a>
    </div>
    """,
    unsafe_allow_html=True,
)
