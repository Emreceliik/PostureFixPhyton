"""
PostureFix - Tema Yöneticisi
Uygulama temalarını yöneten sınıf
"""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
import logging

from config import COLORS

class ThemeManager(QObject):
    """Tema yönetimi sınıfı"""
    
    # Sinyaller
    theme_changed = pyqtSignal(str)  # tema_adı
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        self.current_theme = "light"
        
        # Tema tanımları
        self.themes = {
            "light": self.get_light_theme(),
            "dark": self.get_dark_theme()
        }
        
        self.logger.info("ThemeManager oluşturuldu")
    
    def get_light_theme(self):
        """Açık tema stil tanımı"""
        return """
/* Ana Pencere */
QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

/* Butonlar */
QPushButton {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
    color: #333;
}

QPushButton:hover {
    background-color: #f0f0f0;
    border-color: #ccc;
}

QPushButton:pressed {
    background-color: #e0e0e0;
}

QPushButton:disabled {
    background-color: #f9f9f9;
    color: #999;
    border-color: #eee;
}

/* Primary Button */
QPushButton[objectName="primary_button"] {
    background-color: """ + COLORS["primary"] + """;
    color: white;
    border: none;
}

QPushButton[objectName="primary_button"]:hover {
    background-color: #2574a3;
}

QPushButton[objectName="primary_button"]:pressed {
    background-color: #1f5f8b;
}

/* Secondary Button */
QPushButton[objectName="secondary_button"] {
    background-color: """ + COLORS["secondary"] + """;
    color: white;
    border: none;
}

QPushButton[objectName="secondary_button"]:hover {
    background-color: #8b2f5f;
}

/* Settings Button */
QPushButton[objectName="settings_button"] {
    background-color: #6c757d;
    color: white;
    border: none;
}

QPushButton[objectName="settings_button"]:hover {
    background-color: #5a6268;
}

/* Frame'ler */
QFrame {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}

QFrame[frameShape="4"] { /* StyledPanel */
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #ddd;
    border-radius: 6px;
    background-color: #ffffff;
}

QTabBar::tab {
    background-color: #f8f9fa;
    border: 1px solid #ddd;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: """ + COLORS["primary"] + """;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #e9ecef;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #ddd;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
}

QProgressBar::chunk {
    background-color: """ + COLORS["primary"] + """;
    border-radius: 3px;
}

/* Labels */
QLabel {
    color: #333333;
    background-color: transparent;
}

/* List Widget */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 6px;
    alternate-background-color: #f8f9fa;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #eee;
}

QListWidget::item:selected {
    background-color: """ + COLORS["primary"] + """;
    color: white;
}

QListWidget::item:hover {
    background-color: #f0f0f0;
}

/* Combo Box */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 6px 12px;
}

QComboBox:hover {
    border-color: """ + COLORS["primary"] + """;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: url(assets/images/arrow-down.png);
    width: 12px;
    height: 12px;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 6px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: """ + COLORS["primary"] + """;
}

/* Slider */
QSlider::groove:horizontal {
    border: 1px solid #ddd;
    height: 6px;
    background-color: #f8f9fa;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: """ + COLORS["primary"] + """;
    border: 1px solid #ddd;
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background-color: """ + COLORS["primary"] + """;
    border-radius: 3px;
}

/* Check Box */
QCheckBox {
    color: #333333;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #ddd;
    border-radius: 3px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: """ + COLORS["primary"] + """;
    border-color: """ + COLORS["primary"] + """;
}

/* Group Box */
QGroupBox {
    font-weight: bold;
    border: 1px solid #ddd;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 8px 0 8px;
    background-color: #f5f5f5;
}

/* Status Bar */
QStatusBar {
    background-color: #f8f9fa;
    border-top: 1px solid #ddd;
    color: #666;
}

/* Menu Bar */
QMenuBar {
    background-color: #ffffff;
    border-bottom: 1px solid #ddd;
}

QMenuBar::item {
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: """ + COLORS["primary"] + """;
    color: white;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #f8f9fa;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #ccc;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #999;
}

/* Text Edit */
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px;
}

QTextEdit:focus {
    border-color: """ + COLORS["primary"] + """;
}
"""
    
    def get_dark_theme(self):
        """Koyu tema stil tanımı"""
        return """
/* Ana Pencere */
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

/* Butonlar */
QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
    color: #fff;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #666;
}

QPushButton:pressed {
    background-color: #333;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666;
    border-color: #444;
}

/* Primary Button */
QPushButton[objectName="primary_button"] {
    background-color: """ + COLORS["primary"] + """;
    color: white;
    border: none;
}

QPushButton[objectName="primary_button"]:hover {
    background-color: #2574a3;
}

QPushButton[objectName="primary_button"]:pressed {
    background-color: #1f5f8b;
}

/* Secondary Button */
QPushButton[objectName="secondary_button"] {
    background-color: """ + COLORS["secondary"] + """;
    color: white;
    border: none;
}

QPushButton[objectName="secondary_button"]:hover {
    background-color: #8b2f5f;
}

/* Settings Button */
QPushButton[objectName="settings_button"] {
    background-color: #6c757d;
    color: white;
    border: none;
}

QPushButton[objectName="settings_button"]:hover {
    background-color: #5a6268;
}

/* Frame'ler */
QFrame {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 8px;
}

QFrame[frameShape="4"] { /* StyledPanel */
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 8px;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #555;
    border-radius: 6px;
    background-color: #3c3c3c;
}

QTabBar::tab {
    background-color: #2b2b2b;
    border: 1px solid #555;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
    color: #ccc;
}

QTabBar::tab:selected {
    background-color: #3c3c3c;
    color: """ + COLORS["primary"] + """;
    font-weight: bold;
}

QTabBar::tab:hover {
    background-color: #4a4a4a;
    color: #fff;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #555;
    border-radius: 4px;
    text-align: center;
    font-weight: bold;
    background-color: #2b2b2b;
    color: #fff;
}

QProgressBar::chunk {
    background-color: """ + COLORS["primary"] + """;
    border-radius: 3px;
}

/* Labels */
QLabel {
    color: #ffffff;
    background-color: transparent;
}

/* List Widget */
QListWidget {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 6px;
    alternate-background-color: #2b2b2b;
    color: #fff;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #555;
}

QListWidget::item:selected {
    background-color: """ + COLORS["primary"] + """;
    color: white;
}

QListWidget::item:hover {
    background-color: #4a4a4a;
}

/* Combo Box */
QComboBox {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px 12px;
    color: #fff;
}

QComboBox:hover {
    border-color: """ + COLORS["primary"] + """;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #3c3c3c;
    border: 1px solid #555;
    color: #fff;
}

/* Spin Box */
QSpinBox, QDoubleSpinBox {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px;
    color: #fff;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: """ + COLORS["primary"] + """;
}

/* Slider */
QSlider::groove:horizontal {
    border: 1px solid #555;
    height: 6px;
    background-color: #2b2b2b;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background-color: """ + COLORS["primary"] + """;
    border: 1px solid #555;
    width: 18px;
    margin: -6px 0;
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background-color: """ + COLORS["primary"] + """;
    border-radius: 3px;
}

/* Check Box */
QCheckBox {
    color: #ffffff;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #555;
    border-radius: 3px;
    background-color: #3c3c3c;
}

QCheckBox::indicator:checked {
    background-color: """ + COLORS["primary"] + """;
    border-color: """ + COLORS["primary"] + """;
}

/* Group Box */
QGroupBox {
    font-weight: bold;
    border: 1px solid #555;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 12px;
    color: #fff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 8px 0 8px;
    background-color: #2b2b2b;
}

/* Status Bar */
QStatusBar {
    background-color: #2b2b2b;
    border-top: 1px solid #555;
    color: #ccc;
}

/* Menu Bar */
QMenuBar {
    background-color: #3c3c3c;
    border-bottom: 1px solid #555;
    color: #fff;
}

QMenuBar::item {
    padding: 6px 12px;
}

QMenuBar::item:selected {
    background-color: """ + COLORS["primary"] + """;
    color: white;
}

/* Scroll Bar */
QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #555;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #666;
}

/* Text Edit */
QTextEdit {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 8px;
    color: #fff;
}

QTextEdit:focus {
    border-color: """ + COLORS["primary"] + """;
}

/* Line Edit */
QLineEdit {
    background-color: #3c3c3c;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 6px;
    color: #fff;
}

QLineEdit:focus {
    border-color: """ + COLORS["primary"] + """;
}
"""
    
    def get_theme_stylesheet(self, theme_name: str) -> str:
        """Tema stil sayfasını döndür"""
        return self.themes.get(theme_name, self.themes["light"])
    
    def set_theme(self, theme_name: str):
        """Tema ayarla"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name)
            self.logger.info(f"Tema değiştirildi: {theme_name}")
        else:
            self.logger.warning(f"Bilinmeyen tema: {theme_name}")
    
    def get_current_theme(self) -> str:
        """Mevcut tema adını döndür"""
        return self.current_theme
    
    def get_available_themes(self) -> list:
        """Mevcut temaları döndür"""
        return list(self.themes.keys())
    
    def create_custom_palette(self, theme_name: str) -> QPalette:
        """Tema için özel palet oluştur"""
        palette = QPalette()
        
        if theme_name == "dark":
            # Koyu tema renkleri
            palette.setColor(QPalette.Window, QColor(43, 43, 43))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(60, 60, 60))
            palette.setColor(QPalette.AlternateBase, QColor(43, 43, 43))
            palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(60, 60, 60))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        else:
            # Açık tema renkleri (varsayılan)
            palette.setColor(QPalette.Window, QColor(245, 245, 245))
            palette.setColor(QPalette.WindowText, QColor(51, 51, 51))
            palette.setColor(QPalette.Base, QColor(255, 255, 255))
            palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
            palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
            palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
            palette.setColor(QPalette.Text, QColor(51, 51, 51))
            palette.setColor(QPalette.Button, QColor(255, 255, 255))
            palette.setColor(QPalette.ButtonText, QColor(51, 51, 51))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        return palette
