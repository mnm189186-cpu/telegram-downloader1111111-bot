#!/usr/bin/env bash
set -e
# تحميل متغيرات من .env إن وجدت
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
python bot.py
RUN mkdir -p /app/downloads && chown -R 1000:1000 /app/downloads

ENV PYTHONUNBUFFERED=1

CMD ["./run.sh"]
