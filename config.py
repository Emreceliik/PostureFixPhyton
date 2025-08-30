"""
PostureFix - Yapılandırma Dosyası
Bu dosya uygulamanın genel ayarlarını içerir.
"""

import os
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class AppConfig:
    """Ana uygulama yapılandırması"""
    
    # Uygulama Bilgileri
    APP_NAME: str = "PostureFix"
    VERSION: str = "1.0.0"
    AUTHOR: str = "PostureFix Team"
    
    # Pencere Ayarları
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    MIN_WINDOW_WIDTH: int = 800
    MIN_WINDOW_HEIGHT: int = 600
    
    # Kamera Ayarları
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    CAMERA_FPS: int = 30
    
    # Postür Analiz Ayarları
    POSTURE_CHECK_INTERVAL: float = 0.5  # saniye
    POOR_POSTURE_THRESHOLD: float = 0.7   # 0-1 arası
    ALERT_COOLDOWN: int = 10              # saniye
    
    # MediaPipe Ayarları
    MEDIAPIPE_CONFIDENCE: float = 0.5
    MEDIAPIPE_DETECTION_CONFIDENCE: float = 0.5
    MEDIAPIPE_TRACKING_CONFIDENCE: float = 0.5
    
    # Veri Saklama
    DATA_DIR: str = "data"
    MODELS_DIR: str = "models"
    REPORTS_DIR: str = "reports"
    LOGS_DIR: str = "logs"
    
    # Ses Ayarları
    SOUND_ENABLED: bool = True
    SOUND_VOLUME: float = 0.7
    ALERT_SOUND_PATH: str = "assets/sounds/alert.wav"
    
    # Tema Ayarları
    DEFAULT_THEME: str = "light"  # light veya dark
    
    # Model Ayarları
    MODEL_PATH: str = "models/posture_model.onnx"
    USE_GPU: bool = False
    
    # İstatistik Ayarları
    STATS_SAVE_INTERVAL: int = 60  # saniye
    REPORT_DAYS: int = 30
    
    # Egzersiz Ayarları
    EXERCISE_REMINDER_INTERVAL: int = 1800  # 30 dakika
    
    @classmethod
    def create_directories(cls) -> None:
        """Gerekli dizinleri oluştur"""
        directories = [
            cls.DATA_DIR,
            cls.MODELS_DIR,
            cls.REPORTS_DIR,
            cls.LOGS_DIR,
            "assets/sounds",
            "assets/images",
            "assets/exercises"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

# Postür Eşikleri
POSTURE_THRESHOLDS = {
    "head_forward": 15.0,      # derece
    "shoulder_slope": 10.0,     # derece
    "neck_angle": 20.0,         # derece
    "back_straightness": 15.0   # derece
}

# Renk Paleti
COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "success": "#F18F01",
    "warning": "#C73E1D",
    "danger": "#FF6B6B",
    "light": "#F8F9FA",
    "dark": "#212529",
    "good_posture": "#28A745",
    "poor_posture": "#DC3545"
}

# Ses Dosya Yolları
SOUND_FILES = {
    "alert": "assets/sounds/alert.wav",
    "success": "assets/sounds/success.wav",
    "reminder": "assets/sounds/reminder.wav"
}

# Egzersiz Kategorileri
EXERCISE_CATEGORIES = {
    "neck": "Boyun Egzersizleri",
    "shoulder": "Omuz Egzersizleri", 
    "back": "Sırt Egzersizleri",
    "general": "Genel Postür Egzersizleri"
}
