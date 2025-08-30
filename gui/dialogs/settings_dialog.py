"""
PostureFix - Ayarlar Dialog'u
Uygulama ayarlarını yönetmek için dialog penceresi
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QWidget, QLabel, QSpinBox, QDoubleSpinBox, 
                            QCheckBox, QComboBox, QSlider, QPushButton,
                            QGroupBox, QGridLayout, QLineEdit, QFileDialog,
                            QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import logging
import json
import os

from config import AppConfig, POSTURE_THRESHOLDS, COLORS

class SettingsDialog(QDialog):
    """Ayarlar dialog'u"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        
        # Ayarlar
        self.settings = self.load_current_settings()
        
        # UI kurulumu
        self.setup_ui()
        self.load_settings_to_ui()
        
        self.logger.info("SettingsDialog oluşturuldu")
    
    def setup_ui(self):
        """UI kurulumu"""
        self.setWindowTitle("PostureFix Ayarları")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Genel ayarlar sekmesi
        self.create_general_tab()
        self.tab_widget.addTab(self.general_widget, "Genel")
        
        # Kamera ayarları sekmesi
        self.create_camera_tab()
        self.tab_widget.addTab(self.camera_widget, "Kamera")
        
        # Postür ayarları sekmesi
        self.create_posture_tab()
        self.tab_widget.addTab(self.posture_widget, "Postür")
        
        # Uyarı ayarları sekmesi
        self.create_alerts_tab()
        self.tab_widget.addTab(self.alerts_widget, "Uyarılar")
        
        # Görünüm ayarları sekmesi
        self.create_appearance_tab()
        self.tab_widget.addTab(self.appearance_widget, "Görünüm")
        
        layout.addWidget(self.tab_widget)
        
        # Alt butonlar
        self.create_bottom_buttons(layout)
    
    def create_general_tab(self):
        """Genel ayarlar sekmesi"""
        self.general_widget = QWidget()
        layout = QVBoxLayout(self.general_widget)
        
        # Başlatma ayarları
        startup_group = QGroupBox("Başlatma")
        startup_layout = QFormLayout(startup_group)
        
        self.auto_start_cb = QCheckBox("Windows başlangıcında otomatik başlat")
        startup_layout.addRow(self.auto_start_cb)
        
        self.start_minimized_cb = QCheckBox("Minimize edilmiş olarak başlat")
        startup_layout.addRow(self.start_minimized_cb)
        
        self.auto_monitoring_cb = QCheckBox("Başlangıçta izlemeyi otomatik başlat")
        startup_layout.addRow(self.auto_monitoring_cb)
        
        layout.addWidget(startup_group)
        
        # Veri ayarları
        data_group = QGroupBox("Veri Yönetimi")
        data_layout = QFormLayout(data_group)
        
        self.data_retention_spin = QSpinBox()
        self.data_retention_spin.setRange(7, 365)
        self.data_retention_spin.setSuffix(" gün")
        data_layout.addRow("Veri saklama süresi:", self.data_retention_spin)
        
        self.backup_enabled_cb = QCheckBox("Otomatik yedekleme")        
        data_layout.addRow(self.backup_enabled_cb)
        
        backup_path_layout = QHBoxLayout()
        self.backup_path_edit = QLineEdit()
        backup_browse_btn = QPushButton("Gözat...")
        backup_browse_btn.clicked.connect(self.browse_backup_path)
        backup_path_layout.addWidget(self.backup_path_edit)
        backup_path_layout.addWidget(backup_browse_btn)
        data_layout.addRow("Yedekleme klasörü:", backup_path_layout)
        
        layout.addWidget(data_group)
        
        # Performans ayarları
        performance_group = QGroupBox("Performans")
        performance_layout = QFormLayout(performance_group)
        
        self.update_interval_spin = QDoubleSpinBox()
        self.update_interval_spin.setRange(0.1, 2.0)
        self.update_interval_spin.setSingleStep(0.1)
        self.update_interval_spin.setSuffix(" saniye")
        performance_layout.addRow("Güncelleme aralığı:", self.update_interval_spin)
        
        self.use_gpu_cb = QCheckBox("GPU kullan (varsa)")
        performance_layout.addRow(self.use_gpu_cb)
        
        layout.addWidget(performance_group)
        
        layout.addStretch()
    
    def create_camera_tab(self):
        """Kamera ayarları sekmesi"""
        self.camera_widget = QWidget()
        layout = QVBoxLayout(self.camera_widget)
        
        # Kamera seçimi
        camera_group = QGroupBox("Kamera Seçimi")
        camera_layout = QFormLayout(camera_group)
        
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Varsayılan Kamera (0)", "USB Kamera (1)", "Harici Kamera (2)"])
        camera_layout.addRow("Kamera:", self.camera_combo)
        
        test_camera_btn = QPushButton("Kamerayı Test Et")
        test_camera_btn.clicked.connect(self.test_camera)
        camera_layout.addRow(test_camera_btn)
        
        layout.addWidget(camera_group)
        
        # Görüntü kalitesi
        quality_group = QGroupBox("Görüntü Kalitesi")
        quality_layout = QFormLayout(quality_group)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["320x240", "640x480", "800x600", "1024x768"])
        quality_layout.addRow("Çözünürlük:", self.resolution_combo)
        
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(10, 60)
        self.fps_spin.setSuffix(" FPS")
        quality_layout.addRow("Kare hızı:", self.fps_spin)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        quality_layout.addRow("Parlaklık:", self.brightness_slider)
        
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(0, 100)
        quality_layout.addRow("Kontrast:", self.contrast_slider)
        
        layout.addWidget(quality_group)
        
        # MediaPipe ayarları
        mediapipe_group = QGroupBox("MediaPipe Ayarları")
        mediapipe_layout = QFormLayout(mediapipe_group)
        
        self.detection_confidence_slider = QSlider(Qt.Horizontal)
        self.detection_confidence_slider.setRange(10, 100)
        self.detection_confidence_label = QLabel("50%")
        detection_layout = QHBoxLayout()
        detection_layout.addWidget(self.detection_confidence_slider)
        detection_layout.addWidget(self.detection_confidence_label)
        mediapipe_layout.addRow("Tespit güveni:", detection_layout)
        
        self.tracking_confidence_slider = QSlider(Qt.Horizontal)
        self.tracking_confidence_slider.setRange(10, 100)
        self.tracking_confidence_label = QLabel("50%")
        tracking_layout = QHBoxLayout()
        tracking_layout.addWidget(self.tracking_confidence_slider)
        tracking_layout.addWidget(self.tracking_confidence_label)
        mediapipe_layout.addRow("İzleme güveni:", tracking_layout)
        
        # Slider değer güncellemeleri
        self.detection_confidence_slider.valueChanged.connect(
            lambda v: self.detection_confidence_label.setText(f"{v}%")
        )
        self.tracking_confidence_slider.valueChanged.connect(
            lambda v: self.tracking_confidence_label.setText(f"{v}%")
        )
        
        layout.addWidget(mediapipe_group)
        
        layout.addStretch()
    
    def create_posture_tab(self):
        """Postür ayarları sekmesi"""
        self.posture_widget = QWidget()
        layout = QVBoxLayout(self.posture_widget)
        
        # Postür eşikleri
        thresholds_group = QGroupBox("Postür Eşikleri")
        thresholds_layout = QFormLayout(thresholds_group)
        
        self.head_forward_spin = QDoubleSpinBox()
        self.head_forward_spin.setRange(5.0, 30.0)
        self.head_forward_spin.setSingleStep(0.5)
        self.head_forward_spin.setSuffix("°")
        thresholds_layout.addRow("Kafa öne eğimi eşiği:", self.head_forward_spin)
        
        self.shoulder_slope_spin = QDoubleSpinBox()
        self.shoulder_slope_spin.setRange(3.0, 20.0)
        self.shoulder_slope_spin.setSingleStep(0.5)
        self.shoulder_slope_spin.setSuffix("°")
        thresholds_layout.addRow("Omuz eğimi eşiği:", self.shoulder_slope_spin)
        
        self.neck_angle_spin = QDoubleSpinBox()
        self.neck_angle_spin.setRange(10.0, 40.0)
        self.neck_angle_spin.setSingleStep(0.5)
        self.neck_angle_spin.setSuffix("°")
        thresholds_layout.addRow("Boyun açısı eşiği:", self.neck_angle_spin)
        
        self.back_straightness_spin = QDoubleSpinBox()
        self.back_straightness_spin.setRange(5.0, 25.0)
        self.back_straightness_spin.setSingleStep(0.5)
        self.back_straightness_spin.setSuffix("°")
        thresholds_layout.addRow("Sırt düzlüğü eşiği:", self.back_straightness_spin)
        
        layout.addWidget(thresholds_group)
        
        # Postür değerlendirme
        evaluation_group = QGroupBox("Değerlendirme")
        evaluation_layout = QFormLayout(evaluation_group)
        
        self.poor_posture_threshold_slider = QSlider(Qt.Horizontal)
        self.poor_posture_threshold_slider.setRange(30, 80)
        self.poor_posture_threshold_label = QLabel("70%")
        posture_layout = QHBoxLayout()
        posture_layout.addWidget(self.poor_posture_threshold_slider)
        posture_layout.addWidget(self.poor_posture_threshold_label)
        evaluation_layout.addRow("Kötü postür eşiği:", posture_layout)
        
        self.poor_posture_threshold_slider.valueChanged.connect(
            lambda v: self.poor_posture_threshold_label.setText(f"{v}%")
        )
        
        self.smoothing_enabled_cb = QCheckBox("Veri yumuşatma kullan")
        evaluation_layout.addRow(self.smoothing_enabled_cb)
        
        self.history_size_spin = QSpinBox()
        self.history_size_spin.setRange(3, 10)
        evaluation_layout.addRow("Yumuşatma penceresi:", self.history_size_spin)
        
        layout.addWidget(evaluation_group)
        
        # Kalibrasyon
        calibration_group = QGroupBox("Kalibrasyon")
        calibration_layout = QVBoxLayout(calibration_group)
        
        calibrate_btn = QPushButton("Postür Kalibrasyonu Yap")
        calibrate_btn.clicked.connect(self.calibrate_posture)
        calibration_layout.addWidget(calibrate_btn)
        
        reset_calibration_btn = QPushButton("Kalibrasyonu Sıfırla")
        reset_calibration_btn.clicked.connect(self.reset_calibration)
        calibration_layout.addWidget(reset_calibration_btn)
        
        layout.addWidget(calibration_group)
        
        layout.addStretch()
    
    def create_alerts_tab(self):
        """Uyarı ayarları sekmesi"""
        self.alerts_widget = QWidget()
        layout = QVBoxLayout(self.alerts_widget)
        
        # Uyarı türleri
        alert_types_group = QGroupBox("Uyarı Türleri")
        alert_types_layout = QFormLayout(alert_types_group)
        
        self.visual_alerts_cb = QCheckBox("Görsel uyarılar")
        alert_types_layout.addRow(self.visual_alerts_cb)
        
        self.sound_alerts_cb = QCheckBox("Sesli uyarılar")
        alert_types_layout.addRow(self.sound_alerts_cb)
        
        self.system_notifications_cb = QCheckBox("Sistem bildirimleri")
        alert_types_layout.addRow(self.system_notifications_cb)
        
        layout.addWidget(alert_types_group)
        
        # Uyarı zamanlaması
        timing_group = QGroupBox("Uyarı Zamanlaması")
        timing_layout = QFormLayout(timing_group)
        
        self.alert_cooldown_spin = QSpinBox()
        self.alert_cooldown_spin.setRange(5, 300)
        self.alert_cooldown_spin.setSuffix(" saniye")
        timing_layout.addRow("Uyarı aralığı:", self.alert_cooldown_spin)
        
        self.persistent_alerts_cb = QCheckBox("Kalıcı uyarılar (manuel kapatma)")
        timing_layout.addRow(self.persistent_alerts_cb)
        
        layout.addWidget(timing_group)
        
        # Ses ayarları
        sound_group = QGroupBox("Ses Ayarları")
        sound_layout = QFormLayout(sound_group)
        
        self.sound_volume_slider = QSlider(Qt.Horizontal)
        self.sound_volume_slider.setRange(0, 100)
        self.sound_volume_label = QLabel("70%")
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.sound_volume_slider)
        volume_layout.addWidget(self.sound_volume_label)
        sound_layout.addRow("Ses seviyesi:", volume_layout)
        
        self.sound_volume_slider.valueChanged.connect(
            lambda v: self.sound_volume_label.setText(f"{v}%")
        )
        
        sound_file_layout = QHBoxLayout()
        self.sound_file_edit = QLineEdit()
        sound_browse_btn = QPushButton("Gözat...")
        sound_browse_btn.clicked.connect(self.browse_sound_file)
        sound_file_layout.addWidget(self.sound_file_edit)
        sound_file_layout.addWidget(sound_browse_btn)
        sound_layout.addRow("Uyarı sesi:", sound_file_layout)
        
        test_sound_btn = QPushButton("Sesi Test Et")
        test_sound_btn.clicked.connect(self.test_sound)
        sound_layout.addRow(test_sound_btn)
        
        layout.addWidget(sound_group)
        
        layout.addStretch()
    
    def create_appearance_tab(self):
        """Görünüm ayarları sekmesi"""
        self.appearance_widget = QWidget()
        layout = QVBoxLayout(self.appearance_widget)
        
        # Tema
        theme_group = QGroupBox("Tema")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık", "Koyu", "Sistem"])
        theme_layout.addRow("Tema:", self.theme_combo)
        
        layout.addWidget(theme_group)
        
        # Pencere ayarları
        window_group = QGroupBox("Pencere")
        window_layout = QFormLayout(window_group)
        
        self.always_on_top_cb = QCheckBox("Her zaman üstte tut")
        window_layout.addRow(self.always_on_top_cb)
        
        self.minimize_to_tray_cb = QCheckBox("Sistem tepsisine küçült")
        window_layout.addRow(self.minimize_to_tray_cb)
        
        self.close_to_tray_cb = QCheckBox("Kapatırken sistem tepsisine gizle")
        window_layout.addRow(self.close_to_tray_cb)
        
        layout.addWidget(window_group)
        
        # Gösterim ayarları
        display_group = QGroupBox("Gösterim")
        display_layout = QFormLayout(display_group)
        
        self.show_pose_lines_cb = QCheckBox("Postür çizgilerini göster")
        display_layout.addRow(self.show_pose_lines_cb)
        
        self.show_score_overlay_cb = QCheckBox("Skor göstergesini göster")
        display_layout.addRow(self.show_score_overlay_cb)
        
        self.animation_enabled_cb = QCheckBox("Animasyonları etkinleştir")
        display_layout.addRow(self.animation_enabled_cb)
        
        layout.addWidget(display_group)
        
        layout.addStretch()
    
    def create_bottom_buttons(self, parent_layout):
        """Alt butonları oluştur"""
        buttons_layout = QHBoxLayout()
        
        # Varsayılana sıfırla
        reset_btn = QPushButton("Varsayılana Sıfırla")
        reset_btn.clicked.connect(self.reset_to_defaults)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        
        # İptal
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        # Tamam
        ok_btn = QPushButton("Tamam")
        ok_btn.clicked.connect(self.accept_settings)
        ok_btn.setDefault(True)
        buttons_layout.addWidget(ok_btn)
        
        parent_layout.addLayout(buttons_layout)
    
    def load_current_settings(self):
        """Mevcut ayarları yükle"""
        # Varsayılan ayarlar
        settings = {
            # Genel
            "auto_start": False,
            "start_minimized": False,
            "auto_monitoring": False,
            "data_retention_days": 30,
            "backup_enabled": True,
            "backup_path": os.path.join(os.path.expanduser("~"), "PostureFix_Backup"),
            "update_interval": 0.5,
            "use_gpu": False,
            
            # Kamera
            "camera_index": 0,
            "resolution": "640x480",
            "fps": 30,
            "brightness": 50,
            "contrast": 50,
            "detection_confidence": 50,
            "tracking_confidence": 50,
            
            # Postür
            "head_forward_threshold": 15.0,
            "shoulder_slope_threshold": 10.0,
            "neck_angle_threshold": 20.0,
            "back_straightness_threshold": 15.0,
            "poor_posture_threshold": 70,
            "smoothing_enabled": True,
            "history_size": 5,
            
            # Uyarılar
            "visual_alerts": True,
            "sound_alerts": True,
            "system_notifications": True,
            "alert_cooldown": 10,
            "persistent_alerts": False,
            "sound_volume": 70,
            "sound_file": "assets/sounds/alert.wav",
            
            # Görünüm
            "theme": "Açık",
            "always_on_top": False,
            "minimize_to_tray": True,
            "close_to_tray": True,
            "show_pose_lines": True,
            "show_score_overlay": True,
            "animation_enabled": True
        }
        
        # Kayıtlı ayarları yükle (varsa)
        settings_file = os.path.join(self.config.DATA_DIR, "settings.json")
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    settings.update(saved_settings)
            except Exception as e:
                self.logger.error(f"Ayarlar yüklenirken hata: {str(e)}")
        
        return settings
    
    def load_settings_to_ui(self):
        """Ayarları UI'ye yükle"""
        try:
            # Genel
            self.auto_start_cb.setChecked(self.settings["auto_start"])
            self.start_minimized_cb.setChecked(self.settings["start_minimized"])
            self.auto_monitoring_cb.setChecked(self.settings["auto_monitoring"])
            self.data_retention_spin.setValue(self.settings["data_retention_days"])
            self.backup_enabled_cb.setChecked(self.settings["backup_enabled"])
            self.backup_path_edit.setText(self.settings["backup_path"])
            self.update_interval_spin.setValue(self.settings["update_interval"])
            self.use_gpu_cb.setChecked(self.settings["use_gpu"])
            
            # Kamera
            self.camera_combo.setCurrentIndex(self.settings["camera_index"])
            resolution_index = self.resolution_combo.findText(self.settings["resolution"])
            if resolution_index >= 0:
                self.resolution_combo.setCurrentIndex(resolution_index)
            self.fps_spin.setValue(self.settings["fps"])
            self.brightness_slider.setValue(self.settings["brightness"])
            self.contrast_slider.setValue(self.settings["contrast"])
            self.detection_confidence_slider.setValue(self.settings["detection_confidence"])
            self.tracking_confidence_slider.setValue(self.settings["tracking_confidence"])
            
            # Postür
            self.head_forward_spin.setValue(self.settings["head_forward_threshold"])
            self.shoulder_slope_spin.setValue(self.settings["shoulder_slope_threshold"])
            self.neck_angle_spin.setValue(self.settings["neck_angle_threshold"])
            self.back_straightness_spin.setValue(self.settings["back_straightness_threshold"])
            self.poor_posture_threshold_slider.setValue(self.settings["poor_posture_threshold"])
            self.smoothing_enabled_cb.setChecked(self.settings["smoothing_enabled"])
            self.history_size_spin.setValue(self.settings["history_size"])
            
            # Uyarılar
            self.visual_alerts_cb.setChecked(self.settings["visual_alerts"])
            self.sound_alerts_cb.setChecked(self.settings["sound_alerts"])
            self.system_notifications_cb.setChecked(self.settings["system_notifications"])
            self.alert_cooldown_spin.setValue(self.settings["alert_cooldown"])
            self.persistent_alerts_cb.setChecked(self.settings["persistent_alerts"])
            self.sound_volume_slider.setValue(self.settings["sound_volume"])
            self.sound_file_edit.setText(self.settings["sound_file"])
            
            # Görünüm
            theme_index = self.theme_combo.findText(self.settings["theme"])
            if theme_index >= 0:
                self.theme_combo.setCurrentIndex(theme_index)
            self.always_on_top_cb.setChecked(self.settings["always_on_top"])
            self.minimize_to_tray_cb.setChecked(self.settings["minimize_to_tray"])
            self.close_to_tray_cb.setChecked(self.settings["close_to_tray"])
            self.show_pose_lines_cb.setChecked(self.settings["show_pose_lines"])
            self.show_score_overlay_cb.setChecked(self.settings["show_score_overlay"])
            self.animation_enabled_cb.setChecked(self.settings["animation_enabled"])
            
        except Exception as e:
            self.logger.error(f"Ayarları UI'ye yüklerken hata: {str(e)}")
    
    def get_settings(self):
        """UI'den ayarları al"""
        settings = {}
        
        try:
            # Genel
            settings["auto_start"] = self.auto_start_cb.isChecked()
            settings["start_minimized"] = self.start_minimized_cb.isChecked()
            settings["auto_monitoring"] = self.auto_monitoring_cb.isChecked()
            settings["data_retention_days"] = self.data_retention_spin.value()
            settings["backup_enabled"] = self.backup_enabled_cb.isChecked()
            settings["backup_path"] = self.backup_path_edit.text()
            settings["update_interval"] = self.update_interval_spin.value()
            settings["use_gpu"] = self.use_gpu_cb.isChecked()
            
            # Kamera
            settings["camera_index"] = self.camera_combo.currentIndex()
            settings["resolution"] = self.resolution_combo.currentText()
            settings["fps"] = self.fps_spin.value()
            settings["brightness"] = self.brightness_slider.value()
            settings["contrast"] = self.contrast_slider.value()
            settings["detection_confidence"] = self.detection_confidence_slider.value()
            settings["tracking_confidence"] = self.tracking_confidence_slider.value()
            
            # Postür
            settings["head_forward_threshold"] = self.head_forward_spin.value()
            settings["shoulder_slope_threshold"] = self.shoulder_slope_spin.value()
            settings["neck_angle_threshold"] = self.neck_angle_spin.value()
            settings["back_straightness_threshold"] = self.back_straightness_spin.value()
            settings["poor_posture_threshold"] = self.poor_posture_threshold_slider.value()
            settings["smoothing_enabled"] = self.smoothing_enabled_cb.isChecked()
            settings["history_size"] = self.history_size_spin.value()
            
            # Uyarılar
            settings["visual_alerts"] = self.visual_alerts_cb.isChecked()
            settings["sound_alerts"] = self.sound_alerts_cb.isChecked()
            settings["system_notifications"] = self.system_notifications_cb.isChecked()
            settings["alert_cooldown"] = self.alert_cooldown_spin.value()
            settings["persistent_alerts"] = self.persistent_alerts_cb.isChecked()
            settings["sound_volume"] = self.sound_volume_slider.value()
            settings["sound_file"] = self.sound_file_edit.text()
            
            # Görünüm
            settings["theme"] = self.theme_combo.currentText()
            settings["always_on_top"] = self.always_on_top_cb.isChecked()
            settings["minimize_to_tray"] = self.minimize_to_tray_cb.isChecked()
            settings["close_to_tray"] = self.close_to_tray_cb.isChecked()
            settings["show_pose_lines"] = self.show_pose_lines_cb.isChecked()
            settings["show_score_overlay"] = self.show_score_overlay_cb.isChecked()
            settings["animation_enabled"] = self.animation_enabled_cb.isChecked()
            
        except Exception as e:
            self.logger.error(f"Ayarları UI'den alırken hata: {str(e)}")
        
        return settings
    
    def save_settings(self, settings):
        """Ayarları kaydet"""
        settings_file = os.path.join(self.config.DATA_DIR, "settings.json")
        try:
            os.makedirs(os.path.dirname(settings_file), exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.logger.info("Ayarlar kaydedildi")
        except Exception as e:
            self.logger.error(f"Ayarlar kaydedilirken hata: {str(e)}")
    
    def accept_settings(self):
        """Ayarları kabul et"""
        self.settings = self.get_settings()
        self.save_settings(self.settings)
        self.accept()
    
    def reset_to_defaults(self):
        """Varsayılan ayarlara sıfırla"""
        reply = QMessageBox.question(
            self, 
            "Ayarları Sıfırla", 
            "Tüm ayarlar varsayılan değerlere sıfırlanacak. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.settings = self.load_current_settings()  # Varsayılan ayarları yükle
            self.load_settings_to_ui()
    
    def browse_backup_path(self):
        """Yedekleme klasörü seç"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Yedekleme Klasörü Seç",
            self.backup_path_edit.text()
        )
        if folder:
            self.backup_path_edit.setText(folder)
    
    def browse_sound_file(self):
        """Ses dosyası seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ses Dosyası Seç",
            self.sound_file_edit.text(),
            "Ses Dosyaları (*.wav *.mp3 *.ogg);;Tüm Dosyalar (*)"
        )
        if file_path:
            self.sound_file_edit.setText(file_path)
    
    def test_camera(self):
        """Kamerayı test et"""
        QMessageBox.information(self, "Kamera Testi", "Kamera test fonksiyonu henüz implementasyonda...")
    
    def test_sound(self):
        """Sesi test et"""
        QMessageBox.information(self, "Ses Testi", "Ses test fonksiyonu henüz implementasyonda...")
    
    def calibrate_posture(self):
        """Postür kalibrasyonu"""
        QMessageBox.information(self, "Kalibrasyon", "Postür kalibrasyon fonksiyonu henüz implementasyonda...")
    
    def reset_calibration(self):
        """Kalibrasyonu sıfırla"""
        QMessageBox.information(self, "Kalibrasyon Sıfırlama", "Kalibrasyon sıfırlandı.")
