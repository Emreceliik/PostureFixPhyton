# PostureFix Değişiklik Günlüğü

Bu dosya PostureFix projesindeki tüm önemli değişiklikleri belgeler.

Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardını takip eder,
ve proje [Semantic Versioning](https://semver.org/spec/v2.0.0.html) kullanır.

## [Unreleased]
### Planlanan
- Makine öğrenmesi modeli entegrasyonu
- Mobil uygulama senkronizasyonu
- Çoklu kullanıcı desteği
- Bulut senkronizasyonu

## [1.0.0] - 2024-01-15
### Eklenen
#### Ana Özellikler
- Gerçek zamanlı postür izleme sistemi
- MediaPipe tabanlı pose estimation
- Akıllı uyarı ve bildirim sistemi
- Kapsamlı istatistik ve raporlama
- Postür odaklı egzersiz önerileri
- Kişiselleştirilebilir ayarlar sistemi

#### Teknik Özellikler
- PyQt5 tabanlı modern GUI
- SQLite veri tabanı entegrasyonu
- Matplotlib grafik desteği
- Sistem tepsisi entegrasyonu
- Çoklu tema desteği (açık/koyu)
- Kapsamlı logging sistemi

#### Kullanıcı Arayüzü
- Ana pencere ile sekmeli arayüz
- Gerçek zamanlı kamera görüntüsü
- Postür durum göstergesi
- İstatistik dashboard'u
- Egzersiz rehberi
- Ayarlar dialog'u

#### Veri Yönetimi
- Postür verilerinin yerel saklanması
- Oturum bazlı takip
- Günlük/haftalık/aylık raporlar
- Veri dışa aktarma (CSV, JSON, Excel)
- Otomatik yedekleme sistemi

#### Bildirim Sistemi
- Sistem bildirimleri
- Sesli uyarılar
- Görsel uyarılar
- Tray icon bildirimleri
- Özelleştirilebilir uyarı eşikleri

#### Egzersiz Sistemi
- Kategori bazlı egzersizler (boyun, omuz, sırt)
- Rehberli egzersiz talimatları
- Egzersiz zamanlayıcısı
- İlerleme takibi
- Hızlı egzersiz seçenekleri

### Güvenlik
- Yerel veri işleme (internet gerektirmez)
- Kullanıcı verilerinin şifrelenmesi
- Gizlilik odaklı tasarım
- Güvenli veri saklama

### Performans
- Optimize edilmiş görüntü işleme
- Düşük CPU kullanımı
- Bellek yönetimi
- GPU desteği (opsiyonel)
- Veri yumuşatma algoritmaları

### Uyumluluk
- Windows 10/11 desteği
- Python 3.8+ uyumluluğu
- Çeşitli webcam modellerini destekler
- Düşük sistem gereksinimleri

## [0.9.0] - 2024-01-10 (Beta)
### Eklenen
- Beta sürüm çıkarıldı
- Temel postür tespit algoritması
- Basit GUI arayüzü
- SQLite veri tabanı
- Temel bildirim sistemi

### Değiştirilen
- Performans iyileştirmeleri
- UI tasarım güncellemeleri
- Hata düzeltmeleri

### Düzeltilen
- Kamera bağlantı sorunları
- Memory leak'ler
- UI donma sorunları

## [0.5.0] - 2024-01-05 (Alpha)
### Eklenen
- İlk alpha sürüm
- MediaPipe entegrasyonu
- Temel postür analizi
- Prototip GUI

### Bilinen Sorunlar
- Kamera performans sorunları
- Sınırlı postür tespit doğruluğu
- UI responsive sorunları

## Geliştirme Notları

### Sürüm Numaralandırma
- **Major (X.0.0)**: Büyük özellik eklemeleri, API değişiklikleri
- **Minor (0.X.0)**: Yeni özellikler, geriye uyumlu değişiklikler
- **Patch (0.0.X)**: Hata düzeltmeleri, küçük iyileştirmeler

### Kategori Tanımları
- **Eklenen**: Yeni özellikler
- **Değiştirilen**: Mevcut işlevlerde değişiklikler
- **Kaldırılan**: Artık desteklenmeyen özellikler
- **Düzeltilen**: Hata düzeltmeleri
- **Güvenlik**: Güvenlik ile ilgili değişiklikler

### Katkıda Bulunma
Değişiklik günlüğü güncellemeleri için:
1. Her yeni özellik için uygun kategori altına ekleyin
2. Kullanıcı etkisi olan değişiklikleri belgelendirin
3. Sürüm numaralarını semantic versioning'e uygun tutun
4. Tarih formatını YYYY-MM-DD olarak kullanın

### Linkler
[Unreleased]: https://github.com/posturefix/PostureFix/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/posturefix/PostureFix/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/posturefix/PostureFix/compare/v0.5.0...v0.9.0
[0.5.0]: https://github.com/posturefix/PostureFix/releases/tag/v0.5.0
