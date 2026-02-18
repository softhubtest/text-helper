#!/bin/bash
set -e # Hata olursa dur

# Modelin varligini kontrol et (Runtime Download)
echo "Model kontrol ediliyor..."
python download_model.py

# Uygulamayi baslat
echo "Uygulama baslatiliyor..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive 120
