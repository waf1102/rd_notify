import requests
import datetime
import sys
import time
import zoneinfo
from configparser import ConfigParser

config_path = "/config/rd_notify.conf"
config = ConfigParser()
config.read(config_path)

# --- Config values ---
TOKEN = config.get("real_debrid", "token", fallback=None)
THRESHOLD = config.getint("real_debrid", "days_threshold", fallback=5)

WEBHOOK_URL = config.get("discord", "webhook_url", fallback=None)
DISCORD_PREFIX = config.get("discord", "prefix", fallback="RD Notify")

DAILY_TIME = config.get("schedule", "daily_time", fallback="").strip()
TIMEZONE = config.get("schedule", "timezone", fallback="UTC")

# --- Helpers ---
def send_discord_message(content: str):
    if not WEBHOOK_URL:
        return
    payload = {"content": f"**{DISCORD_PREFIX}:** {content}"}
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to send Discord message: {e}", flush=True)

def check_expiry():
    if not TOKEN:
        print("❌ Missing Real-Debrid API token in config", flush=True)
        sys.exit(1)

    try:
        resp = requests.get(
            "https://api.real-debrid.com/rest/1.0/user",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
    except requests.RequestException as e:
        print(f"❌ Failed to reach Real-Debrid: {e}", flush=True)
        send_discord_message(f"❌ Failed to reach Real-Debrid: {e}")
        sys.exit(1)

    if resp.status_code == 401:
        msg = "❌ Real-Debrid token is invalid or expired (401)"
        print(msg, flush=True)
        send_discord_message(msg)
        sys.exit(1)

    if resp.status_code == 403:
        msg = "❌ Real-Debrid account locked or permission denied (403)"
        print(msg, flush=True)
        send_discord_message(msg)
        sys.exit(1)

    resp.raise_for_status()
    data = resp.json()

    expiry = datetime.datetime.strptime(
        data["expiration"], "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=datetime.UTC)

    now = datetime.datetime.now(datetime.UTC)
    days_left = (expiry - now).days

    if days_left <= THRESHOLD:
        msg = f"⚠️ Real-Debrid expires in {days_left} days ({expiry.date()})"
    else:
        msg = f"✅ {days_left} days left (expires {expiry.date()})"

    print(msg, flush=True)
    send_discord_message(msg)

    return expiry


def get_next_run(expiry: datetime.datetime):
    """Decide when the next daily check should run."""
    now = datetime.datetime.now(datetime.UTC)

    if DAILY_TIME:
        # User wants a fixed time in their timezone
        try:
            tz = zoneinfo.ZoneInfo(TIMEZONE)
        except Exception:
            print(f"⚠️ Invalid timezone '{TIMEZONE}', defaulting to UTC", flush=True)
            tz = datetime.UTC

        # Parse HH:MM
        hour, minute = map(int, DAILY_TIME.split(":"))
        target_local = datetime.datetime.now(tz).replace(hour=hour, minute=minute,
                                                         second=0, microsecond=0)
        if target_local < datetime.datetime.now(tz):
            target_local += datetime.timedelta(days=1)

        # Convert to UTC
        target_utc = target_local.astimezone(datetime.UTC)
        return target_utc

    else:
        # Default: align with RD expiry time
        target = expiry.replace(year=now.year, month=now.month, day=now.day)
        if target < now:
            target += datetime.timedelta(days=1)
        return target

# --- Main loop ---
if __name__ == "__main__":
    expiry = check_expiry()

    while True:
        next_run = get_next_run(expiry)
        now = datetime.datetime.now(datetime.UTC)
        sleep_seconds = (next_run - now).total_seconds()

        print(f"⏳ Sleeping until next check at {next_run} UTC "
              f"({int(sleep_seconds/3600)}h {int((sleep_seconds%3600)/60)}m)", flush=True)

        time.sleep(sleep_seconds)
        expiry = check_expiry()

