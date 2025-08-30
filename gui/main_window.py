"""
PostureFix - Ana Pencere
Modern ve kullanıcı dostu ana uygulama penceresi
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTabWidget, QLabel, QPushButton, QProgressBar,
                            QFrame, QGridLayout, QScrollArea, QSplitter,
                            QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import QTimer, pyqtSignal, Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon
import logging
from datetime import datetime

from config import AppConfig, COLORS
from gui.widgets.camera_widget import CameraWidget
from gui.widgets.posture_display import PostureDisplayWidget
from gui.widgets.statistics_widget import StatisticsWidget
from gui.widgets.exercises_widget import ExercisesWidget
from gui.dialogs.settings_dialog import SettingsDialog
from gui.styles.theme_manager import ThemeManager

class MainWindow(QMainWindow):
    """Ana pencere sınıfı"""
    
    # Sinyaller
    settings_changed = pyqtSignal(dict)
    start_monitoring = pyqtSignal()
    stop_monitoring = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        
        # Tema yöneticisi
        self.theme_manager = ThemeManager()
        
        # İzleme durumu
        self.is_monitoring = False
        
        # UI kurulumu
        self.setup_ui()
        self.setup_connections()
        self.apply_theme()
        
        # Başlangıç durumu
        self.update_monitoring_status(False)
        
        self.logger.info("Ana pencere oluşturuldu")
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        # Ana pencere ayarları
        self.setWindowTitle(f"{self.config.APP_NAME} v{self.config.VERSION}")
        self.setGeometry(100, 100, self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        self.setMinimumSize(self.config.MIN_WINDOW_WIDTH, self.config.MIN_WINDOW_HEIGHT)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Üst bar
        self.create_top_bar(main_layout)
        
        # Ana içerik alanı
        self.create_main_content(main_layout)
        
        # Alt durum çubuğu
        self.create_status_bar()
    
    def create_top_bar(self, parent_layout):
        """Üst kontrol çubuğunu oluştur"""
        top_bar = QFrame()
        top_bar.setFixedHeight(80)
        top_bar.setFrameStyle(QFrame.StyledPanel)
        
        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo/Başlık
        title_label = QLabel("PostureFix")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Kontrol butonları
        self.start_button = QPushButton("İzlemeyi Başlat")
        self.start_button.setFixedSize(150, 40)
        self.start_button.setObjectName("primary_button")
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("İzlemeyi Durdur")
        self.stop_button.setFixedSize(150, 40)
        self.stop_button.setObjectName("secondary_button")
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        # Ayarlar butonu
        settings_button = QPushButton("Ayarlar")
        settings_button.setFixedSize(100, 40)
        settings_button.setObjectName("settings_button")
        layout.addWidget(settings_button)
        settings_button.clicked.connect(self.show_settings_dialog)
        
        parent_layout.addWidget(top_bar)
    
    def create_main_content(self, parent_layout):
        """Ana içerik alanını oluştur"""
        # Splitter ile bölünmüş alan
        splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel - Kamera ve postür gösterimi
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Sağ panel - Sekmeli alan
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Splitter oranları
        splitter.setSizes([400, 800])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        parent_layout.addWidget(splitter)
    
    def create_left_panel(self):
        """Sol paneli oluştur (kamera ve postür durumu)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Kamera widget'ı
        self.camera_widget = CameraWidget()
        layout.addWidget(self.camera_widget)
        
        # Postür durum göstergesi
        self.posture_display = PostureDisplayWidget()
        layout.addWidget(self.posture_display)
        
        return panel
    
    def create_right_panel(self):
        """Sağ paneli oluştur (sekmeli alan)"""
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # İstatistikler sekmesi
        self.statistics_widget = StatisticsWidget()
        self.tab_widget.addTab(self.statistics_widget, "📊 İstatistikler")
        
        # Egzersizler sekmesi
        self.exercises_widget = ExercisesWidget()
        self.tab_widget.addTab(self.exercises_widget, "🏃 Egzersizler")
        
        # Geçmiş sekmesi
        history_widget = self.create_history_widget()
        self.tab_widget.addTab(history_widget, "📈 Geçmiş")
        
        # Raporlar sekmesi
        reports_widget = self.create_reports_widget()
        self.tab_widget.addTab(reports_widget, "📋 Raporlar")
        
        return self.tab_widget
    
    def create_history_widget(self):
        """Geçmiş sekmesini oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Başlık
        title = QLabel("Postür Geçmişi")
        title.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(title)
        
        # İçerik (şimdilik placeholder)
        content = QLabel("Geçmiş veriler burada gösterilecek...")
        content.setAlignment(Qt.AlignCenter)
        content.setStyleSheet("color: gray; font-size: 14px;")
        layout.addWidget(content)
        
        return widget
    
    def create_reports_widget(self):
        """Raporlar sekmesini oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Başlık
        title = QLabel("Postür Raporları")
        title.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Rapor butonları
        buttons_layout = QHBoxLayout()
        
        daily_report_btn = QPushButton("Günlük Rapor")
        daily_report_btn.setObjectName("report_button")
        buttons_layout.addWidget(daily_report_btn)
        
        weekly_report_btn = QPushButton("Haftalık Rapor")
        weekly_report_btn.setObjectName("report_button")
        buttons_layout.addWidget(weekly_report_btn)
        
        monthly_report_btn = QPushButton("Aylık Rapor")
        monthly_report_btn.setObjectName("report_button")
        buttons_layout.addWidget(monthly_report_btn)
        
        export_btn = QPushButton("Verileri Dışa Aktar")
        export_btn.setObjectName("export_button")
        buttons_layout.addWidget(export_btn)
        
        layout.addLayout(buttons_layout)
        
        # Rapor içeriği
        report_content = QLabel("Rapor içeriği burada gösterilecek...")
        report_content.setAlignment(Qt.AlignCenter)
        report_content.setStyleSheet("color: gray; font-size: 14px;")
        layout.addWidget(report_content)
        
        return widget
    
    def create_status_bar(self):
        """Alt durum çubuğunu oluştur"""
        status_bar = self.statusBar()
        
        # Durum etiketi
        self.status_label = QLabel("Hazır")
        status_bar.addWidget(self.status_label)
        
        # Sağ tarafta göstergeler
        status_bar.addPermanentWidget(QLabel(""))  # Spacer
        
        # Bağlantı durumu
        self.connection_status = QLabel("🔴 Bağlantı Yok")
        status_bar.addPermanentWidget(self.connection_status)
        
        # Kamera durumu
        self.camera_status = QLabel("📷 Kamera Kapalı")
        status_bar.addPermanentWidget(self.camera_status)
    
    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        # Buton bağlantıları
        self.start_button.clicked.connect(self.start_monitoring_clicked)
        self.stop_button.clicked.connect(self.stop_monitoring_clicked)
        
        # Widget bağlantıları
        self.camera_widget.frame_ready.connect(self.on_frame_ready)
        self.posture_display.alert_acknowledged.connect(self.on_alert_acknowledged)
    
    def apply_theme(self):
        """Temayı uygula"""
        try:
            # Tema stilini uygula
            theme_style = self.theme_manager.get_theme_stylesheet(self.config.DEFAULT_THEME)
            self.setStyleSheet(theme_style)
            
            # Widget'lara da temayı uygula
            self.camera_widget.apply_theme(self.config.DEFAULT_THEME)
            self.posture_display.apply_theme(self.config.DEFAULT_THEME)
            self.statistics_widget.apply_theme(self.config.DEFAULT_THEME)
            
        except Exception as e:
            self.logger.error(f"Tema uygulama hatası: {str(e)}")
    
    def start_monitoring_clicked(self):
        """İzleme başlatma butonu tıklandı"""
        try:
            self.start_monitoring.emit()
            self.update_monitoring_status(True)
            self.show_status_message("Postür izleme başlatıldı", 3000)
        except Exception as e:
            self.logger.error(f"İzleme başlatma hatası: {str(e)}")
            QMessageBox.warning(self, "Hata", f"İzleme başlatılamadı: {str(e)}")
    
    def stop_monitoring_clicked(self):
        """İzleme durdurma butonu tıklandı"""
        try:
            self.stop_monitoring.emit()
            self.update_monitoring_status(False)
            self.show_status_message("Postür izleme durduruldu", 3000)
        except Exception as e:
            self.logger.error(f"İzleme durdurma hatası: {str(e)}")
    
    def update_monitoring_status(self, is_active: bool):
        """İzleme durumunu güncelle"""
        self.is_monitoring = is_active
        
        # Butonları güncelle
        self.start_button.setEnabled(not is_active)
        self.stop_button.setEnabled(is_active)
        
        # Durum çubuğunu güncelle
        if is_active:
            self.connection_status.setText("🟢 Bağlı")
            self.camera_status.setText("📹 Kamera Aktif")
            self.status_label.setText("İzleme aktif...")
        else:
            self.connection_status.setText("🔴 Bağlantı Yok")
            self.camera_status.setText("📷 Kamera Kapalı")
            self.status_label.setText("Hazır")
        
        # Kamera widget'ını güncelle
        self.camera_widget.set_monitoring_active(is_active)
    
    def update_posture_display(self, posture_data: dict):
        """Postür gösterimini güncelle"""
        try:
            self.posture_display.update_posture_data(posture_data)
            self.statistics_widget.update_realtime_data(posture_data)
            
            # Son güncelleme zamanını göster
            timestamp = posture_data.get('timestamp', datetime.now())
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp)
            
            self.status_label.setText(f"Son güncelleme: {timestamp.strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Postür gösterim güncelleme hatası: {str(e)}")
    
    def show_alert(self, alert_message: str):
        """Uyarı göster"""
        try:
            self.posture_display.show_alert(alert_message)
            
            # Sistem tepsisinde de bildirim göster
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.showMessage(
                    "PostureFix Uyarısı",
                    alert_message,
                    QSystemTrayIcon.Warning,
                    5000  # 5 saniye
                )
            
        except Exception as e:
            self.logger.error(f"Uyarı gösterme hatası: {str(e)}")
    
    def on_frame_ready(self, frame):
        """Kameradan frame hazır olduğunda"""
        # Frame işleme (gerekirse)
        pass
    
    def on_alert_acknowledged(self):
        """Uyarı onaylandığında"""
        self.show_status_message("Uyarı onaylandı", 2000)
    
    def show_settings_dialog(self):
        """Ayarlar penceresini göster"""
        try:
            dialog = SettingsDialog(self)
            if dialog.exec_() == SettingsDialog.Accepted:
                settings = dialog.get_settings()
                self.settings_changed.emit(settings)
                self.show_status_message("Ayarlar güncellendi", 3000)
        except Exception as e:
            self.logger.error(f"Ayarlar penceresi hatası: {str(e)}")
    
    def show_status_message(self, message: str, timeout: int = 2000):
        """Durum çubuğunda mesaj göster"""
        self.statusBar().showMessage(message, timeout)
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        # Sistem tepsisine gizle
        if hasattr(self, 'tray_icon') and self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
            self.show_status_message("Uygulama sistem tepsisinde çalışmaya devam ediyor", 3000)
        else:
            # Gerçekten kapat
            self.stop_monitoring.emit()
            event.accept()
    
    def changeEvent(self, event):
        """Pencere durumu değiştiğinde"""
        if event.type() == event.WindowStateChange:
            if self.isMinimized():
                # Minimize edildiğinde sistem tepsisine gizle
                self.hide()
                event.ignore()
        
        super().changeEvent(event)
