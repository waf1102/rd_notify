# rd_notify
Lightweight Dockerized script to check when your Real-Debrid account expires.

## Docker Run
```bash
docker run --rm \
  -e RD_TOKEN="your_real_debrid_token" \
  -e DAYS_THRESHOLD=5 \
  ghcr.io/waf1102/rd_notify:latest
```
