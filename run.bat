@echo off
REM PostureFix Çalıştırma Scripti
REM Windows için kolay başlatma

echo PostureFix Uygulaması Başlatılıyor...
echo.

REM Python'un kurulu olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo HATA: Python bulunamadı!
    echo Python 3.8+ yüklü olduğundan emin olun.
    echo https://python.org adresinden indirebilirsiniz.
    pause
    exit /b 1
)

REM Sanal ortamın var olup olmadığını kontrol et
if not exist "posturefix_env" (
    echo Sanal ortam bulunamadı, oluşturuluyor...
    python -m venv posturefix_env
    if errorlevel 1 (
        echo HATA: Sanal ortam oluşturulamadı!
        pause
        exit /b 1
    )
)

REM Sanal ortamı aktif et
echo Sanal ortam aktifleştiriliyor...
call posturefix_env\Scripts\activate.bat

REM Bağımlılıkları kontrol et ve yükle
if not exist "posturefix_env\Scripts\pip.exe" (
    echo HATA: Pip bulunamadı!
    pause
    exit /b 1
)

echo Bağımlılıklar kontrol ediliyor...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo UYARI: Bazı bağımlılıklar yüklenemedi.
    echo Devam etmek için herhangi bir tuşa basın...
    pause
)

REM Gerekli dizinleri oluştur
echo Dizinler oluşturuluyor...
python -c "from config import AppConfig; AppConfig.create_directories()" 2>nul

REM Uygulamayı başlat
echo.
echo PostureFix başlatılıyor...
echo Kapatmak için Ctrl+C kullanın veya uygulamadan çıkış yapın.
echo.

python main.py

REM Hata durumunda bekle
if errorlevel 1 (
    echo.
    echo Uygulama hata ile sonlandı!
    echo Log dosyalarını kontrol edin: logs\
    pause
)

echo.
echo PostureFix kapatıldı.
pause
