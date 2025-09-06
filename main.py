import os
from configparser import ConfigParser

config_path = os.getenv("RD_NOTIFY_CONF", "/config/rd_notify.conf")
config = ConfigParser()
config.read(config_path)

TOKEN = config.get("real_debrid", "token")
THRESHOLD = config.getint("real_debrid", "days_threshold", fallback=5)

if not TOKEN:
    print("❌ Missing RD_TOKEN env var")
    sys.exit(1)

resp = requests.get(
    "https://api.real-debrid.com/rest/1.0/user",
    headers={"Authorization": f"Bearer {TOKEN}"}
)
resp.raise_for_status()
data = resp.json()

expiry = datetime.datetime.strptime(data["expiration"], "%Y-%m-%dT%H:%M:%S.%fZ")
days_left = (expiry - datetime.datetime.utcnow()).days

if days_left <= THRESHOLD:
    print(f"⚠️ Real-Debrid expires in {days_left} days ({expiry.date()})")
    sys.exit(1)
else:
    print(f"✅ {days_left} days left (expires {expiry.date()})")

