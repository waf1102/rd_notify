import requests
import datetime
import sys
import time
from configparser import ConfigParser

config_path = "/config/rd_notify.conf"
config = ConfigParser()
config.read(config_path)

# --- Config values ---
TOKEN = config.get("real_debrid", "token", fallback=None)
THRESHOLD = config.getint("real_debrid", "days_threshold", fallback=5)

WEBHOOK_URL = config.get("discord", "webhook_url", fallback=None)
DISCORD_PREFIX = config.get("discord", "prefix", fallback="RD Notify")

# --- Helpers ---
def send_discord_message(content: str):
    if not WEBHOOK_URL:
        return
    payload = {"content": f"**{DISCORD_PREFIX}:** {content}"}
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to send Discord message: {e}")

def check_expiry():
    if not TOKEN:
        print("❌ Missing Real-Debrid API token in config")
        sys.exit(1)

    resp = requests.get(
        "https://api.real-debrid.com/rest/1.0/user",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
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

    print(msg)
    send_discord_message(msg)

    return expiry


# --- Main loop ---
if __name__ == "__main__":
    expiry = check_expiry()

    while True:
        now = datetime.datetime.now(datetime.UTC)
        target = expiry.replace(year=now.year, month=now.month, day=now.day)

        if target < now:
            target = target + datetime.timedelta(days=1)

        sleep_seconds = (target - now).total_seconds()
        print(f"⏳ Sleeping until next check at {target} "
              f"({int(sleep_seconds/3600)}h {int((sleep_seconds%3600)/60)}m)")

        time.sleep(sleep_seconds)

        expiry = check_expiry()

