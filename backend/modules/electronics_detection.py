import numpy as np
from ultralytics import YOLO
from .config import YOLO_CONFIDENCE, CLASSES_OF_INTEREST

# Carregar modelo YOLOv8 pré-treinado
yolo_model = YOLO('yolov8n.pt')  # Modelo nano padrão - substitua por um modelo personalizado se necessário

# Função para detectar notebooks e monitores com YOLOv8
def detect_electronics(frame, model=yolo_model, wrist_position=None, is_lower_body=False):
    if is_lower_body:
        return []
    
    # Usa a confiança definida nas configurações
    CONFIDENCE_THRESHOLD = YOLO_CONFIDENCE
        
    # Run detection once and store results with increased confidence
    results = model(frame, verbose=False, conf=CONFIDENCE_THRESHOLD)[0]
    
    # Use numpy operations instead of loops with stricter validation
    valid_classes = np.isin(results.boxes.cls.cpu().numpy(), CLASSES_OF_INTEREST)
    confident_detections = results.boxes.conf.cpu().numpy() > CONFIDENCE_THRESHOLD
    
    # Validação adicional do tamanho das detecções
    boxes = results.boxes.xyxy.cpu().numpy()
    valid_size = np.ones_like(valid_classes, dtype=bool)
    
    for i, box in enumerate(boxes):
        width = box[2] - box[0]
        height = box[3] - box[1]
        aspect_ratio = width / height if height > 0 else 0
        
        # Filtra detecções com proporções improváveis
        if aspect_ratio < 0.5 or aspect_ratio > 2.0:
            valid_size[i] = False
            
        # Filtra detecções muito pequenas ou muito grandes
        box_area = width * height
        frame_area = frame.shape[0] * frame.shape[1]
        if box_area < frame_area * 0.01 or box_area > frame_area * 0.8:
            valid_size[i] = False
    
    valid_indices = np.where(valid_classes & confident_detections)[0]
    
    if not len(valid_indices):
        return []
        
    boxes = results.boxes.xyxy.cpu().numpy()[valid_indices]
    classes = results.boxes.cls.cpu().numpy()[valid_indices]
    confs = results.boxes.conf.cpu().numpy()[valid_indices]
    
    # Process all detections at once
    detections = [{
        'class': model.names[int(cls)],
        'confidence': conf,
        'bbox': tuple(map(int, box))
    } for box, cls, conf in zip(boxes, classes, confs)]
    
    if wrist_position:
        centers = np.array([[int((box[0] + box[2])//2), int((box[1] + box[3])//2)] for box in boxes])
        distances = np.linalg.norm(centers - np.array(wrist_position), axis=1)
        closest_idx = np.argmin(distances)
        return [detections[closest_idx]]
    
    return detections