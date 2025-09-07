# rd_notify
Lightweight Dockerized script to check when your Real-Debrid account expires. Sends to console and to Discord if configured. Notifications happen on startup and daily.

## How to Run
### Docker
```bash
docker run --rm \
  -e RD_TOKEN="your_real_debrid_token" \
  -e DAYS_THRESHOLD=5 \
  ghcr.io/waf1102/rd_notify:latest
```

### Compose
```bash
mkdir rd_notify && cd rd_notify
curl -O https://raw.githubusercontent.com/waf1102/rd_notify/refs/heads/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/waf1102/rd_notify/refs/heads/main/rd_notify.conf

# add your real-debrid api key to rd_notify.conf
# Change other settings as needed

docker compose up
```

## Optional Settings
### Main
Threshold is the number of days before expiration. Use this for settings notifications.

### Discord
Discord notifications can be added by putting your webhook in the config.

### Schedule
Default notification time is the same as expiration time. This can be changed in the config.
