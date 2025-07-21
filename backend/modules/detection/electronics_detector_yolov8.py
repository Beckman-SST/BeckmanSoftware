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
    
    def detect(self, frame, wrist_position=None, is_lower_body=False, eye_position=None):
        """
        Detecta dispositivos eletrônicos em um frame.
        
        Args:
            frame (numpy.ndarray): Frame a ser processado
            wrist_position (tuple, optional): Posição do pulso para encontrar o dispositivo mais próximo
            is_lower_body (bool, optional): Indica se é análise da parte inferior do corpo
            eye_position (tuple, optional): Posição dos olhos para melhorar a seleção do dispositivo
            
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
        
        # Se uma posição de pulso for fornecida, usa algoritmo inteligente de seleção
        if wrist_position:
            best_device = self._select_best_device(detections, wrist_position, eye_position, frame.shape)
            return [best_device] if best_device else []
            
        return detections
    
    def _select_best_device(self, detections, wrist_position, eye_position=None, frame_shape=None):
        """
        Seleciona o melhor dispositivo baseado em múltiplos critérios.
        
        Args:
            detections (list): Lista de detecções
            wrist_position (tuple): Posição do pulso
            eye_position (tuple, optional): Posição dos olhos
            frame_shape (tuple, optional): Dimensões do frame (height, width, channels)
            
        Returns:
            dict: Melhor detecção ou None se nenhuma for adequada
        """
        if not detections:
            return None
        
        if len(detections) == 1:
            return detections[0]
        
        scores = []
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            device_center = (center_x, center_y)
            
            # Calcula área do dispositivo
            device_area = (x2 - x1) * (y2 - y1)
            
            # Critério 1: Distância ao pulso (peso 30%)
            distance_to_wrist = np.linalg.norm(np.array(device_center) - np.array(wrist_position))
            max_distance = np.sqrt(frame_shape[0]**2 + frame_shape[1]**2) if frame_shape else 1000
            distance_score = 1.0 - (distance_to_wrist / max_distance)
            
            # Critério 2: Posição frontal (peso 25%)
            # Dispositivos mais centralizados horizontalmente são preferidos
            frame_center_x = frame_shape[1] // 2 if frame_shape else 640
            horizontal_distance = abs(center_x - frame_center_x)
            max_horizontal_distance = frame_shape[1] // 2 if frame_shape else 640
            frontal_score = 1.0 - (horizontal_distance / max_horizontal_distance)
            
            # Critério 3: Tamanho do dispositivo (peso 20%)
            # Dispositivos maiores (monitores/TVs) são preferidos para análise ergonômica
            frame_area = frame_shape[0] * frame_shape[1] if frame_shape else 640 * 480
            size_ratio = device_area / frame_area
            # Normaliza para que dispositivos entre 10% e 50% da tela tenham score máximo
            if 0.1 <= size_ratio <= 0.5:
                size_score = 1.0
            elif size_ratio < 0.1:
                size_score = size_ratio / 0.1  # Penaliza dispositivos muito pequenos
            else:
                size_score = max(0.0, 1.0 - (size_ratio - 0.5) / 0.3)  # Penaliza dispositivos muito grandes
            
            # Critério 4: Confiança da detecção (peso 15%)
            confidence_score = detection['confidence']
            
            # Critério 5: Alinhamento com direção do olhar (peso 10%)
            eye_alignment_score = 0.5  # Score neutro por padrão
            if eye_position:
                # Calcula se o dispositivo está na direção do olhar
                eye_to_device = np.array(device_center) - np.array(eye_position)
                eye_to_wrist = np.array(wrist_position) - np.array(eye_position)
                
                # Calcula o ângulo entre os vetores
                if np.linalg.norm(eye_to_device) > 0 and np.linalg.norm(eye_to_wrist) > 0:
                    cos_angle = np.dot(eye_to_device, eye_to_wrist) / (
                        np.linalg.norm(eye_to_device) * np.linalg.norm(eye_to_wrist)
                    )
                    cos_angle = np.clip(cos_angle, -1.0, 1.0)
                    angle = np.arccos(cos_angle)
                    # Converte para score (ângulos menores = score maior)
                    eye_alignment_score = 1.0 - (angle / np.pi)
            
            # Critério 6: Tipo de dispositivo (peso extra para monitores)
            device_type_score = 1.0
            if detection['class'] in ['tv', 'monitor']:
                device_type_score = 1.2  # Bonus para monitores/TVs
            elif detection['class'] == 'laptop':
                device_type_score = 1.0  # Score neutro para laptops
            
            # Calcula score final ponderado
            final_score = (
                distance_score * 0.30 +
                frontal_score * 0.25 +
                size_score * 0.20 +
                confidence_score * 0.15 +
                eye_alignment_score * 0.10
            ) * device_type_score
            
            scores.append({
                'detection': detection,
                'score': final_score,
                'details': {
                    'distance_score': distance_score,
                    'frontal_score': frontal_score,
                    'size_score': size_score,
                    'confidence_score': confidence_score,
                    'eye_alignment_score': eye_alignment_score,
                    'device_type_score': device_type_score
                }
            })
        
        # Ordena por score e retorna o melhor
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Debug: imprime scores para análise
        print(f"Seleção de dispositivo - {len(detections)} detectados:")
        for i, score_info in enumerate(scores):
            det = score_info['detection']
            details = score_info['details']
            print(f"  {i+1}. {det['class']} (conf: {det['confidence']:.2f}) - Score: {score_info['score']:.3f}")
            print(f"     Distância: {details['distance_score']:.2f}, Frontal: {details['frontal_score']:.2f}, "
                  f"Tamanho: {details['size_score']:.2f}, Olhar: {details['eye_alignment_score']:.2f}")
        
        return scores[0]['detection']
    
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