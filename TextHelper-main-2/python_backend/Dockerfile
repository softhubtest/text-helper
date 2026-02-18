# Python 3.9 slim image
FROM python:3.9-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (gcc vb. gerekebilir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Model indirme (Build sirasinda indirilsin ki image icinde hazir olsun)
COPY download_model.py .
RUN python download_model.py

# Uygulama kodunu kopyala
# python_backend dizini içindeyiz, tüm içeriği /app içine atıyoruz
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8080

# Port
EXPOSE 8080

# Başlatma komutu
# app/main.py üzerinden çalıştırıyoruz
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
