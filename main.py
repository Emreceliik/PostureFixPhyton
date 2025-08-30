"""
PostureFix - Ana Uygulama Dosyası
Postür düzeltme uygulamasının ana giriş noktası
"""

import sys
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon

# Proje modüllerini import et
from config import AppConfig
from gui.main_window import MainWindow
from core.posture_detector import PostureDetector
from core.data_manager import DataManager
from utils.logger import setup_logger

class PostureFixApp(QObject):
    """Ana uygulama sınıfı"""
    
    # Sinyaller
    posture_changed = pyqtSignal(dict)
    alert_triggered = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Yapılandırma
        self.config = AppConfig()
        self.config.create_directories()
        
        # Logger kurulumu
        self.logger = setup_logger()
        self.logger.info("PostureFix uygulaması başlatılıyor...")
        
        # Bileşenleri başlat
        self.setup_components()
        self.setup_ui()
        self.setup_system_tray()
        self.setup_timers()
        
        # Sinyalleri bağla
        self.connect_signals()
        
    def setup_components(self):
        """Ana bileşenleri başlat"""
        try:
            # Veri yöneticisi
            self.data_manager = DataManager()
            
            # Postür dedektörü
            self.posture_detector = PostureDetector()
            
            self.logger.info("Tüm bileşenler başarıyla başlatıldı")
            
        except Exception as e:
            self.logger.error(f"Bileşen başlatma hatası: {str(e)}")
            sys.exit(1)
    
    def setup_ui(self):
        """Kullanıcı arayüzünü başlat"""
        try:
            self.main_window = MainWindow()
            self.main_window.show()
            
            self.logger.info("Ana pencere başarıyla oluşturuldu")
            
        except Exception as e:
            self.logger.error(f"UI başlatma hatası: {str(e)}")
            sys.exit(1)
    
    def setup_system_tray(self):
        """Sistem tepsisi menüsünü oluştur"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("Sistem tepsisi mevcut değil")
            return
        
        # Tray icon oluştur
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/images/icon.png"))
        
        # Tray menüsü oluştur
        tray_menu = QMenu()
        
        # Menü öğeleri
        show_action = QAction("Göster", self)
        show_action.triggered.connect(self.show_main_window)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Gizle", self)
        hide_action.triggered.connect(self.hide_main_window)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        settings_action = QAction("Ayarlar", self)
        settings_action.triggered.connect(self.show_settings)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.logger.info("Sistem tepsisi menüsü oluşturuldu")
    
    def setup_timers(self):
        """Zamanlayıcıları ayarla"""
        # Postür kontrol zamanlayıcısı
        self.posture_timer = QTimer()
        self.posture_timer.timeout.connect(self.check_posture)
        self.posture_timer.start(int(self.config.POSTURE_CHECK_INTERVAL * 1000))
        
        # Veri kaydetme zamanlayıcısı
        self.data_save_timer = QTimer()
        self.data_save_timer.timeout.connect(self.save_periodic_data)
        self.data_save_timer.start(self.config.STATS_SAVE_INTERVAL * 1000)
        
        self.logger.info("Zamanlayıcılar başlatıldı")
    
    def connect_signals(self):
        """Sinyalleri bağla"""
        # Postür değişikliği sinyali
        self.posture_changed.connect(self.main_window.update_posture_display)
        
        # Uyarı sinyali
        self.alert_triggered.connect(self.main_window.show_alert)
        
        # Ana pencere sinyalleri
        self.main_window.settings_changed.connect(self.update_settings)
        self.main_window.start_monitoring.connect(self.start_monitoring)
        self.main_window.stop_monitoring.connect(self.stop_monitoring)
    
    def check_posture(self):
        """Postür kontrolü yap"""
        try:
            # Postür analizi
            posture_data = self.posture_detector.analyze_posture()
            
            if posture_data:
                # Postür verilerini işle
                self.process_posture_data(posture_data)
                
        except Exception as e:
            self.logger.error(f"Postür kontrolü hatası: {str(e)}")
    
    def process_posture_data(self, posture_data):
        """Postür verilerini işle"""
        # Postür skorunu hesapla
        posture_score = self.calculate_posture_score(posture_data)
        
        # Veriyi kaydet
        self.data_manager.save_posture_data(posture_data, posture_score)
        
        # UI'yi güncelle
        display_data = {
            'posture_data': posture_data,
            'score': posture_score,
            'timestamp': datetime.now()
        }
        self.posture_changed.emit(display_data)
        
        # Kötü postür kontrolü
        if posture_score < self.config.POOR_POSTURE_THRESHOLD:
            self.trigger_posture_alert(posture_score)
    
    def calculate_posture_score(self, posture_data):
        """Postür skorunu hesapla (0-1 arası)"""
        # Basit skorlama algoritması
        # Gerçek implementasyonda daha karmaşık olacak
        score = 1.0
        
        # Kafa öne eğimi kontrolü
        if posture_data.get('head_forward_angle', 0) > 15:
            score -= 0.3
        
        # Omuz eğimi kontrolü  
        if posture_data.get('shoulder_slope', 0) > 10:
            score -= 0.2
        
        # Boyun açısı kontrolü
        if posture_data.get('neck_angle', 0) > 20:
            score -= 0.3
        
        # Sırt düzlüğü kontrolü
        if posture_data.get('back_straightness', 0) > 15:
            score -= 0.2
        
        return max(0.0, score)
    
    def trigger_posture_alert(self, score):
        """Postür uyarısını tetikle"""
        alert_message = f"Kötü postür tespit edildi! Skor: {score:.2f}"
        self.alert_triggered.emit(alert_message)
        
        self.logger.warning(alert_message)
    
    def save_periodic_data(self):
        """Periyodik veri kaydetme"""
        try:
            self.data_manager.save_session_data()
            self.logger.debug("Periyodik veri kaydedildi")
        except Exception as e:
            self.logger.error(f"Veri kaydetme hatası: {str(e)}")
    
    def start_monitoring(self):
        """İzlemeyi başlat"""
        try:
            self.posture_detector.start_camera()
            self.posture_timer.start()
            self.logger.info("Postür izleme başlatıldı")
        except Exception as e:
            self.logger.error(f"İzleme başlatma hatası: {str(e)}")
    
    def stop_monitoring(self):
        """İzlemeyi durdur"""
        try:
            self.posture_detector.stop_camera()
            self.posture_timer.stop()
            self.logger.info("Postür izleme durduruldu")
        except Exception as e:
            self.logger.error(f"İzleme durdurma hatası: {str(e)}")
    
    def update_settings(self, settings):
        """Ayarları güncelle"""
        # Ayarları uygula
        self.logger.info("Ayarlar güncellendi")
    
    def show_main_window(self):
        """Ana pencereyi göster"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def hide_main_window(self):
        """Ana pencereyi gizle"""
        self.main_window.hide()
    
    def show_settings(self):
        """Ayarlar penceresini göster"""
        self.main_window.show_settings_dialog()
    
    def quit_application(self):
        """Uygulamayı kapat"""
        try:
            # Kaynakları temizle
            self.posture_detector.cleanup()
            self.data_manager.save_session_data()
            
            self.logger.info("PostureFix uygulaması kapatılıyor...")
            QApplication.quit()
            
        except Exception as e:
            self.logger.error(f"Uygulama kapatma hatası: {str(e)}")
            QApplication.quit()

def main():
    """Ana fonksiyon"""
    # QApplication oluştur
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Sistem tepsisinde çalışabilmesi için
    
    # Uygulama bilgilerini ayarla
    app.setApplicationName(AppConfig.APP_NAME)
    app.setApplicationVersion(AppConfig.VERSION)
    app.setOrganizationName(AppConfig.AUTHOR)
    
    try:
        # Ana uygulama örneğini oluştur
        posture_app = PostureFixApp()
        
        # Uygulamayı çalıştır
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Uygulama başlatma hatası: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
