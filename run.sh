#!/usr/bin/env bash
set -e
# تحميل متغيرات من .env إن وجدت
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
python bot.py
