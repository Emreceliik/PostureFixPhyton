"""
PostureFix - Kamera Widget'ı
Kamera görüntüsünü gösteren ve postür çizgilerini ekleyen widget
"""

import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
import logging

class CameraWidget(QWidget):
    """Kamera görüntüsü widget'ı"""
    
    # Sinyaller
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        
        # Durum değişkenleri
        self.is_monitoring = False
        self.current_frame = None
        self.show_pose_lines = True
        
        # UI kurulumu
        self.setup_ui()
        
        # Timer (demo için)
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.update_demo_frame)
        
        self.logger.info("CameraWidget oluşturuldu")
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Başlık
        title = QLabel("Kamera Görüntüsü")
        title.setFont(QFont("", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Kamera frame'i
        self.camera_frame = QFrame()
        self.camera_frame.setFrameStyle(QFrame.StyledPanel)
        self.camera_frame.setMinimumSize(320, 240)
        self.camera_frame.setMaximumSize(640, 480)
        
        # Kamera label
        camera_layout = QVBoxLayout(self.camera_frame)
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                border-radius: 10px;
                color: #888;
                font-size: 14px;
            }
        """)
        self.camera_label.setText("Kamera görüntüsü burada gösterilecek")
        camera_layout.addWidget(self.camera_label)
        
        layout.addWidget(self.camera_frame)
        
        # Kontrol butonları
        controls_layout = QVBoxLayout()
        
        self.pose_lines_button = QPushButton("Postür Çizgilerini Gizle/Göster")
        self.pose_lines_button.setCheckable(True)
        self.pose_lines_button.setChecked(True)
        self.pose_lines_button.clicked.connect(self.toggle_pose_lines)
        controls_layout.addWidget(self.pose_lines_button)
        
        layout.addLayout(controls_layout)
        
        # Durum bilgisi
        self.status_label = QLabel("Kamera kapalı")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: gray; font-size: 12px;")
        layout.addWidget(self.status_label)
    
    def set_monitoring_active(self, active: bool):
        """İzleme durumunu ayarla"""
        self.is_monitoring = active
        
        if active:
            self.status_label.setText("Kamera aktif - İzleme devam ediyor")
            self.status_label.setStyleSheet("color: green; font-size: 12px; font-weight: bold;")
            # Demo timer başlat
            self.demo_timer.start(100)  # 10 FPS
        else:
            self.status_label.setText("Kamera kapalı")
            self.status_label.setStyleSheet("color: gray; font-size: 12px;")
            self.demo_timer.stop()
            self.show_placeholder()
    
    def show_placeholder(self):
        """Placeholder görüntüsü göster"""
        self.camera_label.setText("Kamera görüntüsü burada gösterilecek\\n\\nİzlemeyi başlatmak için\\n'İzlemeyi Başlat' butonuna tıklayın")
        self.camera_label.setPixmap(QPixmap())
    
    def update_demo_frame(self):
        """Demo frame güncelle (gerçek kamera yerine)"""
        # Demo için basit bir görüntü oluştur
        width, height = 320, 240
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Arka plan rengi
        frame[:] = (50, 50, 50)
        
        # Demo postür çizgileri
        if self.show_pose_lines:
            self.draw_demo_pose(frame)
        
        # Zaman damgası
        import time
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(frame, f"Demo Mode - {timestamp}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Frame'i göster
        self.display_frame(frame)
        
        # Sinyal gönder
        self.frame_ready.emit(frame)
    
    def draw_demo_pose(self, frame):
        """Demo postür çizgileri çiz"""
        import time
        
        # Basit animasyon için zaman bazlı hareket
        t = time.time()
        offset_x = int(20 * np.sin(t))
        offset_y = int(10 * np.cos(t * 1.5))
        
        # Merkez noktalar
        center_x, center_y = 160, 120
        
        # Kafa (daire)
        head_center = (center_x + offset_x, center_y - 80 + offset_y)
        cv2.circle(frame, head_center, 25, (0, 255, 255), 2)
        
        # Boyun
        neck_point = (center_x + offset_x, center_y - 50 + offset_y)
        cv2.line(frame, head_center, neck_point, (0, 255, 255), 2)
        
        # Omuzlar
        left_shoulder = (center_x - 40 + offset_x, center_y - 40 + offset_y)
        right_shoulder = (center_x + 40 + offset_x, center_y - 40 + offset_y)
        cv2.line(frame, left_shoulder, right_shoulder, (0, 255, 0), 2)
        cv2.line(frame, neck_point, left_shoulder, (0, 255, 255), 2)
        cv2.line(frame, neck_point, right_shoulder, (0, 255, 255), 2)
        
        # Gövde
        spine_bottom = (center_x + offset_x, center_y + 60 + offset_y)
        cv2.line(frame, neck_point, spine_bottom, (255, 0, 0), 2)
        
        # Kalçalar
        left_hip = (center_x - 25 + offset_x, center_y + 60 + offset_y)
        right_hip = (center_x + 25 + offset_x, center_y + 60 + offset_y)
        cv2.line(frame, left_hip, right_hip, (255, 0, 255), 2)
        
        # Postür durumu göstergesi
        posture_quality = abs(np.sin(t * 0.5))  # 0-1 arası
        if posture_quality > 0.7:
            status_text = "İyi Postür"
            status_color = (0, 255, 0)
        elif posture_quality > 0.4:
            status_text = "Orta Postür"
            status_color = (0, 255, 255)
        else:
            status_text = "Kötü Postür"
            status_color = (0, 0, 255)
        
        cv2.putText(frame, status_text, (10, height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Skor göstergesi
        score = int(posture_quality * 100)
        cv2.putText(frame, f"Skor: {score}%", (10, height - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def display_frame(self, frame):
        """Frame'i widget'ta göster"""
        try:
            # OpenCV BGR'den RGB'ye çevir
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # QImage'e çevir
            height, width, channel = rgb_frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # QPixmap'e çevir ve boyutlandır
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                self.camera_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # Label'da göster
            self.camera_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.logger.error(f"Frame gösterme hatası: {str(e)}")
    
    def toggle_pose_lines(self):
        """Postür çizgilerini aç/kapat"""
        self.show_pose_lines = not self.show_pose_lines
        
        if self.show_pose_lines:
            self.pose_lines_button.setText("Postür Çizgilerini Gizle")
        else:
            self.pose_lines_button.setText("Postür Çizgilerini Göster")
    
    def apply_theme(self, theme_name: str):
        """Tema uygula"""
        if theme_name == "dark":
            self.camera_frame.setStyleSheet("""
                QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #555;
                    border-radius: 10px;
                }
            """)
            self.camera_label.setStyleSheet("""
                QLabel {
                    background-color: #3c3c3c;
                    border: 2px dashed #666;
                    border-radius: 10px;
                    color: #ccc;
                    font-size: 14px;
                }
            """)
        else:
            self.camera_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                }
            """)
            self.camera_label.setStyleSheet("""
                QLabel {
                    background-color: #f0f0f0;
                    border: 2px dashed #ccc;
                    border-radius: 10px;
                    color: #888;
                    font-size: 14px;
                }
            """)
    
    def update_frame_with_pose(self, frame, pose_landmarks=None):
        """Frame'i postür landmark'ları ile güncelle"""
        if pose_landmarks and self.show_pose_lines:
            # Gerçek MediaPipe landmark'ları çiz
            # Bu fonksiyon gerçek implementasyonda MediaPipe çizim fonksiyonları kullanacak
            pass
        
        self.display_frame(frame)
        self.frame_ready.emit(frame)
