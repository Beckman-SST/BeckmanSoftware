import os
import json
import tempfile

# Função para carregar as configurações do arquivo de status
def carregar_configuracoes():
    status_file = os.path.join(tempfile.gettempdir(), 'processamento_status.json')
    config = {
        'min_detection_confidence': 0.80,
        'min_tracking_confidence': 0.80,
        'yolo_confidence': 0.65,
        'moving_average_window': 5,
        'show_face_blur': True,
        'show_electronics': False,
        'show_angles': True,
        'show_upper_body': True,
        'show_lower_body': True,
        'process_lower_body': True,
        'resize_width': 800
    }
    
    try:
        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                status_data = json.load(f)
                if 'config' in status_data:
                    config = status_data['config']
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
    
    return config

# Carrega as configurações
config = carregar_configuracoes()

# Configurações de detecção e rastreamento
MIN_DETECTION_CONFIDENCE = config['min_detection_confidence']
MIN_TRACKING_CONFIDENCE = config['min_tracking_confidence']
MOVING_AVERAGE_WINDOW = config['moving_average_window']
SHOW_FACE_BLUR = config['show_face_blur']
SHOW_ELECTRONICS = config['show_electronics']
SHOW_ANGLES = config['show_angles']
SHOW_UPPER_BODY = config['show_upper_body']
SHOW_LOWER_BODY = config['show_lower_body']
PROCESS_LOWER_BODY = config['process_lower_body']
RESIZE_WIDTH = config['resize_width']
YOLO_CONFIDENCE = config['yolo_confidence']

# Classes de interesse para notebooks e monitores (IDs do dataset COCO)
CLASSES_OF_INTEREST = [63, 62]  # 63 = laptop, 62 = tv/monitor