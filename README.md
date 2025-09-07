# rd_notify
Lightweight Dockerized script to check when your Real-Debrid account expires.

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
### Discord
discord notifications can be added by putting your webhook in the config
