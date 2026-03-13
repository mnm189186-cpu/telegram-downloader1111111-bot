# استخدم Ubuntu 22.04 كأساس
FROM ubuntu:22.04

# تحديث الحزم وتثبيت ffmpeg و Python و pip
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        python3 \
        python3-pip \
        git \
        curl \
        unzip \
        && rm -rf /var/lib/apt/lists/*

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات البوت
COPY bot.py .
COPY requirements.txt .
COPY run.sh .

# تثبيت متطلبات بايثون
RUN pip3 install --no-cache-dir -r requirements.txt

# إنشاء مجلد التنزيلات
RUN mkdir -p /app/downloads

# السماح بتنفيذ run.sh
RUN chmod +x run.sh

# جعل Python يطبع مباشرة (للتصحيح)
ENV PYTHONUNBUFFERED=1

# تشغيل البوت عند تشغيل الحاوية
CMD ["./run.sh"]
