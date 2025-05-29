import cv2
import numpy as np
import os
from ultralytics import YOLO

class ElectronicsDetectorYOLOv8:
    def __init__(self, yolo_confidence=0.65):
        """
        Inicializa o detector de dispositivos eletrônicos usando YOLOv8.
        
        Args:
            yolo_confidence (float): Confiança mínima para detecção
        """
        self.confidence_threshold = yolo_confidence
        self.yolo_initialized = False
        self.model = None
        
        # Classes de interesse para notebooks e monitores (IDs do dataset COCO)
        self.CLASSES_OF_INTEREST = [63, 62]  # 63 = laptop, 62 = tv/monitor
        
        # Inicializa o modelo YOLOv8
        self._initialize_yolo()
    
    def _initialize_yolo(self):
        """
        Inicializa o modelo YOLOv8 para detecção de objetos.
        """
        try:
            # Carrega o modelo YOLOv8 pré-treinado
            model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yolov8n.pt')
            
            # Verifica se o arquivo existe no diretório atual, caso contrário, usa o modelo padrão
            if not os.path.exists(model_path):
                # Se o arquivo não existir, usa o modelo padrão do YOLOv8
                self.model = YOLO('yolov8n.pt')
            else:
                self.model = YOLO(model_path)
                
            self.yolo_initialized = True
        except Exception as e:
            print(f"Erro ao inicializar YOLOv8: {e}")
            self.yolo_initialized = False
    
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
        
        if not self.yolo_initialized or self.model is None:
            return []
        
        # Usa a confiança definida nas configurações
        CONFIDENCE_THRESHOLD = self.confidence_threshold
        
        # Run detection once and store results with increased confidence
        results = self.model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)[0]
        
        # Use numpy operations instead of loops with stricter validation
        valid_classes = np.isin(results.boxes.cls.cpu().numpy(), self.CLASSES_OF_INTEREST)
        confident_detections = results.boxes.conf.cpu().numpy() > CONFIDENCE_THRESHOLD
        
        # Validação adicional do tamanho das detecções
        boxes = results.boxes.xyxy.cpu().numpy()
        valid_size = np.ones_like(valid_classes, dtype=bool)
        
        for i, box in enumerate(boxes):
            width = box[2] - box[0]
            height = box[3] - box[1]
            aspect_ratio = width / height if height > 0 else 0
            
            # Filtra detecções com proporções improváveis
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:  # Ex: largura muito menor que altura ou vice-versa
                valid_size[i] = False
                
            # Filtra detecções muito pequenas ou muito grandes
            box_area = width * height
            frame_area = frame.shape[0] * frame.shape[1]
            if box_area < frame_area * 0.01 or box_area > frame_area * 0.8:  # Menor que 1% ou maior que 80% do frame
                valid_size[i] = False
        
        # Combina todas as validações para obter os índices finais das detecções válidas
        valid_indices = np.where(valid_classes & confident_detections & valid_size)[0]
        
        if not len(valid_indices):
            return []
            
        boxes = results.boxes.xyxy.cpu().numpy()[valid_indices]
        classes = results.boxes.cls.cpu().numpy()[valid_indices]
        confs = results.boxes.conf.cpu().numpy()[valid_indices]
        
        # Process all detections at once
        detections = [{
            'class': self.model.names[int(cls)],
            'confidence': conf,
            'bbox': tuple(map(int, box))
        } for box, cls, conf in zip(boxes, classes, confs)]
        
        # Se uma posição de pulso for fornecida, retorna apenas a detecção mais próxima
        if wrist_position:
            centers = np.array([[int((box[0] + box[2])//2), int((box[1] + box[3])//2)] for box in boxes])
            distances = np.linalg.norm(centers - np.array(wrist_position), axis=1)  # Distância euclidiana
            closest_idx = np.argmin(distances)
            return [detections[closest_idx]]  # Retorna uma lista com a detecção mais próxima
            
        return detections
    
    def draw_detections(self, frame, detections):
        """
        Desenha as detecções de dispositivos eletrônicos no frame.
        
        Args:
            frame (numpy.ndarray): Frame onde as detecções serão desenhadas
            detections (list): Lista de detecções (dicionários com classe, confiança, bbox)
            
        Returns:
            numpy.ndarray: Frame com as detecções desenhadas
        """
        for detection in detections:
            class_name = detection['class']
            confidence = detection['confidence']
            x1, y1, x2, y2 = detection['bbox']
            
            # Desenha a caixa delimitadora
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Desenha o nome da classe e a confiança
            label = f"{class_name}: {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame
    
    def get_detection_center(self, detection):
        """
        Obtém o centro de uma detecção.
        
        Args:
            detection (dict): Detecção (dicionário com classe, confiança, bbox)
            
        Returns:
            tuple: Coordenadas (x, y) do centro da detecção
        """
        x1, y1, x2, y2 = detection['bbox']
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        
        return (center_x, center_y)