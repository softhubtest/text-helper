# Python 3.9 slim image
FROM python:3.9-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (gcc vb. gerekebilir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve yükle
# CPU-only Torch kurulumu (Boyut tasarrufu: ~2GB)
RUN pip install --no-cache-dir torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu

# Diger bagimliliklari kopyala ve yukle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Scriptleri kopyala
COPY download_model.py .
COPY start.sh .
RUN chmod +x start.sh

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
CMD ["./start.sh"]
