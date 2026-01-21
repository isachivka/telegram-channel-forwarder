FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

COPY script.py /app/script.py
COPY docker/crontab /etc/cron.d/telegram-forwarder
COPY docker/entrypoint.sh /entrypoint.sh

RUN chmod 0644 /etc/cron.d/telegram-forwarder \
    && chmod +x /entrypoint.sh

RUN pip install --no-cache-dir telethon

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/entrypoint.sh"]
