"""
PostureFix - Bildirim Sistemi
Sistem bildirimleri ve uyarı yönetimi
"""

import os
import sys
import logging
from typing import Optional
from datetime import datetime
import threading
import time

try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from PyQt5.QtWidgets import QSystemTrayIcon, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon

from config import AppConfig, SOUND_FILES

class NotificationManager(QObject):
    """Bildirim yöneticisi sınıfı"""
    
    # Sinyaller
    notification_sent = pyqtSignal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        
        # Bildirim ayarları
        self.notifications_enabled = True
        self.sound_enabled = self.config.SOUND_ENABLED
        self.sound_volume = self.config.SOUND_VOLUME
        
        # Ses sistemi başlat
        self.init_sound_system()
        
        # Son bildirim zamanları (spam önleme için)
        self.last_notifications = {}
        self.notification_cooldown = 5  # saniye
        
        self.logger.info("NotificationManager başlatıldı")
    
    def init_sound_system(self):
        """Ses sistemini başlat"""
        self.sound_system = None
        
        if PYGAME_AVAILABLE and self.sound_enabled:
            try:
                pygame.mixer.init()
                self.sound_system = "pygame"
                self.logger.info("Pygame ses sistemi başlatıldı")
            except Exception as e:
                self.logger.warning(f"Pygame başlatılamadı: {str(e)}")
        
        if not self.sound_system:
            self.logger.info("Ses sistemi mevcut değil")
    
    def show_system_notification(self, title: str, message: str, 
                                icon_path: str = None, timeout: int = 5):
        """Sistem bildirimi göster"""
        try:
            if not self.notifications_enabled:
                return
            
            # Spam önleme
            notification_key = f"{title}:{message}"
            current_time = time.time()
            
            if notification_key in self.last_notifications:
                if current_time - self.last_notifications[notification_key] < self.notification_cooldown:
                    self.logger.debug(f"Bildirim spam önlendi: {title}")
                    return
            
            self.last_notifications[notification_key] = current_time
            
            # Plyer ile sistem bildirimi
            if PLYER_AVAILABLE:
                notification.notify(
                    title=title,
                    message=message,
                    app_icon=icon_path or "assets/images/icon.png",
                    timeout=timeout
                )
                
                self.logger.info(f"Sistem bildirimi gönderildi: {title}")
                self.notification_sent.emit(title, message)
            else:
                self.logger.warning("Plyer mevcut değil, sistem bildirimi gösterilemiyor")
                
        except Exception as e:
            self.logger.error(f"Sistem bildirimi hatası: {str(e)}")
    
    def show_tray_notification(self, tray_icon: QSystemTrayIcon, 
                              title: str, message: str, 
                              icon_type: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information,
                              timeout: int = 5000):
        """Sistem tepsisi bildirimi göster"""
        try:
            if not self.notifications_enabled or not tray_icon:
                return
            
            if QSystemTrayIcon.isSystemTrayAvailable():
                tray_icon.showMessage(title, message, icon_type, timeout)
                self.logger.info(f"Tray bildirimi gönderildi: {title}")
                self.notification_sent.emit(title, message)
            else:
                self.logger.warning("Sistem tepsisi mevcut değil")
                
        except Exception as e:
            self.logger.error(f"Tray bildirimi hatası: {str(e)}")
    
    def play_sound(self, sound_type: str = "alert"):
        """Ses çal"""
        try:
            if not self.sound_enabled or not self.sound_system:
                return
            
            sound_file = SOUND_FILES.get(sound_type, SOUND_FILES["alert"])
            
            if not os.path.exists(sound_file):
                self.logger.warning(f"Ses dosyası bulunamadı: {sound_file}")
                return
            
            if self.sound_system == "pygame":
                # Pygame ile ses çal
                sound = pygame.mixer.Sound(sound_file)
                sound.set_volume(self.sound_volume)
                sound.play()
                
                self.logger.debug(f"Ses çalındı: {sound_type}")
            
        except Exception as e:
            self.logger.error(f"Ses çalma hatası: {str(e)}")
    
    def show_posture_alert(self, score: float, tray_icon: QSystemTrayIcon = None):
        """Postür uyarısı göster"""
        if score < 0.3:
            severity = "Kritik"
            icon_type = QSystemTrayIcon.Critical
            sound_type = "alert"
        elif score < 0.5:
            severity = "Kötü"
            icon_type = QSystemTrayIcon.Warning
            sound_type = "alert"
        else:
            return  # Uyarı gerekmiyor
        
        title = "PostureFix Uyarısı"
        message = f"{severity} postür tespit edildi! Lütfen duruşunuzu düzeltin.\nSkor: {int(score * 100)}%"
        
        # Sistem bildirimi
        self.show_system_notification(title, message)
        
        # Tray bildirimi
        if tray_icon:
            self.show_tray_notification(tray_icon, title, message, icon_type)
        
        # Ses uyarısı
        self.play_sound(sound_type)
    
    def show_exercise_reminder(self, tray_icon: QSystemTrayIcon = None):
        """Egzersiz hatırlatıcısı göster"""
        title = "PostureFix Hatırlatıcı"
        message = "Postürünüzü düzeltmek için egzersiz yapma zamanı!"
        
        self.show_system_notification(title, message)
        
        if tray_icon:
            self.show_tray_notification(tray_icon, title, message, QSystemTrayIcon.Information)
        
        self.play_sound("reminder")
    
    def show_session_summary(self, session_data: dict, tray_icon: QSystemTrayIcon = None):
        """Oturum özeti bildirimi"""
        duration = session_data.get('duration', 0)
        avg_score = session_data.get('average_score', 0)
        alerts_count = session_data.get('alerts_count', 0)
        
        title = "Oturum Tamamlandı"
        message = f"""Postür İzleme Oturumu Sona Erdi
Süre: {int(duration)} dakika
Ortalama Skor: {int(avg_score * 100)}%
Uyarı Sayısı: {alerts_count}"""
        
        self.show_system_notification(title, message, timeout=10)
        
        if tray_icon:
            self.show_tray_notification(tray_icon, title, message, 
                                      QSystemTrayIcon.Information, 10000)
    
    def show_achievement(self, achievement_name: str, description: str, 
                        tray_icon: QSystemTrayIcon = None):
        """Başarı bildirimi göster"""
        title = f"🏆 Başarı Kazanıldı!"
        message = f"{achievement_name}\n{description}"
        
        self.show_system_notification(title, message, timeout=8)
        
        if tray_icon:
            self.show_tray_notification(tray_icon, title, message, 
                                      QSystemTrayIcon.Information, 8000)
        
        self.play_sound("success")
    
    def show_error_notification(self, error_message: str, tray_icon: QSystemTrayIcon = None):
        """Hata bildirimi göster"""
        title = "PostureFix Hatası"
        message = f"Bir hata oluştu: {error_message}"
        
        self.show_system_notification(title, message, timeout=10)
        
        if tray_icon:
            self.show_tray_notification(tray_icon, title, message, 
                                      QSystemTrayIcon.Critical, 10000)
    
    def set_notifications_enabled(self, enabled: bool):
        """Bildirimleri etkinleştir/devre dışı bırak"""
        self.notifications_enabled = enabled
        self.logger.info(f"Bildirimler {'etkinleştirildi' if enabled else 'devre dışı bırakıldı'}")
    
    def set_sound_enabled(self, enabled: bool):
        """Sesleri etkinleştir/devre dışı bırak"""
        self.sound_enabled = enabled
        
        if enabled and not self.sound_system:
            self.init_sound_system()
        
        self.logger.info(f"Sesler {'etkinleştirildi' if enabled else 'devre dışı bırakıldı'}")
    
    def set_sound_volume(self, volume: float):
        """Ses seviyesini ayarla (0.0 - 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        self.logger.info(f"Ses seviyesi ayarlandı: {int(self.sound_volume * 100)}%")
    
    def test_notification(self, tray_icon: QSystemTrayIcon = None):
        """Test bildirimi göster"""
        title = "PostureFix Test"
        message = "Bu bir test bildirimidir. Bildirim sistemi çalışıyor!"
        
        self.show_system_notification(title, message)
        
        if tray_icon:
            self.show_tray_notification(tray_icon, title, message)
        
        self.play_sound("success")
    
    def cleanup(self):
        """Kaynakları temizle"""
        try:
            if self.sound_system == "pygame":
                pygame.mixer.quit()
            
            self.logger.info("NotificationManager kaynakları temizlendi")
            
        except Exception as e:
            self.logger.error(f"NotificationManager cleanup hatası: {str(e)}")

class AlertSystem(QObject):
    """Gelişmiş uyarı sistemi"""
    
    # Sinyaller
    alert_triggered = pyqtSignal(str, dict)  # alert_type, alert_data
    alert_resolved = pyqtSignal(str)  # alert_type
    
    def __init__(self, notification_manager: NotificationManager):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.notification_manager = notification_manager
        
        # Aktif uyarılar
        self.active_alerts = {}
        
        # Uyarı kuralları
        self.alert_rules = {
            "poor_posture": {
                "threshold": 0.4,
                "duration": 10,  # saniye
                "cooldown": 30,  # saniye
                "escalation": True
            },
            "no_movement": {
                "threshold": 300,  # 5 dakika hareket yok
                "cooldown": 600,   # 10 dakika
                "escalation": False
            },
            "session_too_long": {
                "threshold": 3600,  # 1 saat
                "cooldown": 1800,   # 30 dakika
                "escalation": True
            }
        }
        
        # Zamanlayıcılar
        self.alert_timers = {}
        
        self.logger.info("AlertSystem başlatıldı")
    
    def check_posture_alert(self, score: float, tray_icon: QSystemTrayIcon = None):
        """Postür uyarısı kontrolü"""
        alert_type = "poor_posture"
        rule = self.alert_rules[alert_type]
        
        if score < rule["threshold"]:
            # Kötü postür tespit edildi
            if alert_type not in self.active_alerts:
                # Yeni uyarı başlat
                self.start_alert_timer(alert_type, rule["duration"])
                self.active_alerts[alert_type] = {
                    "start_time": time.time(),
                    "score": score,
                    "escalation_level": 0
                }
            else:
                # Mevcut uyarıyı güncelle
                self.active_alerts[alert_type]["score"] = score
        else:
            # Postür düzeldi
            if alert_type in self.active_alerts:
                self.resolve_alert(alert_type)
    
    def start_alert_timer(self, alert_type: str, duration: float):
        """Uyarı zamanlayıcısı başlat"""
        if alert_type in self.alert_timers:
            self.alert_timers[alert_type].stop()
        
        timer = QTimer()
        timer.timeout.connect(lambda: self.trigger_alert(alert_type))
        timer.setSingleShot(True)
        timer.start(int(duration * 1000))  # milisaniye
        
        self.alert_timers[alert_type] = timer
    
    def trigger_alert(self, alert_type: str):
        """Uyarıyı tetikle"""
        if alert_type not in self.active_alerts:
            return
        
        alert_data = self.active_alerts[alert_type]
        
        # Bildirim göster
        if alert_type == "poor_posture":
            self.notification_manager.show_posture_alert(
                alert_data["score"]
            )
        
        # Sinyal gönder
        self.alert_triggered.emit(alert_type, alert_data)
        
        # Escalation kontrolü
        rule = self.alert_rules[alert_type]
        if rule.get("escalation", False):
            alert_data["escalation_level"] += 1
            
            # Daha sık uyarı
            if alert_data["escalation_level"] < 3:
                escalated_duration = rule["duration"] * (0.5 ** alert_data["escalation_level"])
                self.start_alert_timer(alert_type, escalated_duration)
        
        self.logger.warning(f"Uyarı tetiklendi: {alert_type}")
    
    def resolve_alert(self, alert_type: str):
        """Uyarıyı çöz"""
        if alert_type in self.active_alerts:
            del self.active_alerts[alert_type]
        
        if alert_type in self.alert_timers:
            self.alert_timers[alert_type].stop()
            del self.alert_timers[alert_type]
        
        self.alert_resolved.emit(alert_type)
        self.logger.info(f"Uyarı çözüldü: {alert_type}")
    
    def get_active_alerts(self) -> dict:
        """Aktif uyarıları döndür"""
        return self.active_alerts.copy()
    
    def update_alert_rule(self, alert_type: str, rule_updates: dict):
        """Uyarı kuralını güncelle"""
        if alert_type in self.alert_rules:
            self.alert_rules[alert_type].update(rule_updates)
            self.logger.info(f"Uyarı kuralı güncellendi: {alert_type}")
    
    def cleanup(self):
        """Kaynakları temizle"""
        for timer in self.alert_timers.values():
            timer.stop()
        
        self.alert_timers.clear()
        self.active_alerts.clear()
        
        self.logger.info("AlertSystem kaynakları temizlendi")

# Test fonksiyonu
def test_notifications():
    """Bildirim sistemini test et"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Bildirim yöneticisi
    notification_manager = NotificationManager()
    
    # Test bildirimleri
    notification_manager.test_notification()
    
    # Test sesi
    notification_manager.play_sound("alert")
    
    # Test postür uyarısı
    notification_manager.show_posture_alert(0.3)
    
    print("Bildirim testleri tamamlandı")

if __name__ == "__main__":
    test_notifications()
