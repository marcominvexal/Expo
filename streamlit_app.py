import os
import imaplib
import email
from email.utils import parseaddr
import json
import re
import time
import gspread
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google import genai
from google.oauth2.service_account import Credentials

from ui_retry_animations import SYNC_SUCCESS_CHARACTER_HTML, gemini_retry_wait_html

# Local secrets (Streamlit Cloud uses st.secrets instead)
load_dotenv("secrets.env", override=True)
load_dotenv(override=True)

SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
SPREADSHEET_ID = "1E9gYdeZUwMEmnwe164io7E47QuXnBfYcELdulUroN_4"
WORKSHEET_GID = 0
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


def _coerce_mapping(raw):
    """Convert Streamlit SecretDict / dict / JSON string to a plain dict."""
    if raw is None:
        return None
    if isinstance(raw, str):
        return json.loads(raw.strip())
    if hasattr(raw, "to_dict"):
        return raw.to_dict()
    try:
        return dict(raw)
    except (TypeError, ValueError):
        return {k: raw[k] for k in raw}


def _normalize_service_account_info(info):
    """Fix private_key newlines for Streamlit Cloud TOML secrets."""
    data = _coerce_mapping(info)
    if not data:
        return None
    pk = data.get("private_key")
    if isinstance(pk, str) and "\\n" in pk:
        data["private_key"] = pk.replace("\\n", "\n")
    return data


def _credentials_from_service_account_info(info):
    data = _normalize_service_account_info(info)
    if not data:
        return None
    if not data.get("client_email") or not data.get("private_key"):
        return None
    return Credentials.from_service_account_info(data, scopes=SCOPE)


def _streamlit_secret_top_level_keys():
    try:
        return list(st.secrets.keys())
    except Exception:
        return []


def _get_streamlit_secret_section(section_name):
    """Read a TOML section from st.secrets (Cloud UI or local secrets.toml)."""
    try:
        return st.secrets[section_name]
    except Exception:
        pass
    try:
        return getattr(st.secrets, section_name)
    except Exception:
        pass
    return None


def _service_account_from_streamlit_env(prefix="GCP_SERVICE_ACCOUNT"):
    """
    Streamlit Cloud also exposes nested secrets as env vars, e.g.
    GCP_SERVICE_ACCOUNT_CLIENT_EMAIL, GCP_SERVICE_ACCOUNT_PRIVATE_KEY.
    """
    field_map = {
        "TYPE": "type",
        "PROJECT_ID": "project_id",
        "PRIVATE_KEY_ID": "private_key_id",
        "PRIVATE_KEY": "private_key",
        "CLIENT_EMAIL": "client_email",
        "CLIENT_ID": "client_id",
        "AUTH_URI": "auth_uri",
        "TOKEN_URI": "token_uri",
        "AUTH_PROVIDER_X509_CERT_URL": "auth_provider_x509_cert_url",
        "CLIENT_X509_CERT_URL": "client_x509_cert_url",
        "UNIVERSE_DOMAIN": "universe_domain",
    }
    data = {}
    head = f"{prefix}_"
    for env_key, env_val in os.environ.items():
        if not env_key.startswith(head):
            continue
        suffix = env_key[len(head) :]
        field = field_map.get(suffix)
        if field:
            data[field] = env_val
    if data.get("client_email") and data.get("private_key"):
        return data
    return None


def _service_account_from_local_toml():
    """Fallback: read .streamlit/secrets.toml when running locally."""
    import tomllib

    toml_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        ".streamlit",
        "secrets.toml",
    )
    if not os.path.isfile(toml_path):
        return None
    with open(toml_path, "rb") as handle:
        parsed = tomllib.load(handle)
    for section in ("gcp_service_account", "google_service_account", "service_account"):
        if section in parsed:
            return parsed[section]
    return None


def load_google_credentials():
    """
    Load Google Sheets credentials (local file or Streamlit Cloud secrets).
    Streamlit Cloud: paste full TOML in App settings → Secrets, then Reboot app.
    """
    load_errors = []

    for section in (
        "gcp_service_account",
        "google_service_account",
        "service_account",
        "gcp",
    ):
        try:
            block = _get_streamlit_secret_section(section)
            if block is None:
                continue
            creds = _credentials_from_service_account_info(block)
            if creds:
                return creds
            load_errors.append(f"[{section}] missing client_email or private_key")
        except Exception as exc:
            load_errors.append(f"[{section}] {exc}")

    for key in (
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        "GCP_SERVICE_ACCOUNT_JSON",
        "SERVICE_ACCOUNT_JSON",
    ):
        try:
            raw = env_or_secret(key)
            if not raw:
                continue
            creds = _credentials_from_service_account_info(raw)
            if creds:
                return creds
        except Exception as exc:
            load_errors.append(f"{key}: {exc}")

    try:
        env_block = _service_account_from_streamlit_env()
        if env_block:
            creds = _credentials_from_service_account_info(env_block)
            if creds:
                return creds
    except Exception as exc:
        load_errors.append(f"GCP_SERVICE_ACCOUNT_* env: {exc}")

    try:
        local_block = _service_account_from_local_toml()
        if local_block:
            creds = _credentials_from_service_account_info(local_block)
            if creds:
                return creds
    except Exception as exc:
        load_errors.append(f".streamlit/secrets.toml: {exc}")

    if os.path.isfile("service_account.json"):
        try:
            return Credentials.from_service_account_file(
                "service_account.json", scopes=SCOPE
            )
        except Exception as exc:
            load_errors.append(f"service_account.json: {exc}")

    found_keys = _streamlit_secret_top_level_keys()
    keys_hint = ", ".join(found_keys) if found_keys else "(none — secrets empty or not saved)"
    hint = (
        "Streamlit Cloud → App settings → Secrets: paste the ENTIRE file "
        "`.streamlit/secrets.toml` (must include [gcp_service_account] header). "
        "Save → Reboot app. Share sheet with client_email."
    )
    detail = "; ".join(load_errors) if load_errors else f"st.secrets keys: {keys_hint}"
    raise FileNotFoundError(f"Google credentials missing. {hint} Details: {detail}")


def google_credentials_configured():
    try:
        load_google_credentials()
        return True, None
    except Exception as exc:
        return False, str(exc)


@st.cache_resource
def get_gspread_client():
    return gspread.authorize(load_google_credentials())


@st.cache_resource
def get_genai_client():
    key = env_or_secret("GEMINI_API_KEY")
    if not key:
        raise ValueError("Set GEMINI_API_KEY in secrets.env or Streamlit secrets.")
    return genai.Client(api_key=key)


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
# 31-column funnel layout (1-based letters for sheet formatting)
FUNNEL_COL_LM_INFRA = "Z"  # LM Infra details: Fiber or Wireless
HOLIDAYS_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "holidays.json")

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
DEFAULT_END_CUSTOMER = "Unknown"
DEFAULT_ON_NET = "On-Net"
DEFAULT_OFFERED_US = "New Service"
PROTECTION_STATUSES = ("Protected", "Unprotected", "N/A")
XC_STATUSES = ("Included", "Excluded", "N/A")

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


def load_public_holidays():
    """Load YYYY-MM-DD public holiday dates from holidays.json (extend when list is provided)."""
    holidays = set()
    if not os.path.isfile(HOLIDAYS_JSON_PATH):
        return holidays
    try:
        with open(HOLIDAYS_JSON_PATH, encoding="utf-8") as handle:
            data = json.load(handle)
        raw_dates = data.get("dates", data if isinstance(data, list) else [])
        for item in raw_dates:
            text = str(item).strip()
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
                holidays.add(text)
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return holidays


def normalize_lm_infra(value, fallback_text=None):
    """LM Infra details column: Fiber or Wireless only (not terms/conditions)."""
    combined = " ".join(str(part or "") for part in (value, fallback_text)).lower()

    wireless_hints = (
        "wireless", "radio", "microwave", "wifi", "wi-fi", "lte", "5g", "4g",
        "fixed wireless", "airfiber",
    )
    fiber_hints = (
        "fiber", "fibre", "ftth", "fttx", "fttp", "dark fiber", "pon", "gpon",
    )
    terms_hints = (
        "terms", "condition", "contract", "liability", "warranty", "sla",
        "payment", "validity", "quote valid",
    )
    if any(h in combined for h in terms_hints) and not any(
        h in combined for h in wireless_hints + fiber_hints
    ):
        return MEDIA_FIBER

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


def normalize_end_customer(value):
    text = (value or "").strip()
    if not text or text == "-":
        return DEFAULT_END_CUSTOMER
    return text


def normalize_on_net_status(value):
    text = (value or "").strip()
    if not text or text == "-":
        return DEFAULT_ON_NET
    compact = re.sub(r"[^a-z0-9]", "", text.lower())
    if "offnet" in compact or compact == "off":
        return "Off-Net"
    if "onnet" in compact or compact == "on":
        return DEFAULT_ON_NET
    return text


def normalize_contract_term(value):
    """Contract term is always expressed in months (e.g. '12 Months')."""
    text = (value or "").strip()
    if not text or text == "-":
        return "-"
    if re.search(r"month", text, re.IGNORECASE):
        match = re.search(r"(\d+)", text)
        if match:
            return f"{match.group(1)} Months"
        return text
    match = re.search(r"(\d+)", text)
    if match:
        return f"{match.group(1)} Months"
    return f"{text} Months"


def normalize_protection_status(value, default="N/A"):
    text = str(value or "").strip()
    if not text or text == "-":
        return default
    lower = text.lower()
    if lower in ("n/a", "na", "not applicable"):
        return "N/A"
    if "unprotect" in lower or lower in ("no", "n", "unprotected"):
        return "Unprotected"
    if "protect" in lower or lower in ("yes", "y", "protected"):
        return "Protected"
    return default


def normalize_xc_status(value, default="N/A"):
    text = str(value or "").strip()
    if not text or text == "-":
        return default
    lower = text.lower()
    if lower in ("n/a", "na", "not applicable"):
        return "N/A"
    if "exclud" in lower:
        return "Excluded"
    if "includ" in lower:
        return "Included"
    return default


def normalize_offered_us(value):
    text = (value or "").strip()
    return text if text and text != "-" else DEFAULT_OFFERED_US


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


def count_holidays_in_range(start_date, end_date, holidays):
    """Count public holidays that fall within [start_date, end_date] (inclusive)."""
    if not holidays:
        return 0
    current = start_date
    count = 0
    while current <= end_date:
        if current.strftime("%Y-%m-%d") in holidays:
            count += 1
        current += timedelta(days=1)
    return count


def calculate_working_days_exclusive(start_date, end_date, holidays=None):
    """Business days (Mon–Fri) between dates, excluding public holidays, minus 1 exclusive day."""
    if start_date >= end_date:
        return 0

    holiday_set = holidays if holidays is not None else load_public_holidays()
    current = start_date
    working_days = 0
    while current <= end_date:
        if current.weekday() < 5 and current.strftime("%Y-%m-%d") not in holiday_set:
            working_days += 1
        current += timedelta(days=1)

    return max(0, working_days - 1)


def format_ai_sheet_dates(opp_str, prop_str, holidays=None):
    """Parse Gemini YYYY-MM-DD dates; return sheet dates, holiday-aware TAT, and holiday count."""
    tat = 0
    holiday_count = 0
    now_fmt = datetime.now().strftime(SHEET_DATE_FORMAT)
    holiday_set = holidays if holidays is not None else load_public_holidays()
    try:
        opp_date = datetime.strptime((opp_str or "").strip(), "%Y-%m-%d")
        prop_date = datetime.strptime((prop_str or "").strip(), "%Y-%m-%d")
        tat = calculate_working_days_exclusive(opp_date, prop_date, holiday_set)
        holiday_count = count_holidays_in_range(opp_date, prop_date, holiday_set)
        return (
            opp_date.strftime(SHEET_DATE_FORMAT),
            prop_date.strftime(SHEET_DATE_FORMAT),
            tat,
            holiday_count,
        )
    except ValueError:
        opp_fmt = format_sheet_date(opp_str) if opp_str else now_fmt
        prop_fmt = format_sheet_date(prop_str) if prop_str else now_fmt
        return opp_fmt, prop_fmt, tat, holiday_count


GEMINI_CIRCUITS_SCHEMA = {
    'type': 'OBJECT',
    'properties': {
        'circuits': {
            'type': 'ARRAY',
            'items': {
                'type': 'OBJECT',
                'properties': {
                    'Quote ID': {'type': 'STRING'},
                    'Opportunity Date': {'type': 'STRING'},
                    'Proposal Date': {'type': 'STRING'},
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
                    'Last Mile Protection': {'type': 'STRING'},
                    'Wet Segment Protection': {'type': 'STRING'},
                    'XC Included/Excluded': {'type': 'STRING'},
                    'Offered Us': {'type': 'STRING'},
                },
                'required': [
                    'Quote ID', 'Opportunity Date', 'Proposal Date', 'Partner Name',
                    'Technology', 'Service/Product', 'Capacity / Quantity', 'NRC', 'MRC',
                    'LM Infra Details',
                ],
            },
        },
    },
    'required': ['circuits'],
}


def _is_retryable_gemini_error(exc):
    error_str = str(exc).upper()
    return any(token in error_str for token in ("503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED"))


def get_ai_extraction(email_body, email_user):
    """Extract data with a 60s retry loop and animated wait UI on 503/429."""
    prompt = f"""
    You are an expert telecom data verification engine. Analyze the email thread and extract quoting matrix rows into clean structured objects.

    CRITICAL ALIGNMENT & TAXONOMY RULES:
    1. Quote ID: Extract tracking identifier format matching expressions like 'I698-26' or 'F780-23'. Do NOT extract subject titles.

    2. Opportunity Date (HYPER-MINIMAL TAT LOGIC):
       - OBJECTIVE: Calculate the absolute lowest logically defensible Turnaround Time (TAT) for our sales engineering execution.
       - RULE A (Scope Isolation): Look at the exact circuits listed in the final pricing table. If the email thread began days or weeks earlier discussing a completely different country, city, or independent RFQ scope, you MUST completely ignore those older dates.
       - RULE B (The Actionable Milestone Pivot): Do NOT default to the initial incoming email if our team was operationally blocked. If our team replied asking for missing prerequisites (like LPOC details, specific customer names, or explicit capacities) to proceed, the clock does NOT start at the beginning. Instead, set the 'Opportunity Date' to the exact date when the requirement became actively scoped, or when the customer provided the final clarity needed to process the engineering feasibility.
       - RULE C (Eliminate Trailing Idle Days): Ensure no dead time spent waiting on customer definition parameters is unfairly charged against our turnaround performance metric.
       - Format strictly as YYYY-MM-DD.

    3. Proposal Date: Contextually find the date/timestamp when our team ({email_user}) sent the final completed pricing/proposal response. If no pricing has been sent yet, fallback to the opportunity date. Format strictly as YYYY-MM-DD.

    4. Capacity / Quantity: State the metric unit explicitly (e.g., '50 Mbps', '20 Gbps').
    5. Currency Formatting: Ensure NRC and MRC fields include the '$' symbol and correct commas (e.g., '$1,500.00'). If none, write '-'.
    6. Strict Tech/Service Taxonomy Mapping:
       - If Service is DIA or BIA -> Technology MUST be 'Internet'
       - If Service is L2VPN or MPLS -> Technology MUST be 'Ethernet'
       - If Service is IPLC, IEPL, EoSDH, DPLC, or DEPL -> Technology MUST be 'TDM'
       - If Service is Colocation + PWR -> Technology MUST be 'Datacenter'
       - If Service is Cross Connects, Equipment, or Field Support -> Technology MUST be 'Managed Services / Hardware'
    7. End Customer: The final client organization the partner is quoting for (e.g., 'Baker Hughes'). If not mentioned anywhere, use 'Unknown'.
    8. On-Net/Off-Net: If the email does not explicitly state off-net, use 'On-Net'.
    9. Contract Terms: ALWAYS express duration in months with the word 'Months' (e.g., '12 Months', '24 Months', '36 Months'). Never use years-only labels.
       - If a single table row lists multiple contract terms (e.g. columns for 12, 24, and 36 months), output a SEPARATE object for EACH term.
    10. LM Infra Details (column after On-Net/Off-Net): MUST be exactly 'Fiber' or 'Wireless' — the last-mile physical media type. NEVER put terms & conditions, contract text, SLAs, or unrelated notes here.
    11. Last Mile Protection: MUST be exactly one of 'Protected', 'Unprotected', or 'N/A'.
    12. Wet Segment Protection: MUST be exactly one of 'Protected', 'Unprotected', or 'N/A'. This is protection status only — NOT fiber/wireless media.
    13. XC Included/Excluded: Cross-connect status — exactly one of 'Included', 'Excluded', or 'N/A'.
    14. Offered Us: What we offered (e.g., 'New Service', 'Renewal', 'Upgrade'). Default to 'New Service' if unclear.
    15. Partner Name vs End Customer:
       - Partner Name: The external entity emailing Exponentia Global to request a quote (e.g., 'Noor Data Network'). NEVER set this to 'Exponentia Global'.

    EMAIL THREAD FOR PROCESSING:
    {email_body}
    """

    start_overall_time = time.time()
    attempt_count = 0
    anim_placeholder = st.empty()
    retry_limit_seconds = 60

    while (time.time() - start_overall_time) < retry_limit_seconds:
        try:
            response = get_genai_client().models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': GEMINI_CIRCUITS_SCHEMA,
                },
            )
            anim_placeholder.empty()
            return json.loads(response.text)
        except Exception as exc:
            if not _is_retryable_gemini_error(exc):
                anim_placeholder.empty()
                raise

            time_elapsed = time.time() - start_overall_time
            time_remaining_total = max(0, int(retry_limit_seconds - time_elapsed))
            if time_remaining_total <= 0:
                anim_placeholder.empty()
                raise exc

            sleep_interval = min(5 + (attempt_count * 2), time_remaining_total)
            attempt_count += 1

            for remaining_seconds in range(int(sleep_interval), 0, -1):
                current_total_left = max(0, int(retry_limit_seconds - (time.time() - start_overall_time)))
                anim_placeholder.markdown(
                    gemini_retry_wait_html(remaining_seconds, current_total_left),
                    unsafe_allow_html=True,
                )
                time.sleep(1)

    anim_placeholder.empty()
    raise TimeoutError(
        "Gemini Engine overloaded. System timed out automatically after retrying for 1 minute."
    )


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
        email_ids = messages[0].split()

        if not email_ids:
            return "No new (unread) emails found. Mark a quote email as 'Unread' to test."

        new_rows = []
        public_holidays = load_public_holidays()

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

            ai_data = get_ai_extraction(body, email_user)
            circuits = ai_data.get('circuits', [])
            if isinstance(circuits, dict):
                circuits = [circuits]

            for c in circuits:
                opp_formatted, prop_formatted, tat, holiday_count = format_ai_sheet_dates(
                    c.get('Opportunity Date', ''),
                    c.get('Proposal Date', ''),
                    public_holidays,
                )
                lm_infra = normalize_lm_infra(
                    c.get('LM Infra Details'),
                    c.get('Comments'),
                )
                partner_name = normalize_partner_name(c.get('Partner Name'), email_from)
                end_customer = normalize_end_customer(c.get('End Customer'))
                on_net = normalize_on_net_status(c.get('On-Net/Off-Net'))
                contract_term = normalize_contract_term(c.get('Contract Terms'))
                last_mile_protection = normalize_protection_status(
                    c.get('Last Mile Protection'),
                    default='Unprotected',
                )
                wet_segment_protection = normalize_protection_status(
                    c.get('Wet Segment Protection'),
                    default='N/A',
                )
                xc_status = normalize_xc_status(c.get('XC Included/Excluded'))
                offered_us = normalize_offered_us(c.get('Offered Us'))

                new_rows.append([
                    last_s_no,                                          # 1. S.NO
                    c.get('Quote ID', '-'),                             # 2. Quote ID
                    opp_formatted,                                      # 3. Opportunity date
                    partner_name,                                       # 4. Partner name
                    end_customer,                                       # 5. End customer
                    c.get('Site A', '-'),                               # 6. Site A
                    c.get('Site A City', '-'),                          # 7. Site A City
                    c.get('Site B', '-'),                               # 8. Site B
                    c.get('Site B City', '-'),                          # 9. Site B city
                    c.get('Technology', '-'),                           # 10. Technology
                    c.get('Service/Product', '-'),                      # 11. Service/Products
                    c.get('Capacity / Quantity', '-'),                  # 12. Capacity/Quantity
                    format_currency(c.get('NRC')),                      # 13. NRC
                    format_currency(c.get('MRC')),                       # 14. MRC
                    'Email',                                            # 15. Mode of Communication
                    prop_formatted,                                     # 16. Proposal Date
                    contract_term,                                      # 17. Contract Term (Months)
                    c.get('Sales Effort By', '-'),                      # 18. Sales Effort by
                    c.get('Comments', '-'),                             # 19. Comments
                    'OPEN',                                             # 20. Status
                    'MEDIUM',                                           # 21. Sub-status
                    c.get('POC', '-'),                                  # 22. POC
                    c.get('Contact Email Address', '-'),                # 23. Contact Email Address
                    tat,                                                # 24. TAT
                    on_net,                                             # 25. On-Net/Off-Net
                    lm_infra,                                           # 26. LM Infra details (Fiber/Wireless)
                    last_mile_protection,                               # 27. Last mile protection
                    wet_segment_protection,                             # 28. Wet Segment protection status
                    xc_status,                                          # 29. XC included/excluded
                    holiday_count,                                      # 30. Holidays
                    offered_us,                                         # 31. Offered us
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
                    f"{FUNNEL_COL_LM_INFRA}{first_row}:{FUNNEL_COL_LM_INFRA}{last_row}",
                    ValidationConditionType.one_of_list,
                    [MEDIA_FIBER, MEDIA_WIRELESS],
                    strict=True,
                    showCustomUi=True,
                )
            except Exception:
                pass
            return f"✅ Success! Added {len(new_rows)} perfectly structured rows to the Google Sheet!"

        return "Unread emails processed, but no valid data structures were detected by Gemini."

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
GITHUB_REPO_URL = "https://github.com/marcominvexal/Expo"
STREAMLIT_DEPLOY_URL = (
    "https://share.streamlit.io/deploy?repository=marcominvexal/Expo"
    "&branch=main&mainModule=streamlit_app.py"
)

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

creds_ok, creds_error = google_credentials_configured()
if not creds_ok:
    st.error(creds_error)
    found_keys = _streamlit_secret_top_level_keys()
    st.warning(
        f"Secrets detected in app: **{', '.join(found_keys) if found_keys else 'none'}**. "
        "You must include the **`[gcp_service_account]`** section (not only GEMINI/EMAIL)."
    )
    with st.expander("Copy this into Streamlit Cloud → Settings → Secrets, then Reboot"):
        base = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".streamlit")
        for name in ("secrets.toml", "secrets.toml.example"):
            path = os.path.join(base, name)
            try:
                with open(path, encoding="utf-8") as handle:
                    st.caption(f"From `{name}`:")
                    st.code(handle.read(), language="toml")
                    break
            except OSError:
                continue
        else:
            st.markdown(
                "Paste GEMINI_API_KEY, EMAIL_USER, EMAIL_PASS, and a full "
                "`[gcp_service_account]` block from `service_account.json`."
            )
        st.markdown(
            "**Checklist:** `[gcp_service_account]` header on its own line · "
            "multiline `private_key` in triple quotes · **Save** · **Reboot app** · "
            "share sheet with `marcom@exponentia-project.iam.gserviceaccount.com`"
        )
    st.stop()

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
                st.balloons()
                components.html(SYNC_SUCCESS_CHARACTER_HTML, height=270)
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

st.markdown(
    f"""
    <div class="glass-card deploy-card">
        <p class="card-label">Publish the app</p>
        <p class="card-heading">Deploy in this order</p>
        <ol class="deploy-steps">
            <li><strong>Push to GitHub first</strong> — commit the full project (code only) to
                <a href="{GITHUB_REPO_URL}" target="_blank">github.com/marcominvexal/Expo</a>.
                Never commit <code>secrets.env</code>, <code>.env</code>, or <code>service_account.json</code>.</li>
            <li><strong>Deploy on Streamlit Cloud</strong> — connect the same repo, branch <code>main</code>,
                main file <code>streamlit_app.py</code>.</li>
            <li><strong>Add Streamlit Secrets</strong> — paste TOML from <code>.streamlit/secrets.toml.example</code>
                (Gemini, Gmail, <code>[gcp_service_account]</code>). Share the Google Sheet with the service account email.</li>
            <li><strong>Open your live URL</strong> — e.g. <code>https://exponentiabot-xxxxx.streamlit.app</code>
                (Streamlit redeploys automatically on each GitHub push).</li>
        </ol>
        <p class="card-body deploy-note">Vercel only hosts a static info page — the dashboard runs on Streamlit Cloud or locally at <code>localhost:8501</code>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

deploy_col1, deploy_col2 = st.columns(2)
with deploy_col1:
    st.link_button("Open GitHub repo", GITHUB_REPO_URL, use_container_width=True)
with deploy_col2:
    st.link_button("Deploy on Streamlit Cloud", STREAMLIT_DEPLOY_URL, use_container_width=True)
