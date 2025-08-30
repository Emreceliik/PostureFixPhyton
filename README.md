# PostureFix - Akıllı Postür Düzeltme Uygulaması

## 📋 Proje Açıklaması

PostureFix, bilgisayar başında çalışan kişiler için geliştirilmiş akıllı postür izleme ve düzeltme uygulamasıdır. MediaPipe ve OpenCV teknolojilerini kullanarak gerçek zamanlı postür analizi yapar ve kullanıcıları kötü postür durumlarında uyarır.

## ✨ Özellikler

### 🎯 Ana Fonksiyonlar
- **Gerçek Zamanlı Postür İzleme**: Webcam ile sürekli postür analizi
- **Akıllı Uyarı Sistemi**: Görsel ve sesli uyarılar
- **İstatistik ve Raporlama**: Günlük/haftalık postür raporları
- **Egzersiz Önerileri**: Postür tipine göre özelleştirilmiş egzersizler
- **İlerleme Takibi**: Başarı rozetleri ve ödül sistemi

### 🔧 Teknik Özellikler
- **Python tabanlı** masaüstü uygulaması
- **PyQt5** modern GUI framework
- **OpenCV** görüntü işleme
- **MediaPipe** pose estimation
- **SQLite** veri saklama
- **Matplotlib** grafik ve istatistikler

### 💡 Akıllı Özellikler
- Kişiselleştirilmiş postür eşikleri
- Adaptif uyarı sistemi
- Veri yumuşatma algoritmaları
- Sistem tepsisinde çalışma
- Koyu/aydınlık tema desteği

## 🚀 Kurulum

### Sistem Gereksinimleri
- **Python 3.8+**
- **Windows 10/11** (Linux ve macOS desteği yakında)
- **Webcam** (USB veya dahili)
- **Minimum 4GB RAM**
- **500MB disk alanı**

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/username/PostureFix.git
cd PostureFix
```

### 2. Sanal Ortam Oluşturun (Önerilen)
```bash
python -m venv posturefix_env
posturefix_env\\Scripts\\activate  # Windows
# source posturefix_env/bin/activate  # Linux/Mac
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Gerekli Dizinleri Oluşturun
```bash
python -c "from config import AppConfig; AppConfig.create_directories()"
```

### 5. Uygulamayı Çalıştırın
```bash
python main.py
```

## 📁 Proje Yapısı

```
PostureFix/
├── main.py                 # Ana uygulama dosyası
├── config.py              # Yapılandırma ayarları
├── requirements.txt       # Python bağımlılıkları
├── README.md             # Bu dosya
│
├── core/                 # Ana işlevsellik modülleri
│   ├── __init__.py
│   ├── posture_detector.py    # MediaPipe postür tespiti
│   └── data_manager.py        # Veri yönetimi ve saklama
│
├── gui/                  # Kullanıcı arayüzü
│   ├── __init__.py
│   ├── main_window.py         # Ana pencere
│   │
│   ├── widgets/              # UI bileşenleri
│   │   ├── __init__.py
│   │   ├── camera_widget.py      # Kamera görüntüsü
│   │   ├── posture_display.py    # Postür durumu
│   │   ├── statistics_widget.py  # İstatistikler
│   │   └── exercises_widget.py   # Egzersizler
│   │
│   ├── dialogs/              # Dialog pencereleri
│   │   ├── __init__.py
│   │   └── settings_dialog.py    # Ayarlar
│   │
│   └── styles/               # Tema ve stiller
│       ├── __init__.py
│       └── theme_manager.py      # Tema yöneticisi
│
├── utils/                # Yardımcı modüller
│   ├── __init__.py
│   ├── logger.py             # Logging sistemi
│   └── notifications.py      # Bildirim sistemi
│
├── data/                 # Veri dosyaları (otomatik oluşturulur)
├── models/               # AI modelleri (gelecek sürümlerde)
├── reports/              # Rapor dosyaları
├── logs/                 # Log dosyaları
└── assets/               # Medya dosyaları
    ├── images/
    └── sounds/
```

## 🎮 Kullanım Kılavuzu

### İlk Çalıştırma
1. Uygulamayı başlattığınızda kamera erişim izni isteyecektir
2. "İzlemeyi Başlat" butonuna tıklayarak postür izlemeyi başlatın
3. Kamera görüntüsünde postür çizgilerini göreceksiniz

### Ana Özellikler

#### 📹 Kamera Görüntüsü
- Gerçek zamanlı webcam görüntüsü
- MediaPipe postür çizgileri
- Postür kalitesi göstergesi
- Demo mode (kamera yoksa)

#### 📊 Postür Durumu
- Anlık postür skoru (0-100%)
- Detaylı metrikler (boyun açısı, omuz eğimi, vb.)
- Renk kodlu durum göstergeleri
- Uyarı paneli

#### 📈 İstatistikler
- **Güncel Oturum**: Toplam süre, ortalama skor, uyarı sayısı
- **Günlük İstatistikler**: Haftalık performans grafikleri
- **Trend Analizi**: 30 günlük gelişim trendi

#### 🏃 Egzersizler
- **Önerilen**: Postürünüze özel egzersizler
- **Kategoriler**: Boyun, omuz, sırt, genel
- **Rehberli Egzersiz**: Animasyonlu talimatlar
- **İlerleme Takibi**: Egzersiz geçmişi

### Ayarlar

#### ⚙️ Genel Ayarlar
- Otomatik başlatma
- Veri saklama süresi
- Performans optimizasyonları

#### 📷 Kamera Ayarları
- Kamera seçimi
- Çözünürlük ve FPS
- MediaPipe hassasiyet ayarları

#### 🎯 Postür Ayarları
- Eşik değerleri
- Kalibrasyon
- Veri yumuşatma

#### 🔔 Uyarı Ayarları
- Bildirim türleri
- Ses ayarları
- Uyarı sıklığı

#### 🎨 Görünüm
- Açık/koyu tema
- Pencere davranışları
- Animasyon ayarları

## 🔧 Geliştirici Rehberi

### Kod Yapısı
- **MVC Pattern**: Model-View-Controller mimarisi
- **Modüler Tasarım**: Her özellik ayrı modülde
- **Event-Driven**: PyQt5 sinyal-slot sistemi
- **Async Operations**: Threading ile performans

### Yeni Özellik Ekleme

#### 1. Yeni Widget Ekleme
```python
# gui/widgets/new_widget.py
from PyQt5.QtWidgets import QWidget

class NewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # UI kodları
        pass
```

#### 2. Yeni Analiz Algoritması
```python
# core/new_analyzer.py
class NewAnalyzer:
    def analyze(self, landmarks):
        # Analiz kodları
        return result
```

#### 3. Yeni Bildirim Türü
```python
# utils/notifications.py içinde
def show_new_notification(self, data):
    # Bildirim kodları
    pass
```

### Test Etme
```bash
# Logging testi
python utils/logger.py

# Bildirim testi
python utils/notifications.py

# Kamera testi (GUI gerekli)
python core/posture_detector.py
```

## 📊 Veri Formatları

### Postür Verisi
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "head_forward_angle": 15.5,
  "neck_angle": 22.3,
  "shoulder_slope": 8.7,
  "back_straightness": 12.1,
  "overall_score": 0.75
}
```

### Oturum Verisi
```json
{
  "session_id": "session_20240115_103000",
  "start_time": "2024-01-15T10:30:00",
  "end_time": "2024-01-15T11:15:00",
  "total_duration": 45.0,
  "average_score": 0.78,
  "alerts_triggered": 3
}
```

## 🔒 Gizlilik

- **Yerel İşleme**: Tüm veriler cihazınızda kalır
- **İnternet Gerektirmez**: Çevrimdışı çalışır
- **Veri Şifreleme**: Hassas veriler şifrelenir
- **Kullanıcı Kontrolü**: Veri silme ve dışa aktarma

## 🐛 Sorun Giderme

### Yaygın Sorunlar

#### Kamera Açılmıyor
```bash
# Kamera listesi kontrol
python -c "import cv2; print([cv2.VideoCapture(i).isOpened() for i in range(3)])"
```

#### MediaPipe Hatası
```bash
# MediaPipe yeniden yükleme
pip uninstall mediapipe
pip install mediapipe==0.10.7
```

#### PyQt5 Kurulum Sorunu
```bash
# PyQt5 alternatif kurulum
pip install PyQt5 --index-url https://pypi.python.org/simple/
```

### Log Dosyaları
- **Ana Log**: `logs/posturefix.log`
- **Hata Log**: `logs/errors.log`
- **Veri Tabanı**: `data/posture_data.db`

### Performans Optimizasyonu
- GPU kullanımını etkinleştirin (Ayarlar > Genel)
- Kamera çözünürlüğünü düşürün
- Veri yumuşatma penceresini küçültün

## 🤝 Katkıda Bulunma

1. **Fork** edin
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** edin (`git commit -m 'Add amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

### Geliştirme Kuralları
- PEP 8 kod stilini takip edin
- Docstring'leri ekleyin
- Unit testler yazın
- Changelog güncelleyin

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 👨‍💻 Geliştirici

**PostureFix Team**
- Email: support@posturefix.com
- Website: https://posturefix.com
- GitHub: https://github.com/posturefix

## 🙏 Teşekkürler

- **MediaPipe Team** - Pose estimation
- **OpenCV Community** - Computer vision
- **PyQt Team** - GUI framework
- **Python Community** - Ecosystem

## 📈 Yol Haritası

### v1.1 (Yakında)
- [ ] Makine öğrenmesi modeli entegrasyonu
- [ ] Mobil uygulama senkronizasyonu
- [ ] Çoklu kullanıcı desteği
- [ ] Gelişmiş raporlama

### v1.2 (Gelecek)
- [ ] Bulut senkronizasyonu
- [ ] Takım yönetimi özellikleri
- [ ] API entegrasyonları
- [ ] Wearable device desteği

## 📞 Destek

Sorularınız için:
- **GitHub Issues**: Hata raporları ve özellik istekleri
- **Email**: emre.celik.0052@gmail.com


---

**PostureFix** ile sağlıklı çalışma alışkanlıkları edinin! 🚀
