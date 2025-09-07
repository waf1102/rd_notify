FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

# Set default path for the config
ENV RD_NOTIFY_CONF=/config/rd_notify.conf
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]

