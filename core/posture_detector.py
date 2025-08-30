"""
PostureFix - Postür Algılama Modülü
MediaPipe kullanarak gerçek zamanlı postür tespiti yapar
"""

import cv2
import numpy as np
import mediapipe as mp
import logging
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import math

from config import AppConfig, POSTURE_THRESHOLDS

@dataclass
class PostureLandmarks:
    """Postür analizi için gerekli vücut noktaları"""
    nose: Tuple[float, float, float]
    left_shoulder: Tuple[float, float, float]
    right_shoulder: Tuple[float, float, float]
    left_ear: Tuple[float, float, float]
    right_ear: Tuple[float, float, float]
    left_hip: Tuple[float, float, float]
    right_hip: Tuple[float, float, float]

class PostureDetector:
    """MediaPipe kullanarak postür tespiti yapan sınıf"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        
        # MediaPipe kurulumu
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Pose model
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=True,
            min_detection_confidence=self.config.MEDIAPIPE_DETECTION_CONFIDENCE,
            min_tracking_confidence=self.config.MEDIAPIPE_TRACKING_CONFIDENCE
        )
        
        # Kamera
        self.camera = None
        self.is_camera_active = False
        
        # Postür geçmişi (smoothing için)
        self.posture_history = []
        self.history_size = 5
        
        self.logger.info("PostureDetector başlatıldı")
    
    def start_camera(self) -> bool:
        """Kamerayı başlat"""
        try:
            self.camera = cv2.VideoCapture(self.config.CAMERA_INDEX)
            
            if not self.camera.isOpened():
                self.logger.error("Kamera açılamadı")
                return False
            
            # Kamera ayarları
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
            self.camera.set(cv2.CAP_PROP_FPS, self.config.CAMERA_FPS)
            
            self.is_camera_active = True
            self.logger.info("Kamera başarıyla başlatıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"Kamera başlatma hatası: {str(e)}")
            return False
    
    def stop_camera(self):
        """Kamerayı durdur"""
        try:
            if self.camera and self.camera.isOpened():
                self.camera.release()
                self.is_camera_active = False
                self.logger.info("Kamera durduruldu")
        except Exception as e:
            self.logger.error(f"Kamera durdurma hatası: {str(e)}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Kameradan bir frame al"""
        if not self.is_camera_active or not self.camera:
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            self.logger.warning("Frame alınamadı")
            return None
        
        return frame
    
    def extract_landmarks(self, results) -> Optional[PostureLandmarks]:
        """MediaPipe sonuçlarından gerekli landmark'ları çıkar"""
        if not results.pose_landmarks:
            return None
        
        landmarks = results.pose_landmarks.landmark
        
        try:
            # Gerekli noktaları çıkar
            posture_landmarks = PostureLandmarks(
                nose=(
                    landmarks[self.mp_pose.PoseLandmark.NOSE].x,
                    landmarks[self.mp_pose.PoseLandmark.NOSE].y,
                    landmarks[self.mp_pose.PoseLandmark.NOSE].z
                ),
                left_shoulder=(
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER].z
                ),
                right_shoulder=(
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].y,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER].z
                ),
                left_ear=(
                    landmarks[self.mp_pose.PoseLandmark.LEFT_EAR].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_EAR].y,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_EAR].z
                ),
                right_ear=(
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR].y,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR].z
                ),
                left_hip=(
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].x,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].y,
                    landmarks[self.mp_pose.PoseLandmark.LEFT_HIP].z
                ),
                right_hip=(
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].x,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].y,
                    landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP].z
                )
            )
            
            return posture_landmarks
            
        except Exception as e:
            self.logger.error(f"Landmark çıkarma hatası: {str(e)}")
            return None
    
    def calculate_angle(self, point1: Tuple[float, float], 
                       point2: Tuple[float, float], 
                       point3: Tuple[float, float]) -> float:
        """Üç nokta arasındaki açıyı hesapla"""
        # Vektörleri hesapla
        vector1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        vector2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        # Açıyı hesapla
        cosine_angle = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """İki nokta arasındaki mesafeyi hesapla"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def analyze_head_position(self, landmarks: PostureLandmarks) -> Dict[str, float]:
        """Kafa pozisyonunu analiz et"""
        # Kulaklar ve burun orta noktası
        ear_center = (
            (landmarks.left_ear[0] + landmarks.right_ear[0]) / 2,
            (landmarks.left_ear[1] + landmarks.right_ear[1]) / 2
        )
        
        # Omuzlar orta noktası
        shoulder_center = (
            (landmarks.left_shoulder[0] + landmarks.right_shoulder[0]) / 2,
            (landmarks.left_shoulder[1] + landmarks.right_shoulder[1]) / 2
        )
        
        # Kafa öne eğim açısı
        head_forward_angle = abs(landmarks.nose[0] - ear_center[0]) * 100  # Normalized
        
        # Boyun açısı
        neck_angle = self.calculate_angle(
            ear_center,
            shoulder_center,
            (shoulder_center[0], shoulder_center[1] + 0.1)  # Dikey referans
        )
        
        return {
            "head_forward_angle": head_forward_angle,
            "neck_angle": abs(90 - neck_angle) if neck_angle < 90 else neck_angle - 90
        }
    
    def analyze_shoulder_position(self, landmarks: PostureLandmarks) -> Dict[str, float]:
        """Omuz pozisyonunu analiz et"""
        # Omuz eğimi
        shoulder_slope = abs(landmarks.left_shoulder[1] - landmarks.right_shoulder[1]) * 100
        
        # Omuz genişliği
        shoulder_width = self.calculate_distance(
            (landmarks.left_shoulder[0], landmarks.left_shoulder[1]),
            (landmarks.right_shoulder[0], landmarks.right_shoulder[1])
        )
        
        return {
            "shoulder_slope": shoulder_slope,
            "shoulder_width": shoulder_width
        }
    
    def analyze_back_posture(self, landmarks: PostureLandmarks) -> Dict[str, float]:
        """Sırt postürünü analiz et"""
        # Omuz ve kalça orta noktaları
        shoulder_center = (
            (landmarks.left_shoulder[0] + landmarks.right_shoulder[0]) / 2,
            (landmarks.left_shoulder[1] + landmarks.right_shoulder[1]) / 2
        )
        
        hip_center = (
            (landmarks.left_hip[0] + landmarks.right_hip[0]) / 2,
            (landmarks.left_hip[1] + landmarks.right_hip[1]) / 2
        )
        
        # Sırt düzlüğü (omuz-kalça hattının dikeye yakınlığı)
        back_angle = self.calculate_angle(
            shoulder_center,
            hip_center,
            (hip_center[0], hip_center[1] + 0.1)  # Dikey referans
        )
        
        back_straightness = abs(90 - back_angle) if back_angle < 90 else back_angle - 90
        
        return {
            "back_straightness": back_straightness,
            "back_angle": back_angle
        }
    
    def smooth_posture_data(self, current_data: Dict[str, float]) -> Dict[str, float]:
        """Postür verilerini yumuşat (noise reduction)"""
        self.posture_history.append(current_data)
        
        # Geçmiş boyutunu sınırla
        if len(self.posture_history) > self.history_size:
            self.posture_history.pop(0)
        
        # Ortalama hesapla
        if len(self.posture_history) == 1:
            return current_data
        
        smoothed_data = {}
        for key in current_data.keys():
            values = [data[key] for data in self.posture_history if key in data]
            smoothed_data[key] = sum(values) / len(values)
        
        return smoothed_data
    
    def analyze_posture(self) -> Optional[Dict[str, float]]:
        """Ana postür analizi fonksiyonu"""
        if not self.is_camera_active:
            return None
        
        # Frame al
        frame = self.get_frame()
        if frame is None:
            return None
        
        try:
            # BGR'yi RGB'ye çevir
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # MediaPipe ile pose tespiti
            results = self.pose.process(rgb_frame)
            
            # Landmark'ları çıkar
            landmarks = self.extract_landmarks(results)
            if landmarks is None:
                return None
            
            # Postür analizleri
            head_data = self.analyze_head_position(landmarks)
            shoulder_data = self.analyze_shoulder_position(landmarks)
            back_data = self.analyze_back_posture(landmarks)
            
            # Tüm verileri birleştir
            posture_data = {**head_data, **shoulder_data, **back_data}
            
            # Verileri yumuşat
            smoothed_data = self.smooth_posture_data(posture_data)
            
            # Timestamp ekle
            smoothed_data['timestamp'] = cv2.getTickCount() / cv2.getTickFrequency()
            smoothed_data['frame_available'] = True
            
            return smoothed_data
            
        except Exception as e:
            self.logger.error(f"Postür analizi hatası: {str(e)}")
            return None
    
    def get_annotated_frame(self) -> Optional[np.ndarray]:
        """Postür çizgileri eklenmiş frame döndür"""
        if not self.is_camera_active:
            return None
        
        frame = self.get_frame()
        if frame is None:
            return None
        
        try:
            # BGR'yi RGB'ye çevir
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # MediaPipe ile pose tespiti
            results = self.pose.process(rgb_frame)
            
            # RGB'yi tekrar BGR'ye çevir (OpenCV için)
            annotated_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            
            # Pose çizgilerini ekle
            if results.pose_landmarks:
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
            
            return annotated_frame
            
        except Exception as e:
            self.logger.error(f"Frame annotation hatası: {str(e)}")
            return frame
    
    def cleanup(self):
        """Kaynakları temizle"""
        try:
            self.stop_camera()
            if self.pose:
                self.pose.close()
            self.logger.info("PostureDetector kaynakları temizlendi")
        except Exception as e:
            self.logger.error(f"Cleanup hatası: {str(e)}")
    
    def __del__(self):
        """Destructor"""
        self.cleanup()
