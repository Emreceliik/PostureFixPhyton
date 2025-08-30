"""
PostureFix - İstatistikler Widget'ı
Postür istatistiklerini ve grafikleri gösteren widget
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QFrame, QGridLayout, QPushButton, QComboBox,
                            QScrollArea, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QPainter, QPen
import logging
from datetime import datetime, timedelta
import json

# Matplotlib backend'ini Qt5Agg olarak ayarla
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

from config import COLORS

class StatisticsWidget(QWidget):
    """İstatistikler widget'ı"""
    
    def __init__(self):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)
        
        # Veri depolama
        self.daily_data = []
        self.realtime_data = []
        self.session_stats = {
            'start_time': None,
            'total_time': 0,
            'good_posture_time': 0,
            'poor_posture_time': 0,
            'alerts_count': 0,
            'average_score': 0
        }
        
        # UI kurulumu
        self.setup_ui()
        
        # Güncelleme timer'ı
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_statistics)
        self.update_timer.start(5000)  # 5 saniyede bir güncelle
        
        self.logger.info("StatisticsWidget oluşturuldu")
    
    def setup_ui(self):
        """UI kurulumu"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Başlık ve kontroller
        self.create_header(layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Güncel oturum sekmesi
        self.create_current_session_tab()
        self.tab_widget.addTab(self.current_session_widget, "Güncel Oturum")
        
        # Günlük istatistikler sekmesi
        self.create_daily_stats_tab()
        self.tab_widget.addTab(self.daily_stats_widget, "Günlük İstatistikler")
        
        # Trend analizi sekmesi
        self.create_trends_tab()
        self.tab_widget.addTab(self.trends_widget, "Trend Analizi")
        
        layout.addWidget(self.tab_widget)
    
    def create_header(self, parent_layout):
        """Başlık ve kontrolleri oluştur"""
        header_frame = QFrame()
        header_frame.setMaximumHeight(60)
        
        layout = QHBoxLayout(header_frame)
        
        # Başlık
        title = QLabel("📊 Postür İstatistikleri")
        title.setFont(QFont("", 16, QFont.Bold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Zaman aralığı seçici
        period_label = QLabel("Zaman Aralığı:")
        layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Bugün", "Son 7 Gün", "Son 30 Gün", "Tüm Zamanlar"])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        layout.addWidget(self.period_combo)
        
        # Yenile butonu
        refresh_button = QPushButton("🔄 Yenile")
        refresh_button.clicked.connect(self.refresh_statistics)
        layout.addWidget(refresh_button)
        
        parent_layout.addWidget(header_frame)
    
    def create_current_session_tab(self):
        """Güncel oturum sekmesini oluştur"""
        self.current_session_widget = QWidget()
        layout = QVBoxLayout(self.current_session_widget)
        
        # Oturum bilgileri kartları
        cards_layout = QGridLayout()
        
        # Toplam süre kartı
        self.total_time_card = self.create_stat_card("⏱️", "Toplam Süre", "00:00:00", COLORS["primary"])
        cards_layout.addWidget(self.total_time_card, 0, 0)
        
        # İyi postür kartı
        self.good_posture_card = self.create_stat_card("✅", "İyi Postür", "0%", COLORS["good_posture"])
        cards_layout.addWidget(self.good_posture_card, 0, 1)
        
        # Kötü postür kartı
        self.poor_posture_card = self.create_stat_card("❌", "Kötü Postür", "0%", COLORS["poor_posture"])
        cards_layout.addWidget(self.poor_posture_card, 0, 2)
        
        # Uyarı sayısı kartı
        self.alerts_card = self.create_stat_card("⚠️", "Uyarılar", "0", COLORS["warning"])
        cards_layout.addWidget(self.alerts_card, 1, 0)
        
        # Ortalama skor kartı
        self.average_score_card = self.create_stat_card("📈", "Ortalama Skor", "0%", COLORS["secondary"])
        cards_layout.addWidget(self.average_score_card, 1, 1)
        
        # Mevcut skor kartı
        self.current_score_card = self.create_stat_card("🎯", "Mevcut Skor", "0%", COLORS["success"])
        cards_layout.addWidget(self.current_score_card, 1, 2)
        
        layout.addLayout(cards_layout)
        
        # Gerçek zamanlı grafik
        self.create_realtime_chart(layout)
    
    def create_daily_stats_tab(self):
        """Günlük istatistikler sekmesini oluştur"""
        self.daily_stats_widget = QWidget()
        layout = QVBoxLayout(self.daily_stats_widget)
        
        # Günlük özet grafikleri
        self.create_daily_charts(layout)
    
    def create_trends_tab(self):
        """Trend analizi sekmesini oluştur"""
        self.trends_widget = QWidget()
        layout = QVBoxLayout(self.trends_widget)
        
        # Trend grafikleri
        self.create_trend_charts(layout)
    
    def create_stat_card(self, icon: str, title: str, value: str, color: str):
        """İstatistik kartı oluştur"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setFixedHeight(100)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                margin: 2px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Üst kısım - ikon ve başlık
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("", 20))
        top_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("", 10))
        title_label.setStyleSheet("color: gray;")
        top_layout.addWidget(title_label)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # Alt kısım - değer
        value_label = QLabel(value)
        value_label.setFont(QFont("", 18, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Kartı güncelleme için referans sakla
        card.icon_label = icon_label
        card.title_label = title_label
        card.value_label = value_label
        
        return card
    
    def create_realtime_chart(self, parent_layout):
        """Gerçek zamanlı grafik oluştur"""
        chart_frame = QFrame()
        chart_frame.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(chart_frame)
        
        # Başlık
        chart_title = QLabel("Gerçek Zamanlı Postür Skoru")
        chart_title.setFont(QFont("", 12, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_title)
        
        # Matplotlib figür
        self.realtime_figure = Figure(figsize=(10, 4), dpi=80)
        self.realtime_canvas = FigureCanvas(self.realtime_figure)
        layout.addWidget(self.realtime_canvas)
        
        # İlk grafik çizimi
        self.plot_realtime_data()
        
        parent_layout.addWidget(chart_frame)
    
    def create_daily_charts(self, parent_layout):
        """Günlük grafikler oluştur"""
        # Günlük özet grafiği
        daily_frame = QFrame()
        daily_frame.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(daily_frame)
        
        chart_title = QLabel("Günlük Postür Özeti")
        chart_title.setFont(QFont("", 12, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_title)
        
        self.daily_figure = Figure(figsize=(10, 6), dpi=80)
        self.daily_canvas = FigureCanvas(self.daily_figure)
        layout.addWidget(self.daily_canvas)
        
        self.plot_daily_data()
        
        parent_layout.addWidget(daily_frame)
    
    def create_trend_charts(self, parent_layout):
        """Trend grafikleri oluştur"""
        trend_frame = QFrame()
        trend_frame.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(trend_frame)
        
        chart_title = QLabel("Postür Trend Analizi")
        chart_title.setFont(QFont("", 12, QFont.Bold))
        chart_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_title)
        
        self.trend_figure = Figure(figsize=(10, 8), dpi=80)
        self.trend_canvas = FigureCanvas(self.trend_figure)
        layout.addWidget(self.trend_canvas)
        
        self.plot_trend_data()
        
        parent_layout.addWidget(trend_frame)
    
    def plot_realtime_data(self):
        """Gerçek zamanlı veri grafiği çiz"""
        self.realtime_figure.clear()
        ax = self.realtime_figure.add_subplot(111)
        
        if len(self.realtime_data) > 0:
            # Son 100 veriyi al
            recent_data = self.realtime_data[-100:]
            times = [i for i in range(len(recent_data))]
            scores = [d.get('score', 0) * 100 for d in recent_data]
            
            ax.plot(times, scores, color=COLORS["primary"], linewidth=2, label="Postür Skoru")
            ax.axhline(y=70, color=COLORS["good_posture"], linestyle='--', alpha=0.7, label="İyi Postür Eşiği")
            ax.axhline(y=40, color=COLORS["poor_posture"], linestyle='--', alpha=0.7, label="Kötü Postür Eşiği")
            
            ax.set_ylim(0, 100)
            ax.set_ylabel("Postür Skoru (%)")
            ax.set_xlabel("Zaman")
            ax.legend()
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, "Henüz veri yok", ha='center', va='center', transform=ax.transAxes)
        
        ax.set_title("Son 100 Ölçüm")
        self.realtime_canvas.draw()
    
    def plot_daily_data(self):
        """Günlük veri grafiği çiz"""
        self.daily_figure.clear()
        
        # 2x2 subplot
        ax1 = self.daily_figure.add_subplot(221)
        ax2 = self.daily_figure.add_subplot(222)
        ax3 = self.daily_figure.add_subplot(223)
        ax4 = self.daily_figure.add_subplot(224)
        
        # Demo veriler (gerçek implementasyonda veritabanından gelecek)
        days = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
        scores = [75, 68, 82, 71, 79, 85, 77]
        good_posture_times = [6.2, 5.8, 7.1, 6.0, 6.8, 7.5, 6.9]
        poor_posture_times = [1.8, 2.2, 0.9, 2.0, 1.2, 0.5, 1.1]
        alert_counts = [3, 5, 1, 4, 2, 1, 2]
        
        # Günlük skorlar
        ax1.bar(days, scores, color=COLORS["primary"], alpha=0.7)
        ax1.set_title("Günlük Ortalama Skorlar")
        ax1.set_ylabel("Skor (%)")
        ax1.set_ylim(0, 100)
        
        # İyi/Kötü postür süreleri
        width = 0.35
        x = np.arange(len(days))
        ax2.bar(x - width/2, good_posture_times, width, label='İyi Postür', color=COLORS["good_posture"], alpha=0.7)
        ax2.bar(x + width/2, poor_posture_times, width, label='Kötü Postür', color=COLORS["poor_posture"], alpha=0.7)
        ax2.set_title("Günlük Postür Süreleri")
        ax2.set_ylabel("Süre (saat)")
        ax2.set_xticks(x)
        ax2.set_xticklabels(days)
        ax2.legend()
        
        # Uyarı sayıları
        ax3.plot(days, alert_counts, marker='o', color=COLORS["warning"], linewidth=2, markersize=6)
        ax3.set_title("Günlük Uyarı Sayıları")
        ax3.set_ylabel("Uyarı Sayısı")
        ax3.grid(True, alpha=0.3)
        
        # Pasta grafiği - Bu haftanın özeti
        total_good = sum(good_posture_times)
        total_poor = sum(poor_posture_times)
        labels = ['İyi Postür', 'Kötü Postür']
        sizes = [total_good, total_poor]
        colors = [COLORS["good_posture"], COLORS["poor_posture"]]
        
        ax4.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax4.set_title("Bu Haftanın Postür Dağılımı")
        
        self.daily_figure.tight_layout()
        self.daily_canvas.draw()
    
    def plot_trend_data(self):
        """Trend analizi grafiği çiz"""
        self.trend_figure.clear()
        
        # 2x1 subplot
        ax1 = self.trend_figure.add_subplot(211)
        ax2 = self.trend_figure.add_subplot(212)
        
        # Demo trend verileri (30 günlük)
        days = list(range(1, 31))
        avg_scores = [65 + 10 * np.sin(i/5) + np.random.normal(0, 3) for i in days]
        improvement_trend = [60 + i * 0.5 + np.random.normal(0, 2) for i in days]
        
        # Ortalama skorlar trendi
        ax1.plot(days, avg_scores, color=COLORS["primary"], linewidth=2, label="Günlük Ortalama")
        ax1.plot(days, improvement_trend, color=COLORS["success"], linewidth=2, linestyle='--', label="İyileşme Trendi")
        ax1.axhline(y=70, color=COLORS["good_posture"], linestyle=':', alpha=0.7, label="İyi Postür Eşiği")
        ax1.set_title("30 Günlük Postür Skoru Trendi")
        ax1.set_ylabel("Ortalama Skor (%)")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Haftalık karşılaştırma
        weeks = ['1. Hafta', '2. Hafta', '3. Hafta', '4. Hafta']
        week_scores = [68, 72, 75, 78]
        week_improvements = [0, 4, 3, 3]
        
        x = np.arange(len(weeks))
        bars = ax2.bar(x, week_scores, color=COLORS["secondary"], alpha=0.7, label="Haftalık Ortalama")
        
        # Gelişim oklarını ekle
        for i, (bar, improvement) in enumerate(zip(bars, week_improvements)):
            if improvement > 0:
                ax2.annotate(f'+{improvement}%', 
                           xy=(bar.get_x() + bar.get_width()/2, bar.get_height()), 
                           xytext=(0, 10), textcoords='offset points',
                           ha='center', va='bottom',
                           color=COLORS["success"], fontweight='bold')
        
        ax2.set_title("Haftalık Gelişim")
        ax2.set_ylabel("Ortalama Skor (%)")
        ax2.set_xticks(x)
        ax2.set_xticklabels(weeks)
        ax2.set_ylim(0, 100)
        
        self.trend_figure.tight_layout()
        self.trend_canvas.draw()
    
    def update_realtime_data(self, posture_data: dict):
        """Gerçek zamanlı veri güncelle"""
        try:
            # Veriyi listeye ekle
            self.realtime_data.append(posture_data)
            
            # Liste boyutunu sınırla
            if len(self.realtime_data) > 1000:
                self.realtime_data = self.realtime_data[-500:]
            
            # Oturum istatistiklerini güncelle
            self.update_session_stats(posture_data)
            
            # Kartları güncelle
            self.update_stat_cards()
            
        except Exception as e:
            self.logger.error(f"Gerçek zamanlı veri güncelleme hatası: {str(e)}")
    
    def update_session_stats(self, posture_data: dict):
        """Oturum istatistiklerini güncelle"""
        if self.session_stats['start_time'] is None:
            self.session_stats['start_time'] = datetime.now()
        
        # Toplam süreyi güncelle
        elapsed = (datetime.now() - self.session_stats['start_time']).total_seconds() / 60  # dakika
        self.session_stats['total_time'] = elapsed
        
        # Postür kalitesine göre süre ekle
        score = posture_data.get('score', 0)
        if score >= 0.7:
            self.session_stats['good_posture_time'] += 0.1  # 0.1 dakika (~6 saniye)
        elif score < 0.4:
            self.session_stats['poor_posture_time'] += 0.1
        
        # Ortalama skor hesapla
        if len(self.realtime_data) > 0:
            total_score = sum(d.get('score', 0) for d in self.realtime_data)
            self.session_stats['average_score'] = total_score / len(self.realtime_data)
    
    def update_stat_cards(self):
        """İstatistik kartlarını güncelle"""
        try:
            # Toplam süre
            total_minutes = int(self.session_stats['total_time'])
            hours = total_minutes // 60
            minutes = total_minutes % 60
            self.total_time_card.value_label.setText(f"{hours:02d}:{minutes:02d}:00")
            
            # İyi postür yüzdesi
            total_posture_time = self.session_stats['good_posture_time'] + self.session_stats['poor_posture_time']
            if total_posture_time > 0:
                good_percentage = (self.session_stats['good_posture_time'] / total_posture_time) * 100
                self.good_posture_card.value_label.setText(f"{good_percentage:.1f}%")
                
                poor_percentage = (self.session_stats['poor_posture_time'] / total_posture_time) * 100
                self.poor_posture_card.value_label.setText(f"{poor_percentage:.1f}%")
            
            # Uyarı sayısı
            self.alerts_card.value_label.setText(str(self.session_stats['alerts_triggered']))
            
            # Ortalama skor
            avg_score_percent = int(self.session_stats['average_score'] * 100)
            self.average_score_card.value_label.setText(f"{avg_score_percent}%")
            
            # Mevcut skor
            if len(self.realtime_data) > 0:
                current_score = int(self.realtime_data[-1].get('score', 0) * 100)
                self.current_score_card.value_label.setText(f"{current_score}%")
            
        except Exception as e:
            self.logger.error(f"Kart güncelleme hatası: {str(e)}")
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        try:
            # Grafikleri yeniden çiz
            self.plot_realtime_data()
            
            # Günlük sekme aktifse günlük grafikleri güncelle
            if self.tab_widget.currentIndex() == 1:
                self.plot_daily_data()
            
            # Trend sekmesi aktifse trend grafikleri güncelle
            elif self.tab_widget.currentIndex() == 2:
                self.plot_trend_data()
                
        except Exception as e:
            self.logger.error(f"İstatistik güncelleme hatası: {str(e)}")
    
    def on_period_changed(self, period: str):
        """Zaman aralığı değiştiğinde"""
        self.logger.info(f"Zaman aralığı değiştirildi: {period}")
        # Seçilen periyoda göre verileri filtrele ve grafikleri güncelle
        self.refresh_statistics()
    
    def refresh_statistics(self):
        """İstatistikleri yenile"""
        try:
            # Tüm grafikleri yeniden çiz
            self.plot_realtime_data()
            self.plot_daily_data()
            self.plot_trend_data()
            
            self.logger.info("İstatistikler yenilendi")
            
        except Exception as e:
            self.logger.error(f"İstatistik yenileme hatası: {str(e)}")
    
    def increment_alert_count(self):
        """Uyarı sayısını artır"""
        self.session_stats['alerts_triggered'] += 1
    
    def apply_theme(self, theme_name: str):
        """Tema uygula"""
        if theme_name == "dark":
            # Matplotlib için koyu tema
            plt.style.use('dark_background')
            
            # Widget stilleri
            card_style = """
                QFrame {
                    background-color: #2b2b2b;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    color: white;
                }
                QLabel {
                    color: white;
                }
            """
        else:
            # Matplotlib için açık tema
            plt.style.use('default')
            
            card_style = """
                QFrame {
                    background-color: white;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    color: black;
                }
                QLabel {
                    color: black;
                }
            """
        
        # Grafikleri yeniden çiz
        self.refresh_statistics()
