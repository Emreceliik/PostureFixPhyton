"""
PostureFix - Postür Gösterim Widget'ı
Gerçek zamanlı postür durumunu ve uyarıları gösteren widget
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QProgressBar, QFrame, QGridLayout,
                            QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                            QGraphicsLineItem, QGraphicsTextItem)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QPen, QBrush, QPainter
import logging
from datetime import datetime
import math

from config import COLORS, POSTURE_THRESHOLDS

class PostureDisplayWidget(QWidget):
    """Postür durumu gösterim widget'ı"""
    
    # Sinyaller
    alert_acknowledged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        
        # Mevcut postür verileri
        self.current_posture_data = {}
        self.current_score = 0.0
        self.is_alert_active = False
        
        # Animasyon timer'ları
        self.alert_timer = QTimer()
        self.alert_timer.timeout.connect(self.animate_alert)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(100)  # 10 FPS güncelleme
        
        # UI kurulumu
        self.setup_ui()
        
        self.logger.info("PostureDisplayWidget oluşturuldu")
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("Postür Durumu")
        title.setFont(QFont("", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Genel skor göstergesi
        self.create_score_display(layout)
        
        # Detaylı postür metrikleri
        self.create_metrics_display(layout)
        
        # Uyarı paneli
        self.create_alert_panel(layout)
        
        # Durum göstergesi
        self.create_status_display(layout)
    
    def create_score_display(self, parent_layout):
        """Genel skor göstergesini oluştur"""
        score_frame = QFrame()
        score_frame.setFrameStyle(QFrame.StyledPanel)
        score_frame.setMaximumHeight(120)
        
        layout = QVBoxLayout(score_frame)
        
        # Skor etiketi
        self.score_label = QLabel("Postür Skoru")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setFont(QFont("", 12))
        layout.addWidget(self.score_label)
        
        # Skor progress bar
        self.score_progress = QProgressBar()
        self.score_progress.setRange(0, 100)
        self.score_progress.setValue(0)
        self.score_progress.setTextVisible(True)
        self.score_progress.setFormat("%v%")
        layout.addWidget(self.score_progress)
        
        # Skor değeri
        self.score_value_label = QLabel("0%")
        self.score_value_label.setAlignment(Qt.AlignCenter)
        self.score_value_label.setFont(QFont("", 20, QFont.Bold))
        layout.addWidget(self.score_value_label)
        
        parent_layout.addWidget(score_frame)
    
    def create_metrics_display(self, parent_layout):
        """Detaylı metrikleri oluştur"""
        metrics_frame = QFrame()
        metrics_frame.setFrameStyle(QFrame.StyledPanel)
        
        layout = QGridLayout(metrics_frame)
        
        # Metrik başlığı
        metrics_title = QLabel("Postür Metrikleri")
        metrics_title.setFont(QFont("", 12, QFont.Bold))
        metrics_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(metrics_title, 0, 0, 1, 2)
        
        # Metrikler
        self.metrics = {}
        metrics_info = [
            ("head_forward", "Kafa Öne Eğimi", "°"),
            ("neck_angle", "Boyun Açısı", "°"),
            ("shoulder_slope", "Omuz Eğimi", "°"),
            ("back_straightness", "Sırt Düzlüğü", "°")
        ]
        
        row = 1
        for key, name, unit in metrics_info:
            # Metrik adı
            name_label = QLabel(name + ":")
            name_label.setFont(QFont("", 10))
            layout.addWidget(name_label, row, 0)
            
            # Metrik değeri
            value_label = QLabel(f"0{unit}")
            value_label.setFont(QFont("", 10, QFont.Bold))
            value_label.setAlignment(Qt.AlignRight)
            layout.addWidget(value_label, row, 1)
            
            self.metrics[key] = {
                'name_label': name_label,
                'value_label': value_label,
                'unit': unit
            }
            
            row += 1
        
        parent_layout.addWidget(metrics_frame)
    
    def create_alert_panel(self, parent_layout):
        """Uyarı panelini oluştur"""
        self.alert_frame = QFrame()
        self.alert_frame.setFrameStyle(QFrame.StyledPanel)
        self.alert_frame.setMaximumHeight(100)
        self.alert_frame.setVisible(False)
        
        layout = QVBoxLayout(self.alert_frame)
        
        # Uyarı ikonu ve metni
        alert_header = QHBoxLayout()
        
        self.alert_icon = QLabel("⚠️")
        self.alert_icon.setFont(QFont("", 20))
        alert_header.addWidget(self.alert_icon)
        
        self.alert_text = QLabel("Postür Uyarısı")
        self.alert_text.setFont(QFont("", 12, QFont.Bold))
        self.alert_text.setWordWrap(True)
        alert_header.addWidget(self.alert_text)
        
        layout.addLayout(alert_header)
        
        # Uyarı butonları
        button_layout = QHBoxLayout()
        
        self.acknowledge_button = QPushButton("Tamam")
        self.acknowledge_button.clicked.connect(self.acknowledge_alert)
        button_layout.addWidget(self.acknowledge_button)
        
        self.snooze_button = QPushButton("Ertele (5dk)")
        self.snooze_button.clicked.connect(self.snooze_alert)
        button_layout.addWidget(self.snooze_button)
        
        layout.addLayout(button_layout)
        
        parent_layout.addWidget(self.alert_frame)
    
    def create_status_display(self, parent_layout):
        """Durum göstergesini oluştur"""
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_frame.setMaximumHeight(80)
        
        layout = QVBoxLayout(status_frame)
        
        # Durum başlığı
        status_title = QLabel("Durum")
        status_title.setFont(QFont("", 12, QFont.Bold))
        status_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_title)
        
        # Durum ikonu ve metni
        status_content = QHBoxLayout()
        
        self.status_icon = QLabel("⭕")
        self.status_icon.setFont(QFont("", 24))
        status_content.addWidget(self.status_icon)
        
        self.status_text = QLabel("Hazır")
        self.status_text.setFont(QFont("", 12))
        self.status_text.setAlignment(Qt.AlignCenter)
        status_content.addWidget(self.status_text)
        
        layout.addLayout(status_content)
        
        # Son güncelleme zamanı
        self.last_update_label = QLabel("Son güncelleme: --:--:--")
        self.last_update_label.setFont(QFont("", 9))
        self.last_update_label.setAlignment(Qt.AlignCenter)
        self.last_update_label.setStyleSheet("color: gray;")
        layout.addWidget(self.last_update_label)
        
        parent_layout.addWidget(status_frame)
    
    def update_posture_data(self, posture_data: dict):
        """Postür verilerini güncelle"""
        try:
            self.current_posture_data = posture_data
            
            # Skor güncelle
            if 'score' in posture_data:
                self.current_score = posture_data['score']
                self.update_score_display()
            
            # Metrikleri güncelle
            self.update_metrics_display()
            
            # Durum güncelle
            self.update_status_display()
            
            # Son güncelleme zamanı
            timestamp = posture_data.get('timestamp', datetime.now())
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, datetime):
                pass
            else:
                timestamp = datetime.now()
            
            self.last_update_label.setText(f"Son güncelleme: {timestamp.strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.logger.error(f"Postür verisi güncelleme hatası: {str(e)}")
    
    def update_score_display(self):
        """Skor göstergesini güncelle"""
        score_percent = int(self.current_score * 100)
        self.score_progress.setValue(score_percent)
        self.score_value_label.setText(f"{score_percent}%")
        
        # Renk güncelle
        if self.current_score >= 0.8:
            color = COLORS["good_posture"]
            status = "Mükemmel"
        elif self.current_score >= 0.6:
            color = COLORS["success"]
            status = "İyi"
        elif self.current_score >= 0.4:
            color = COLORS["warning"]
            status = "Orta"
        else:
            color = COLORS["poor_posture"]
            status = "Kötü"
        
        self.score_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                width: 20px;
            }}
        """)
        
        self.score_value_label.setStyleSheet(f"color: {color};")
    
    def update_metrics_display(self):
        """Metrikleri güncelle"""
        for key, metric_info in self.metrics.items():
            if key in self.current_posture_data:
                value = self.current_posture_data[key]
                unit = metric_info['unit']
                
                # Değeri formatla
                if isinstance(value, (int, float)):
                    formatted_value = f"{value:.1f}{unit}"
                else:
                    formatted_value = f"--{unit}"
                
                metric_info['value_label'].setText(formatted_value)
                
                # Renk kodlaması (eşik değerlerine göre)
                threshold = POSTURE_THRESHOLDS.get(key, float('inf'))
                if isinstance(value, (int, float)):
                    if value <= threshold * 0.5:
                        color = COLORS["good_posture"]
                    elif value <= threshold:
                        color = COLORS["warning"]
                    else:
                        color = COLORS["poor_posture"]
                    
                    metric_info['value_label'].setStyleSheet(f"color: {color};")
    
    def update_status_display(self):
        """Durum göstergesini güncelle"""
        if self.current_score >= 0.7:
            self.status_icon.setText("✅")
            self.status_text.setText("İyi Postür")
            self.status_text.setStyleSheet(f"color: {COLORS['good_posture']};")
        elif self.current_score >= 0.4:
            self.status_icon.setText("⚠️")
            self.status_text.setText("Dikkat Et")
            self.status_text.setStyleSheet(f"color: {COLORS['warning']};")
        else:
            self.status_icon.setText("❌")
            self.status_text.setText("Kötü Postür")
            self.status_text.setStyleSheet(f"color: {COLORS['poor_posture']};")
    
    def show_alert(self, alert_message: str):
        """Uyarı göster"""
        try:
            self.alert_text.setText(alert_message)
            self.alert_frame.setVisible(True)
            self.is_alert_active = True
            
            # Uyarı animasyonu başlat
            self.alert_timer.start(500)  # 0.5 saniyede bir yanıp sönsün
            
            # Uyarı rengi
            self.alert_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['danger']};
                    border: 2px solid {COLORS['warning']};
                    border-radius: 10px;
                    color: white;
                }}
            """)
            
            self.logger.info(f"Uyarı gösterildi: {alert_message}")
            
        except Exception as e:
            self.logger.error(f"Uyarı gösterme hatası: {str(e)}")
    
    def animate_alert(self):
        """Uyarı animasyonu"""
        if not self.is_alert_active:
            self.alert_timer.stop()
            return
        
        # Yanıp sönme efekti
        current_style = self.alert_frame.styleSheet()
        if "background-color: #FF6B6B" in current_style:
            # Kırmızıdan turuncu'ya
            self.alert_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['warning']};
                    border: 2px solid {COLORS['danger']};
                    border-radius: 10px;
                    color: white;
                }}
            """)
        else:
            # Turuncu'dan kırmızı'ya
            self.alert_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['danger']};
                    border: 2px solid {COLORS['warning']};
                    border-radius: 10px;
                    color: white;
                }}
            """)
    
    def acknowledge_alert(self):
        """Uyarıyı onayla"""
        self.hide_alert()
        self.alert_acknowledged.emit()
        self.logger.info("Uyarı onaylandı")
    
    def snooze_alert(self):
        """Uyarıyı ertele"""
        self.hide_alert()
        # 5 dakika sonra tekrar uyarı göstermek için timer ayarla
        QTimer.singleShot(5 * 60 * 1000, self.check_snooze_alert)
        self.logger.info("Uyarı 5 dakika ertelendi")
    
    def check_snooze_alert(self):
        """Ertelenen uyarıyı kontrol et"""
        # Eğer hala kötü postür varsa uyarıyı tekrar göster
        if self.current_score < 0.4:
            self.show_alert("Postür hala kötü - Lütfen duruşunuzu düzeltin!")
    
    def hide_alert(self):
        """Uyarıyı gizle"""
        self.alert_frame.setVisible(False)
        self.is_alert_active = False
        self.alert_timer.stop()
    
    def update_displays(self):
        """Periyodik güncelleme"""
        # Gerekirse ek güncellemeler yapılabilir
        pass
    
    def apply_theme(self, theme_name: str):
        """Tema uygula"""
        if theme_name == "dark":
            # Koyu tema stilleri
            frame_style = """
                QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #555;
                    border-radius: 8px;
                    color: white;
                }
                QLabel {
                    color: white;
                }
            """
        else:
            # Açık tema stilleri
            frame_style = """
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    color: black;
                }
                QLabel {
                    color: black;
                }
            """
        
        # Tüm frame'lere stil uygula
        for widget in self.findChildren(QFrame):
            if widget != self.alert_frame:  # Alert frame'in kendi stili var
                widget.setStyleSheet(frame_style)
