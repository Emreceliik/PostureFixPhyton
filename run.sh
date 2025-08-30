#!/bin/bash
# PostureFix Çalıştırma Scripti
# Linux/macOS için kolay başlatma

echo "PostureFix Uygulaması Başlatılıyor..."
echo

# Python'un kurulu olup olmadığını kontrol et
if ! command -v python3 &> /dev/null; then
    echo "HATA: Python3 bulunamadı!"
    echo "Python 3.8+ yüklü olduğundan emin olun."
    exit 1
fi

# Python sürümünü kontrol et
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "HATA: Python $required_version+ gerekli, mevcut: $python_version"
    exit 1
fi

# Sanal ortamın var olup olmadığını kontrol et
if [ ! -d "posturefix_env" ]; then
    echo "Sanal ortam bulunamadı, oluşturuluyor..."
    python3 -m venv posturefix_env
    if [ $? -ne 0 ]; then
        echo "HATA: Sanal ortam oluşturulamadı!"
        exit 1
    fi
fi

# Sanal ortamı aktif et
echo "Sanal ortam aktifleştiriliyor..."
source posturefix_env/bin/activate

# Pip'i güncelle
echo "Pip güncelleniyor..."
pip install --upgrade pip > /dev/null 2>&1

# Bağımlılıkları kontrol et ve yükle
echo "Bağımlılıklar kontrol ediliyor..."
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "UYARI: Bazı bağımlılıklar yüklenemedi."
    echo "Devam etmek için Enter'a basın..."
    read
fi

# Gerekli dizinleri oluştur
echo "Dizinler oluşturuluyor..."
python -c "from config import AppConfig; AppConfig.create_directories()" 2>/dev/null

# Sistem bağımlılıklarını kontrol et
echo "Sistem bağımlılıkları kontrol ediliyor..."

# Linux için
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # OpenCV için gerekli kütüphaneler
    if ! ldconfig -p | grep -q libGL.so; then
        echo "UYARI: OpenGL kütüphanesi bulunamadı."
        echo "Ubuntu/Debian: sudo apt-get install libgl1-mesa-glx"
        echo "CentOS/RHEL: sudo yum install mesa-libGL"
    fi
    
    if ! ldconfig -p | grep -q libglib; then
        echo "UYARI: GLib kütüphanesi bulunamadı."
        echo "Ubuntu/Debian: sudo apt-get install libglib2.0-0"
    fi
fi

# macOS için
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS sistemi tespit edildi."
    # Gerekli kontroller burada yapılabilir
fi

# Uygulamayı başlat
echo
echo "PostureFix başlatılıyor..."
echo "Kapatmak için Ctrl+C kullanın veya uygulamadan çıkış yapın."
echo

python main.py

# Hata durumunda bilgi ver
if [ $? -ne 0 ]; then
    echo
    echo "Uygulama hata ile sonlandı!"
    echo "Log dosyalarını kontrol edin: logs/"
    echo "Enter'a basın..."
    read
fi

echo
echo "PostureFix kapatıldı."
