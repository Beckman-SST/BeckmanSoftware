import cv2
import numpy as np
import os
from .electronics_detector_yolov8 import ElectronicsDetectorYOLOv8

class ElectronicsDetector:
    def __init__(self, yolo_confidence=0.65):
        """
        Inicializa o detector de dispositivos eletrônicos usando YOLO.
        
        Args:
            yolo_confidence (float): Confiança mínima para detecção
        """
        # Variável global para armazenar a confiança do YOLO
        global YOLO_CONFIDENCE
        YOLO_CONFIDENCE = yolo_confidence
        
        # Inicializa o detector YOLOv8
        self.detector = ElectronicsDetectorYOLOv8(yolo_confidence)
    
    def _initialize_yolo(self):
        """
        Método mantido para compatibilidade com código existente.
        A inicialização real é feita na classe ElectronicsDetectorYOLOv8.
        """
        pass
    
    def detect(self, frame, wrist_position=None, is_lower_body=False):
        """
        Detecta dispositivos eletrônicos em um frame.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            wrist_position (tuple, optional): Posição do pulso para encontrar o dispositivo mais próximo
            is_lower_body (bool, optional): Indica se é análise da parte inferior do corpo
            
        Returns:
            list: Lista de detecções (classe, confiança, caixa delimitadora)
        """
        # Condição para não processar se for análise da parte inferior do corpo
        if is_lower_body:
            return []
            
        # Usa o detector YOLOv8 para detectar eletrônicos
        yolo_detections = self.detector.detect(frame, wrist_position, is_lower_body)
        
        # Converte o formato das detecções para manter compatibilidade com o código existente
        detections = []
        for detection in yolo_detections:
            class_name = detection['class']
            confidence = detection['confidence']
            x1, y1, x2, y2 = detection['bbox']
            
            # Converte para o formato (x, y, w, h) usado pelo código existente
            x = x1
            y = y1
            w = x2 - x1
            h = y2 - y1
            
            detections.append((class_name, confidence, (x, y, w, h)))
        
        return detections
    
    def draw_detections(self, frame, detections):
        """
        Desenha as detecções de dispositivos eletrônicos no frame.
        
        Args:
            frame (numpy.ndarray): Frame onde as detecções serão desenhadas
            detections (list): Lista de detecções (classe, confiança, caixa delimitadora)
            
        Returns:
            numpy.ndarray: Frame com as detecções desenhadas
        """
        for class_name, confidence, (x, y, w, h) in detections:
            # Desenha a caixa delimitadora
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Desenha o nome da classe e a confiança
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def get_detection_center(self, detection):
        """
        Obtém o centro de uma detecção.
        
        Args:
            detection (tuple): Detecção (classe, confiança, caixa delimitadora)
            
        Returns:
            tuple: Coordenadas (x, y) do centro da detecção
        """
        _, _, (x, y, w, h) = detection
        center_x = x + w // 2
        center_y = y + h // 2
        
        return (center_x, center_y)