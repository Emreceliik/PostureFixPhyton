"""
PostureFix - Egzersizler Widget'ı
Postür düzeltme egzersizlerini gösteren ve yöneten widget
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QGridLayout, QPushButton, QScrollArea,
    QTextEdit, QProgressBar, QListWidget,
    QListWidgetItem, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon, QMovie

import logging
from datetime import datetime, timedelta
import json

from config import EXERCISE_CATEGORIES, COLORS

class ExercisesWidget(QWidget):
    """Egzersizler widget'ı"""
    
    # Sinyaller
    exercise_started = pyqtSignal(str)  # egzersiz_id
    exercise_completed = pyqtSignal(str)  # egzersiz_id
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        
        # Mevcut egzersiz durumu
        self.current_exercise = None
        self.exercise_timer = QTimer()
        self.exercise_timer.timeout.connect(self.update_exercise_progress)
        self.exercise_start_time = None
        self.exercise_duration = 0
        
        # Egzersiz verileri
        self.exercises_data = self.load_exercises_data()
        
        # UI kurulumu
        self.setup_ui()
        
        self.logger.info("ExercisesWidget oluşturuldu")
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık
        title = QLabel("🏃 Postür Egzersizleri")
        title.setFont(QFont("", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Önerilen egzersizler sekmesi
        self.create_recommended_tab()
        self.tab_widget.addTab(self.recommended_widget, "Önerilen")
        
        # Tüm egzersizler sekmesi
        self.create_all_exercises_tab()
        self.tab_widget.addTab(self.all_exercises_widget, "Tüm Egzersizler")
        
        # Egzersiz geçmişi sekmesi
        self.create_history_tab()
        self.tab_widget.addTab(self.history_widget, "Geçmiş")
        
        layout.addWidget(self.tab_widget)
    
    def create_recommended_tab(self):
        """Önerilen egzersizler sekmesi"""
        self.recommended_widget = QWidget()
        layout = QVBoxLayout(self.recommended_widget)
        
        # Mevcut postüre göre öneriler
        recommendations_frame = QFrame()
        recommendations_frame.setFrameStyle(QFrame.StyledPanel)
        
        rec_layout = QVBoxLayout(recommendations_frame)
        
        rec_title = QLabel("Postürünüze Özel Öneriler")
        rec_title.setFont(QFont("", 14, QFont.Bold))
        rec_title.setAlignment(Qt.AlignCenter)
        rec_layout.addWidget(rec_title)
        
        # Önerilen egzersizler listesi
        self.recommended_list = QListWidget()
        self.populate_recommended_exercises()
        rec_layout.addWidget(self.recommended_list)
        
        layout.addWidget(recommendations_frame)
        
        # Hızlı egzersiz butonu
        quick_exercise_btn = QPushButton("⚡ 5 Dakikalık Hızlı Egzersiz")
        quick_exercise_btn.setObjectName("primary_button")
        quick_exercise_btn.setFixedHeight(50)
        quick_exercise_btn.clicked.connect(self.start_quick_exercise)
        layout.addWidget(quick_exercise_btn)
        
        # Mevcut egzersiz paneli
        self.create_current_exercise_panel(layout)
    
    def create_all_exercises_tab(self):
        """Tüm egzersizler sekmesi"""
        self.all_exercises_widget = QWidget()
        layout = QVBoxLayout(self.all_exercises_widget)
        
        # Kategori sekmesi
        self.category_tabs = QTabWidget()
        
        for category_key, category_name in EXERCISE_CATEGORIES.items():
            category_widget = self.create_category_widget(category_key)
            self.category_tabs.addTab(category_widget, category_name)
        
        layout.addWidget(self.category_tabs)
    
    def create_history_tab(self):
        """Egzersiz geçmişi sekmesi"""
        self.history_widget = QWidget()
        layout = QVBoxLayout(self.history_widget)
        
        # İstatistikler
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.StyledPanel)
        stats_frame.setMaximumHeight(100)
        
        stats_layout = QHBoxLayout(stats_frame)
        
        # Bu hafta
        week_stats = self.create_stat_mini_card("Bu Hafta", "12", "egzersiz")
        stats_layout.addWidget(week_stats)
        
        # Bu ay
        month_stats = self.create_stat_mini_card("Bu Ay", "45", "egzersiz")
        stats_layout.addWidget(month_stats)
        
        # Toplam süre
        time_stats = self.create_stat_mini_card("Toplam Süre", "3.2", "saat")
        stats_layout.addWidget(time_stats)
        
        layout.addWidget(stats_frame)
        
        # Geçmiş listesi
        history_list = QListWidget()
        self.populate_exercise_history(history_list)
        layout.addWidget(history_list)
    
    def create_category_widget(self, category_key: str):
        """Kategori widget'ı oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Kategori egzersizleri
        exercises = self.exercises_data.get(category_key, [])
        
        for exercise in exercises:
            exercise_card = self.create_exercise_card(exercise)
            layout.addWidget(exercise_card)
        
        layout.addStretch()
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        
        return scroll
    
    def create_exercise_card(self, exercise_data: dict):
        """Egzersiz kartı oluştur"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setMaximumHeight(150)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Sol taraf - bilgiler
        info_layout = QVBoxLayout()
        
        # Egzersiz adı
        name_label = QLabel(exercise_data.get('name', 'Egzersiz'))
        name_label.setFont(QFont("", 14, QFont.Bold))
        info_layout.addWidget(name_label)
        
        # Açıklama
        desc_label = QLabel(exercise_data.get('description', 'Açıklama yok'))
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: gray;")
        info_layout.addWidget(desc_label)
        
        # Süre ve zorluk
        details_layout = QHBoxLayout()
        
        duration_label = QLabel(f"⏱️ {exercise_data.get('duration', '5')} dk")
        duration_label.setStyleSheet("color: blue;")
        details_layout.addWidget(duration_label)
        
        difficulty = exercise_data.get('difficulty', 'Kolay')
        difficulty_color = {"Kolay": "green", "Orta": "orange", "Zor": "red"}.get(difficulty, "gray")
        difficulty_label = QLabel(f"📊 {difficulty}")
        difficulty_label.setStyleSheet(f"color: {difficulty_color};")
        details_layout.addWidget(difficulty_label)
        
        details_layout.addStretch()
        info_layout.addLayout(details_layout)
        
        layout.addLayout(info_layout)
        
        # Sağ taraf - butonlar
        buttons_layout = QVBoxLayout()
        
        start_btn = QPushButton("Başlat")
        start_btn.setObjectName("primary_button")
        start_btn.clicked.connect(lambda: self.start_exercise(exercise_data))
        buttons_layout.addWidget(start_btn)
        
        info_btn = QPushButton("Detaylar")
        info_btn.setObjectName("secondary_button")
        info_btn.clicked.connect(lambda: self.show_exercise_details(exercise_data))
        buttons_layout.addWidget(info_btn)
        
        layout.addLayout(buttons_layout)
        
        return card
    
    def create_current_exercise_panel(self, parent_layout):
        """Mevcut egzersiz paneli"""
        self.current_exercise_frame = QFrame()
        self.current_exercise_frame.setFrameStyle(QFrame.StyledPanel)
        self.current_exercise_frame.setVisible(False)
        
        layout = QVBoxLayout(self.current_exercise_frame)
        
        # Başlık
        self.exercise_title = QLabel("Egzersiz Devam Ediyor")
        self.exercise_title.setFont(QFont("", 14, QFont.Bold))
        self.exercise_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.exercise_title)
        
        # İlerleme çubuğu
        self.exercise_progress = QProgressBar()
        self.exercise_progress.setRange(0, 100)
        layout.addWidget(self.exercise_progress)
        
        # Süre göstergesi
        self.time_label = QLabel("00:00 / 05:00")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("", 12))
        layout.addWidget(self.time_label)
        
        # Kontrol butonları
        controls_layout = QHBoxLayout()
        
        self.pause_btn = QPushButton("Duraklat")
        self.pause_btn.clicked.connect(self.pause_exercise)
        controls_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("Durdur")
        self.stop_btn.clicked.connect(self.stop_exercise)
        controls_layout.addWidget(self.stop_btn)
        
        layout.addLayout(controls_layout)
        
        parent_layout.addWidget(self.current_exercise_frame)
    
    def create_stat_mini_card(self, title: str, value: str, unit: str):
        """Mini istatistik kartı"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setFixedSize(120, 80)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("", 9))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: gray;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        unit_label = QLabel(unit)
        unit_label.setFont(QFont("", 8))
        unit_label.setAlignment(Qt.AlignCenter)
        unit_label.setStyleSheet("color: gray;")
        layout.addWidget(unit_label)
        
        return card
    
    def load_exercises_data(self):
        """Egzersiz verilerini yükle"""
        # Demo egzersiz verileri
        return {
            "neck": [
                {
                    "id": "neck_1",
                    "name": "Boyun Germe",
                    "description": "Boyun kaslarını gevşetmek için yavaş boyun hareketleri",
                    "duration": "3",
                    "difficulty": "Kolay",
                    "instructions": [
                        "Başınızı yavaşça sağa çevirin",
                        "15 saniye bekleyin",
                        "Başınızı yavaşça sola çevirin",
                        "15 saniye bekleyin",
                        "Başınızı öne eğin",
                        "15 saniye bekleyin"
                    ]
                },
                {
                    "id": "neck_2",
                    "name": "Boyun Kuvvetlendirme",
                    "description": "Boyun kaslarını güçlendiren izometrik egzersizler",
                    "duration": "5",
                    "difficulty": "Orta",
                    "instructions": [
                        "Elinizi alnınıza koyun",
                        "Başınızı öne itmeye çalışın",
                        "Elinizle karşı koyun",
                        "10 saniye tutun"
                    ]
                }
            ],
            "shoulder": [
                {
                    "id": "shoulder_1",
                    "name": "Omuz Çevirme",
                    "description": "Omuz kaslarını gevşeten dairesel hareketler",
                    "duration": "2",
                    "difficulty": "Kolay",
                    "instructions": [
                        "Omuzlarınızı geriye doğru çevirin",
                        "10 tekrar yapın",
                        "Omuzlarınızı öne doğru çevirin",
                        "10 tekrar yapın"
                    ]
                }
            ],
            "back": [
                {
                    "id": "back_1",
                    "name": "Sırt Germe",
                    "description": "Sırt kaslarını uzatan ve güçlendiren hareketler",
                    "duration": "7",
                    "difficulty": "Orta",
                    "instructions": [
                        "Ayakta durun",
                        "Kollarınızı yukarı kaldırın",
                        "Geriye doğru hafif eğilin",
                        "15 saniye tutun"
                    ]
                }
            ],
            "general": [
                {
                    "id": "general_1",
                    "name": "Genel Postür",
                    "description": "Tüm vücut postürünü düzelten kombine egzersizler",
                    "duration": "10",
                    "difficulty": "Orta",
                    "instructions": [
                        "Duvara sırtınızı yaslayın",
                        "Başınızı, omuzlarınızı ve kalçanızı duvara değdirin",
                        "2 dakika bu pozisyonda kalın"
                    ]
                }
            ]
        }
    
    def populate_recommended_exercises(self):
        """Önerilen egzersizleri listele"""
        # Şimdilik tüm kategorilerden birer egzersiz öner
        recommended = [
            self.exercises_data["neck"][0],
            self.exercises_data["shoulder"][0],
            self.exercises_data["back"][0]
        ]
        
        self.recommended_list.clear()
        
        for exercise in recommended:
            item = QListWidgetItem()
            item.setText(f"{exercise['name']} ({exercise['duration']} dk)")
            item.setData(Qt.UserRole, exercise)
            self.recommended_list.addItem(item)
        
        # Çift tıklama ile başlat
        self.recommended_list.itemDoubleClicked.connect(
            lambda item: self.start_exercise(item.data(Qt.UserRole))
        )
    
    def populate_exercise_history(self, history_list):
        """Egzersiz geçmişini doldur"""
        # Demo geçmiş verileri
        history_data = [
            {"date": "2024-01-15", "exercise": "Boyun Germe", "duration": "3 dk"},
            {"date": "2024-01-15", "exercise": "Omuz Çevirme", "duration": "2 dk"},
            {"date": "2024-01-14", "exercise": "Genel Postür", "duration": "10 dk"},
            {"date": "2024-01-14", "exercise": "Boyun Kuvvetlendirme", "duration": "5 dk"},
            {"date": "2024-01-13", "exercise": "Sırt Germe", "duration": "7 dk"}
        ]
        
        for entry in history_data:
            item = QListWidgetItem()
            item.setText(f"{entry['date']} - {entry['exercise']} ({entry['duration']})")
            history_list.addItem(item)
    
    def start_exercise(self, exercise_data: dict):
        """Egzersiz başlat"""
        try:
            self.current_exercise = exercise_data
            self.exercise_start_time = datetime.now()
            self.exercise_duration = int(exercise_data.get('duration', 5)) * 60  # saniye
            
            # UI güncelle
            self.exercise_title.setText(f"🏃 {exercise_data['name']}")
            self.current_exercise_frame.setVisible(True)
            self.exercise_progress.setValue(0)
            
            # Timer başlat
            self.exercise_timer.start(1000)  # Her saniye
            
            # Sinyal gönder
            self.exercise_started.emit(exercise_data['id'])
            
            self.logger.info(f"Egzersiz başlatıldı: {exercise_data['name']}")
            
        except Exception as e:
            self.logger.error(f"Egzersiz başlatma hatası: {str(e)}")
    
    def start_quick_exercise(self):
        """Hızlı egzersiz başlat"""
        quick_exercise = {
            "id": "quick_5min",
            "name": "Hızlı 5 Dakika",
            "description": "Boyun, omuz ve sırt egzersizlerinin karışımı",
            "duration": "5",
            "difficulty": "Kolay"
        }
        self.start_exercise(quick_exercise)
    
    def update_exercise_progress(self):
        """Egzersiz ilerlemesini güncelle"""
        if not self.current_exercise or not self.exercise_start_time:
            return
        
        # Geçen süre
        elapsed = (datetime.now() - self.exercise_start_time).total_seconds()
        progress = (elapsed / self.exercise_duration) * 100
        
        # Progress bar güncelle
        self.exercise_progress.setValue(min(int(progress), 100))
        
        # Süre etiketi güncelle
        elapsed_min = int(elapsed // 60)
        elapsed_sec = int(elapsed % 60)
        total_min = int(self.exercise_duration // 60)
        total_sec = int(self.exercise_duration % 60)
        
        self.time_label.setText(f"{elapsed_min:02d}:{elapsed_sec:02d} / {total_min:02d}:{total_sec:02d}")
        
        # Egzersiz tamamlandı mı?
        if elapsed >= self.exercise_duration:
            self.complete_exercise()
    
    def pause_exercise(self):
        """Egzersizi duraklat"""
        if self.exercise_timer.isActive():
            self.exercise_timer.stop()
            self.pause_btn.setText("Devam Et")
        else:
            self.exercise_timer.start(1000)
            self.pause_btn.setText("Duraklat")
    
    def stop_exercise(self):
        """Egzersizi durdur"""
        self.exercise_timer.stop()
        self.current_exercise_frame.setVisible(False)
        self.current_exercise = None
        self.pause_btn.setText("Duraklat")
        
        self.logger.info("Egzersiz durduruldu")
    
    def complete_exercise(self):
        """Egzersizi tamamla"""
        if self.current_exercise:
            # Sinyal gönder
            self.exercise_completed.emit(self.current_exercise['id'])
            
            # UI güncelle
            self.exercise_title.setText("✅ Egzersiz Tamamlandı!")
            self.exercise_progress.setValue(100)
            
            self.logger.info(f"Egzersiz tamamlandı: {self.current_exercise['name']}")
            
            # 3 saniye sonra paneli gizle
            QTimer.singleShot(3000, self.stop_exercise)
    
    def show_exercise_details(self, exercise_data: dict):
        """Egzersiz detaylarını göster"""
        # Basit mesaj kutusu (gerçek implementasyonda detaylı dialog)
        from PyQt5.QtWidgets import QMessageBox
        
        details = f"""
Egzersiz: {exercise_data['name']}

Açıklama: {exercise_data['description']}

Süre: {exercise_data['duration']} dakika
Zorluk: {exercise_data['difficulty']}

Talimatlar:
"""
        for i, instruction in enumerate(exercise_data.get('instructions', []), 1):
            details += f"{i}. {instruction}\n"
        
        msg = QMessageBox()
        msg.setWindowTitle("Egzersiz Detayları")
        msg.setText(details)
        msg.exec_()
    
    def apply_theme(self, theme_name: str):
        """Tema uygula"""
        if theme_name == "dark":
            # Koyu tema stilleri
            card_style = """
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
            card_style = """
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
            widget.setStyleSheet(card_style)
