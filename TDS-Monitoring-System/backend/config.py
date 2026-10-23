# =============================================================
#  config.py — Central Configuration for TDS Monitoring System
#
#  All tunable parameters live here.
#  Import this file in other modules to avoid hardcoding values.
# =============================================================

import os
from dotenv import load_dotenv

# Load .env file if it exists (for development overrides)
load_dotenv()

# -------------------------------------------------------
#  MQTT Broker Settings
# -------------------------------------------------------
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")   # Mosquitto broker host
MQTT_PORT   = int(os.getenv("MQTT_PORT", 1883))        # Default MQTT port
MQTT_TOPIC  = os.getenv("MQTT_TOPIC", "water/tds/data") # Topic to subscribe to

# -------------------------------------------------------
#  Database
# -------------------------------------------------------
from urllib.parse import urlparse, quote

# ── Option 1: Supabase PostgreSQL (Cloud) ──────────────
# Set SUPABASE_DB_URL in .env to connect to Supabase.
# Format: postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres
_raw_supabase_url = os.getenv("SUPABASE_DB_URL", "").strip()

# ── Option 2: Local SQLite (Fallback) ─────────────────
# Used only when SUPABASE_DB_URL is not provided.
DB_PATH = os.getenv("DB_PATH", "../database/tds_data.db")

def _build_safe_db_url(raw_url: str) -> str:
    """
    Safely rebuild the DB URL so that special characters in the password
    (like @, #, %) are properly percent-encoded before being passed to
    the SQLAlchemy engine.
    Forces psycopg2 dialect to avoid psycopg v3 compatibility issues.
    """
    from urllib.parse import unquote
    parsed = urlparse(raw_url)
    # unquote first (handles %40 → @), then re-encode cleanly (@ → %40)
    # This avoids double-encoding (%40 → %2540)
    raw_password = unquote(parsed.password or "")
    raw_username = unquote(parsed.username or "")
    safe_password = quote(raw_password, safe="")
    safe_username = quote(raw_username, safe="")
    # Force psycopg2 dialect explicitly
    rebuilt = (
        f"postgresql+psycopg2://{safe_username}:{safe_password}"
        f"@{parsed.hostname}:{parsed.port}{parsed.path}"
    )
    return rebuilt

# Final DB URL: Supabase takes priority over SQLite
if _raw_supabase_url:
    DB_URL = _build_safe_db_url(_raw_supabase_url)
    print("[CONFIG] Using Supabase PostgreSQL database")
else:
    DB_URL = f"sqlite:///{DB_PATH}"
    print("[CONFIG] Using local SQLite database")

# -------------------------------------------------------
#  TDS Threshold Limits (ppm)
#  These match WHO / BIS IS 10500:2012 guidelines
# -------------------------------------------------------
TDS_EXCELLENT_LIMIT = int(os.getenv("TDS_EXCELLENT_LIMIT", 300))  # ≤300 → Excellent
TDS_SAFE_LIMIT      = int(os.getenv("TDS_SAFE_LIMIT", 500))       # ≤500 → Safe
TDS_WARNING_LIMIT   = int(os.getenv("TDS_WARNING_LIMIT", 900))    # ≤900 → Warning
                                                                    # >900 → Unsafe

# -------------------------------------------------------
#  Flask Server
# -------------------------------------------------------
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))       # Port for Flask app
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"

# -------------------------------------------------------
#  Alert Logging
# -------------------------------------------------------
ALERT_LOG_FILE = "alerts.log"  # File where unsafe readings are logged

# -------------------------------------------------------
#  Email Alerts (Optional — configure SMTP to enable)
# -------------------------------------------------------
ENABLE_EMAIL_ALERTS  = False                          # Set True to enable
SMTP_HOST            = "smtp.gmail.com"
SMTP_PORT            = 587
SMTP_USER            = "your_email@gmail.com"
SMTP_PASSWORD        = "your_app_password"
ALERT_EMAIL_RECEIVER = "recipient@example.com"
