"""
PostureFix - Logging Yapılandırması
Uygulama için merkezi logging sistemi
"""

import logging
import logging.handlers
import os
from datetime import datetime
from config import AppConfig

def setup_logger(name: str = None, level: str = "INFO") -> logging.Logger:
    """
    Merkezi logger kurulumu
    
    Args:
        name: Logger adı (None ise root logger)
        level: Log seviyesi (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Yapılandırılmış logger örneği
    """
    
    config = AppConfig()
    
    # Logger oluştur
    logger = logging.getLogger(name)
    
    # Eğer zaten handler'lar varsa, tekrar ekleme
    if logger.handlers:
        return logger
    
    # Log seviyesi ayarla
    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    logger.setLevel(log_levels.get(level.upper(), logging.INFO))
    
    # Log formatı
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Konsol handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Dosya handler
    try:
        # Log dizinini oluştur
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        
        # Ana log dosyası
        log_file = os.path.join(config.LOGS_DIR, "posturefix.log")
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Hata log dosyası
        error_log_file = os.path.join(config.LOGS_DIR, "errors.log")
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
    except Exception as e:
        # Dosya handler'ı eklenemezse sadece konsola log
        logger.warning(f"Dosya logger kurulamadı: {str(e)}")
    
    # İlk log mesajı
    logger.info(f"Logger başlatıldı - {config.APP_NAME} v{config.VERSION}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Belirli bir modül için logger al
    
    Args:
        name: Logger adı (genellikle __name__)
    
    Returns:
        Logger örneği
    """
    return logging.getLogger(name)

class PostureFixLogger:
    """PostureFix özel logger sınıfı"""
    
    def __init__(self, name: str):
        self.logger = setup_logger(name)
        self.config = AppConfig()
    
    def log_posture_data(self, posture_data: dict, score: float):
        """Postür verilerini logla"""
        self.logger.debug(f"Postür verisi - Skor: {score:.2f}, Veri: {posture_data}")
    
    def log_alert(self, alert_type: str, message: str):
        """Uyarıları logla"""
        self.logger.warning(f"Uyarı [{alert_type}]: {message}")
    
    def log_session_start(self, session_id: str):
        """Oturum başlangıcını logla"""
        self.logger.info(f"Yeni oturum başlatıldı: {session_id}")
    
    def log_session_end(self, session_id: str, duration: float, avg_score: float):
        """Oturum sonunu logla"""
        self.logger.info(f"Oturum sonlandı: {session_id}, Süre: {duration:.1f}dk, Ortalama Skor: {avg_score:.2f}")
    
    def log_exercise_start(self, exercise_name: str):
        """Egzersiz başlangıcını logla"""
        self.logger.info(f"Egzersiz başlatıldı: {exercise_name}")
    
    def log_exercise_complete(self, exercise_name: str, duration: float):
        """Egzersiz tamamlanmasını logla"""
        self.logger.info(f"Egzersiz tamamlandı: {exercise_name}, Süre: {duration:.1f}dk")
    
    def log_settings_change(self, setting_name: str, old_value, new_value):
        """Ayar değişikliklerini logla"""
        self.logger.info(f"Ayar değişti - {setting_name}: {old_value} -> {new_value}")
    
    def log_error(self, error_type: str, error_message: str, context: str = None):
        """Hataları logla"""
        if context:
            self.logger.error(f"Hata [{error_type}] - {context}: {error_message}")
        else:
            self.logger.error(f"Hata [{error_type}]: {error_message}")
    
    def log_performance(self, operation: str, duration: float):
        """Performans metriklerini logla"""
        if duration > 1.0:  # 1 saniyeden uzun işlemler
            self.logger.warning(f"Yavaş işlem - {operation}: {duration:.2f}s")
        else:
            self.logger.debug(f"İşlem - {operation}: {duration:.3f}s")

# Özel log decorator'ı
def log_function_call(logger_name: str = None):
    """Fonksiyon çağrılarını loglayan decorator"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name or func.__module__)
            
            start_time = datetime.now()
            logger.debug(f"Fonksiyon çağrısı: {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                logger.debug(f"Fonksiyon tamamlandı: {func.__name__} ({duration:.3f}s)")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                logger.error(f"Fonksiyon hatası: {func.__name__} ({duration:.3f}s) - {str(e)}")
                raise
        
        return wrapper
    return decorator

# Uygulama başlangıcında çağrılacak
def initialize_logging():
    """Logging sistemini başlat"""
    try:
        # Ana logger'ı kur
        main_logger = setup_logger("posturefix")
        
        # Uygulama başlangıç bilgilerini logla
        main_logger.info("=" * 50)
        main_logger.info("PostureFix Uygulaması Başlatılıyor")
        main_logger.info(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        main_logger.info(f"Python Sürümü: {__import__('sys').version}")
        main_logger.info("=" * 50)
        
        return main_logger
        
    except Exception as e:
        print(f"Logging başlatma hatası: {str(e)}")
        return None

# Uygulama kapatılırken çağrılacak
def cleanup_logging():
    """Logging kaynaklarını temizle"""
    try:
        logger = get_logger("posturefix")
        logger.info("=" * 50)
        logger.info("PostureFix Uygulaması Kapatılıyor")
        logger.info(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
        # Tüm handler'ları kapat
        for handler in logging.root.handlers[:]:
            handler.close()
            logging.root.removeHandler(handler)
            
    except Exception as e:
        print(f"Logging temizleme hatası: {str(e)}")

# Test fonksiyonu
def test_logging():
    """Logging sistemini test et"""
    logger = setup_logger("test")
    
    logger.debug("Bu bir debug mesajıdır")
    logger.info("Bu bir info mesajıdır")
    logger.warning("Bu bir warning mesajıdır")
    logger.error("Bu bir error mesajıdır")
    logger.critical("Bu bir critical mesajıdır")
    
    # PostureFix logger test
    pf_logger = PostureFixLogger("test")
    pf_logger.log_posture_data({"head_forward": 15.5}, 0.75)
    pf_logger.log_alert("POSTURE", "Kötü postür tespit edildi")
    pf_logger.log_session_start("test_session_123")

if __name__ == "__main__":
    test_logging()
