"""
PostureFix - Veri Yönetimi Modülü
Postür verilerini saklar, analiz eder ve raporlar oluşturur
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

from config import AppConfig

@dataclass
class PostureSession:
    """Postür oturum verisi"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_duration: float  # dakika
    average_score: float
    poor_posture_count: int
    good_posture_count: int
    alerts_triggered: int

@dataclass
class PostureRecord:
    """Tek bir postür kaydı"""
    timestamp: datetime
    head_forward_angle: float
    neck_angle: float
    shoulder_slope: float
    shoulder_width: float
    back_straightness: float
    back_angle: float
    overall_score: float
    session_id: str

class DataManager:
    """Veri yönetimi sınıfı"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        
        # Veritabanı yolu
        self.db_path = os.path.join(self.config.DATA_DIR, "posture_data.db")
        
        # Mevcut oturum
        self.current_session: Optional[PostureSession] = None
        self.session_records: List[PostureRecord] = []
        
        # Veritabanını başlat
        self.init_database()
        
        self.logger.info("DataManager başlatıldı")
    
    def init_database(self):
        """SQLite veritabanını başlat"""
        try:
            # Veritabanı dizinini oluştur
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Oturumlar tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        total_duration REAL,
                        average_score REAL,
                        poor_posture_count INTEGER,
                        good_posture_count INTEGER,
                        alerts_triggered INTEGER
                    )
                ''')
                
                # Postür kayıtları tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posture_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        head_forward_angle REAL,
                        neck_angle REAL,
                        shoulder_slope REAL,
                        shoulder_width REAL,
                        back_straightness REAL,
                        back_angle REAL,
                        overall_score REAL,
                        session_id TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                    )
                ''')
                
                # Günlük istatistikler tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS daily_stats (
                        date TEXT PRIMARY KEY,
                        total_time REAL,
                        average_score REAL,
                        good_posture_percentage REAL,
                        poor_posture_percentage REAL,
                        total_alerts INTEGER,
                        sessions_count INTEGER
                    )
                ''')
                
                # Ayarlar tablosu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                conn.commit()
                
            self.logger.info("Veritabanı başarıyla başlatıldı")
            
        except Exception as e:
            self.logger.error(f"Veritabanı başlatma hatası: {str(e)}")
            raise
    
    def start_session(self) -> str:
        """Yeni bir postür oturumu başlat"""
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_session = PostureSession(
                session_id=session_id,
                start_time=datetime.now(),
                end_time=None,
                total_duration=0.0,
                average_score=0.0,
                poor_posture_count=0,
                good_posture_count=0,
                alerts_triggered=0
            )
            
            self.session_records = []
            
            self.logger.info(f"Yeni oturum başlatıldı: {session_id}")
            return session_id
            
        except Exception as e:
            self.logger.error(f"Oturum başlatma hatası: {str(e)}")
            raise
    
    def end_session(self):
        """Mevcut oturumu sonlandır"""
        if not self.current_session:
            return
        
        try:
            self.current_session.end_time = datetime.now()
            self.current_session.total_duration = (
                self.current_session.end_time - self.current_session.start_time
            ).total_seconds() / 60.0  # dakika
            
            # Ortalama skor hesapla
            if self.session_records:
                scores = [record.overall_score for record in self.session_records]
                self.current_session.average_score = sum(scores) / len(scores)
            
            # Oturumu veritabanına kaydet
            self.save_session_to_db()
            
            # Günlük istatistikleri güncelle
            self.update_daily_stats()
            
            self.logger.info(f"Oturum sonlandırıldı: {self.current_session.session_id}")
            
        except Exception as e:
            self.logger.error(f"Oturum sonlandırma hatası: {str(e)}")
        finally:
            self.current_session = None
            self.session_records = []
    
    def save_posture_data(self, posture_data: Dict[str, float], score: float):
        """Postür verisini kaydet"""
        if not self.current_session:
            self.start_session()
        
        try:
            # Postür kaydı oluştur
            record = PostureRecord(
                timestamp=datetime.now(),
                head_forward_angle=posture_data.get('head_forward_angle', 0.0),
                neck_angle=posture_data.get('neck_angle', 0.0),
                shoulder_slope=posture_data.get('shoulder_slope', 0.0),
                shoulder_width=posture_data.get('shoulder_width', 0.0),
                back_straightness=posture_data.get('back_straightness', 0.0),
                back_angle=posture_data.get('back_angle', 0.0),
                overall_score=score,
                session_id=self.current_session.session_id
            )
            
            # Oturum kayıtlarına ekle
            self.session_records.append(record)
            
            # İstatistikleri güncelle
            if score >= self.config.POOR_POSTURE_THRESHOLD:
                self.current_session.good_posture_count += 1
            else:
                self.current_session.poor_posture_count += 1
            
        except Exception as e:
            self.logger.error(f"Postür verisi kaydetme hatası: {str(e)}")
    
    def save_session_to_db(self):
        """Mevcut oturumu veritabanına kaydet"""
        if not self.current_session:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Oturum verilerini kaydet
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions 
                    (session_id, start_time, end_time, total_duration, 
                     average_score, poor_posture_count, good_posture_count, alerts_triggered)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.current_session.session_id,
                    self.current_session.start_time.isoformat(),
                    self.current_session.end_time.isoformat() if self.current_session.end_time else None,
                    self.current_session.total_duration,
                    self.current_session.average_score,
                    self.current_session.poor_posture_count,
                    self.current_session.good_posture_count,
                    self.current_session.alerts_triggered
                ))
                
                # Postür kayıtlarını kaydet
                for record in self.session_records:
                    cursor.execute('''
                        INSERT INTO posture_records 
                        (timestamp, head_forward_angle, neck_angle, shoulder_slope,
                         shoulder_width, back_straightness, back_angle, overall_score, session_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        record.timestamp.isoformat(),
                        record.head_forward_angle,
                        record.neck_angle,
                        record.shoulder_slope,
                        record.shoulder_width,
                        record.back_straightness,
                        record.back_angle,
                        record.overall_score,
                        record.session_id
                    ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Veritabanı kaydetme hatası: {str(e)}")
    
    def update_daily_stats(self):
        """Günlük istatistikleri güncelle"""
        try:
            today = datetime.now().date().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Bugünün verilerini hesapla
                cursor.execute('''
                    SELECT 
                        COUNT(*) as sessions_count,
                        SUM(total_duration) as total_time,
                        AVG(average_score) as average_score,
                        SUM(good_posture_count) as good_posture_total,
                        SUM(poor_posture_count) as poor_posture_total,
                        SUM(alerts_triggered) as total_alerts
                    FROM sessions 
                    WHERE DATE(start_time) = ?
                ''', (today,))
                
                result = cursor.fetchone()
                
                if result and result[0] > 0:  # Eğer bugün oturum varsa
                    sessions_count, total_time, avg_score, good_count, poor_count, total_alerts = result
                    
                    total_postures = good_count + poor_count
                    good_percentage = (good_count / total_postures * 100) if total_postures > 0 else 0
                    poor_percentage = (poor_count / total_postures * 100) if total_postures > 0 else 0
                    
                    # Günlük istatistikleri kaydet
                    cursor.execute('''
                        INSERT OR REPLACE INTO daily_stats
                        (date, total_time, average_score, good_posture_percentage,
                         poor_posture_percentage, total_alerts, sessions_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        today,
                        total_time or 0,
                        avg_score or 0,
                        good_percentage,
                        poor_percentage,
                        total_alerts or 0,
                        sessions_count
                    ))
                    
                    conn.commit()
                    
        except Exception as e:
            self.logger.error(f"Günlük istatistik güncelleme hatası: {str(e)}")
    
    def get_daily_stats(self, days: int = 30) -> pd.DataFrame:
        """Son N günün istatistiklerini getir"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT * FROM daily_stats 
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                '''
                
                df = pd.read_sql_query(query, conn, params=(
                    start_date.isoformat(), 
                    end_date.isoformat()
                ))
                
                return df
                
        except Exception as e:
            self.logger.error(f"Günlük istatistik alma hatası: {str(e)}")
            return pd.DataFrame()
    
    def get_session_history(self, limit: int = 50) -> List[PostureSession]:
        """Oturum geçmişini getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM sessions 
                    ORDER BY start_time DESC 
                    LIMIT ?
                ''', (limit,))
                
                sessions = []
                for row in cursor.fetchall():
                    session = PostureSession(
                        session_id=row[0],
                        start_time=datetime.fromisoformat(row[1]),
                        end_time=datetime.fromisoformat(row[2]) if row[2] else None,
                        total_duration=row[3] or 0,
                        average_score=row[4] or 0,
                        poor_posture_count=row[5] or 0,
                        good_posture_count=row[6] or 0,
                        alerts_triggered=row[7] or 0
                    )
                    sessions.append(session)
                
                return sessions
                
        except Exception as e:
            self.logger.error(f"Oturum geçmişi alma hatası: {str(e)}")
            return []
    
    def get_posture_trends(self, days: int = 7) -> Dict[str, List[float]]:
        """Postür trendlerini analiz et"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                query = '''
                    SELECT 
                        DATE(timestamp) as date,
                        AVG(overall_score) as avg_score,
                        AVG(head_forward_angle) as avg_head_forward,
                        AVG(neck_angle) as avg_neck,
                        AVG(shoulder_slope) as avg_shoulder,
                        AVG(back_straightness) as avg_back
                    FROM posture_records 
                    WHERE timestamp BETWEEN ? AND ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                '''
                
                df = pd.read_sql_query(query, conn, params=(
                    start_date.isoformat(),
                    end_date.isoformat()
                ))
                
                trends = {
                    'dates': df['date'].tolist(),
                    'scores': df['avg_score'].tolist(),
                    'head_forward': df['avg_head_forward'].tolist(),
                    'neck_angles': df['avg_neck'].tolist(),
                    'shoulder_slopes': df['avg_shoulder'].tolist(),
                    'back_straightness': df['avg_back'].tolist()
                }
                
                return trends
                
        except Exception as e:
            self.logger.error(f"Trend analizi hatası: {str(e)}")
            return {}
    
    def export_data(self, format: str = "csv", days: int = 30) -> str:
        """Verileri dışa aktar"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                # Tüm verileri al
                query = '''
                    SELECT 
                        pr.*,
                        s.start_time as session_start,
                        s.total_duration as session_duration
                    FROM posture_records pr
                    LEFT JOIN sessions s ON pr.session_id = s.session_id
                    WHERE pr.timestamp BETWEEN ? AND ?
                    ORDER BY pr.timestamp
                '''
                
                df = pd.read_sql_query(query, conn, params=(
                    start_date.isoformat(),
                    end_date.isoformat()
                ))
                
                # Dosya yolu
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"posture_data_{timestamp}.{format}"
                filepath = os.path.join(self.config.REPORTS_DIR, filename)
                
                # Dizini oluştur
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Formatına göre kaydet
                if format.lower() == "csv":
                    df.to_csv(filepath, index=False)
                elif format.lower() == "json":
                    df.to_json(filepath, orient="records", date_format="iso")
                elif format.lower() == "excel":
                    df.to_excel(filepath, index=False)
                
                self.logger.info(f"Veriler dışa aktarıldı: {filepath}")
                return filepath
                
        except Exception as e:
            self.logger.error(f"Veri dışa aktarma hatası: {str(e)}")
            return ""
    
    def save_session_data(self):
        """Mevcut oturum verilerini kaydet (periyodik)"""
        if self.current_session and self.session_records:
            try:
                # Sadece yeni kayıtları veritabanına ekle
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Son kaydedilen zamanı kontrol et
                    cursor.execute('''
                        SELECT MAX(timestamp) FROM posture_records 
                        WHERE session_id = ?
                    ''', (self.current_session.session_id,))
                    
                    last_saved = cursor.fetchone()[0]
                    last_saved_time = datetime.fromisoformat(last_saved) if last_saved else datetime.min
                    
                    # Yeni kayıtları filtrele
                    new_records = [r for r in self.session_records if r.timestamp > last_saved_time]
                    
                    # Yeni kayıtları ekle
                    for record in new_records:
                        cursor.execute('''
                            INSERT INTO posture_records 
                            (timestamp, head_forward_angle, neck_angle, shoulder_slope,
                             shoulder_width, back_straightness, back_angle, overall_score, session_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            record.timestamp.isoformat(),
                            record.head_forward_angle,
                            record.neck_angle,
                            record.shoulder_slope,
                            record.shoulder_width,
                            record.back_straightness,
                            record.back_angle,
                            record.overall_score,
                            record.session_id
                        ))
                    
                    conn.commit()
                    
                    if new_records:
                        self.logger.debug(f"{len(new_records)} yeni kayıt kaydedildi")
                        
            except Exception as e:
                self.logger.error(f"Oturum verisi kaydetme hatası: {str(e)}")
    
    def increment_alert_count(self):
        """Uyarı sayısını artır"""
        if self.current_session:
            self.current_session.alerts_triggered += 1
