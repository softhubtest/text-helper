@echo off
setlocal
title TextHelper Ultimate Server
color 0A

echo ==================================================
echo TEXTHELPER ULTIMATE
echo Enterprise NLP Engine + UI + Docker
echo ==================================================
echo.

REM --- CONFIGURATION (OPTIMIZED ULTIMATE) ---
set USE_BERT=true
set USE_GPT=true
set USE_SYMSPELL=true
REM -- Performance Optimization --
set OMP_NUM_THREADS=2
set MKL_NUM_THREADS=2
set USE_QUANTIZATION=true
REM ------------------------------------------

echo [INFO] ULTIMATE Mod optimize edildi:
echo        - CPU Kullanim Limiti: 2 Cekirdek (Sistem donmasini engeller)
echo        - RAM Optimizasyonu: Aktif
echo.
REM --- DOCKER KONTROL ---
echo [INFO] Docker altyapisi kontrol ediliyor...
docker info >nul 2>&1
if %errorlevel% neq 0 goto DockerMissing

echo [OK] Docker tespit edildi. Servisler baslatiliyor...
call docker-compose up -d
if %errorlevel% neq 0 (
    echo [UYARI] docker-compose komutu hatali. Docker Desktop acik mi?
    echo Lite moduna geciliyor...
    goto DockerMissing
)
echo [INFO] Redis ve Elasticsearch containerlari aktif.
goto StartBackend

:DockerMissing
echo [UYARI] Docker aktif degil veya yuklu degil.
echo [INFO] Sistem "Hybrid Lite" modunda calisacak:
echo        - Arama Motoru: SymSpell (Dahili)
echo        - Onbellek: RAM (Dahili)
echo [INFO] Bu mod tek kullanici icin en hizli moddur.
echo.


:StartBackend
REM --- PORT TEMIZIGI (8080) ---
echo [INFO] Port 8080 kontrol ediliyor...
netstat -aon | findstr ":8080" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo [UYARI] Port 8080 dolu. Otomatik temizleniyor...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8080" ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)

REM --- BACKEND BASLATMA ---
echo [INFO] Python altyapisi hazirlaniyor...

if not exist "python_backend" (
    echo [KRITIK HATA] 'python_backend' klasoru bulunamadi!
    echo Lutfen scripti 'TextHelper' ana klasorunde calistirdiginizdan emin olun.
    pause
    exit /b
)

cd python_backend

echo [INFO] Tarayici aciliyor...
start "" "http://localhost:8080"

echo.
echo [BASLATILIYOR] Sunucu devreye aliniyor...
echo --------------------------------------------------
echo Dashboard: http://localhost:8080
echo API Docs:  http://localhost:8080/docs
echo --------------------------------------------------
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

if %errorlevel% neq 0 (
    echo.
    echo [HATA] Sunucu beklenmedik sekilde kapandi!
    echo.
    echo MUHTEMEL COZUMLER:
    echo 1. Python yuklu degilse yukleyin.
    echo 2. Kutuphaneler eksik olabilir. Su komutu calistirin:
    echo    pip install -r requirements.txt
    echo 3. Port 8080 dolu olabilir.
)

echo.
echo Kapatmak icin bir tusa basin...
pause
