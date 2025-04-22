import cv2 as cv
import numpy as np
import mediapipe as mp
import sys
import os
import signal
import math
import json
import tempfile
import logging
import datetime
from ultralytics import YOLO
from multiprocessing import Pool

# Configuração do sistema de logs
log_folder = "logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# Configura o logger
log_file = os.path.join(log_folder, f"processamento_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("processamento")

# Variável global para controle do processamento
deve_continuar = True

# Handler para sinal de interrupção
def signal_handler(sig, frame):
    global deve_continuar
    deve_continuar = False
    logger.warning("\nProcessamento recebeu sinal de cancelamento...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Configurações
mpDraw = mp.solutions.drawing_utils
mpHolistic = mp.solutions.holistic

# Carregar modelo YOLOv8 pré-treinado
yolo_model = YOLO('yolov8n.pt')  # Modelo nano padrão - substitua por um modelo personalizado se necessário

# Classes de interesse para notebooks e monitores (IDs do dataset COCO)
CLASSES_OF_INTEREST = [63, 62]  # 63 = laptop, 62 = tv/monitor

# Conexões personalizadas para mostrar apenas o necessário
custom_pose_connections = [
    # Upper body connections
    (mpHolistic.PoseLandmark.RIGHT_SHOULDER.value, mpHolistic.PoseLandmark.RIGHT_ELBOW.value),
    (mpHolistic.PoseLandmark.RIGHT_ELBOW.value, mpHolistic.PoseLandmark.RIGHT_WRIST.value),
    (mpHolistic.PoseLandmark.LEFT_SHOULDER.value, mpHolistic.PoseLandmark.LEFT_ELBOW.value),
    (mpHolistic.PoseLandmark.LEFT_ELBOW.value, mpHolistic.PoseLandmark.LEFT_WRIST.value),
    # Lower body connections with heel and ankle-foot connections
    (mpHolistic.PoseLandmark.RIGHT_HIP.value, mpHolistic.PoseLandmark.RIGHT_KNEE.value),
    (mpHolistic.PoseLandmark.RIGHT_KNEE.value, mpHolistic.PoseLandmark.RIGHT_ANKLE.value),
    (mpHolistic.PoseLandmark.RIGHT_ANKLE.value, mpHolistic.PoseLandmark.RIGHT_HEEL.value),
    (mpHolistic.PoseLandmark.RIGHT_HEEL.value, mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value),
    (mpHolistic.PoseLandmark.RIGHT_ANKLE.value, mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value),
    (mpHolistic.PoseLandmark.LEFT_HIP.value, mpHolistic.PoseLandmark.LEFT_KNEE.value),
    (mpHolistic.PoseLandmark.LEFT_KNEE.value, mpHolistic.PoseLandmark.LEFT_ANKLE.value),
    (mpHolistic.PoseLandmark.LEFT_ANKLE.value, mpHolistic.PoseLandmark.LEFT_HEEL.value),
    (mpHolistic.PoseLandmark.LEFT_HEEL.value, mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value),
    (mpHolistic.PoseLandmark.LEFT_ANKLE.value, mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value)
]

# Carrega as configurações do arquivo de status
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

# Inicializando o modelo Holistic com parâmetros otimizados
holistic = mpHolistic.Holistic(
    min_detection_confidence=MIN_DETECTION_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    model_complexity=2 
)

# Buffer para média móvel dos landmarks
landmark_buffer = []

# Função para redimensionar imagem mantendo a proporção
def resize_with_aspect_ratio(image, width=None, height=None, inter=cv.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv.resize(image, dim, interpolation=inter)

# Função para calcular ângulos
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def prolongar_reta(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    # Não precisamos prolongar a reta, apenas retornamos o ponto final (vértice da caixa)
    return (int(x2), int(y2))

# Função para calcular a visibilidade de um conjunto de landmarks
def calculate_visibility(landmarks, indices):
    visibility_sum = 0
    valid_count = 0
    for idx in indices:
        if landmarks[idx].visibility:
            visibility_sum += landmarks[idx].visibility
            valid_count += 1
    
    # Retorna 0 se não houver landmarks válidos
    if valid_count == 0:
        return 0
    
    # Calcula a média de visibilidade
    avg_visibility = visibility_sum / valid_count
    
    # Aplica um limiar mínimo de confiança
    return avg_visibility if avg_visibility > MIN_DETECTION_CONFIDENCE else 0

# Função para detectar notebooks e monitores com YOLOv8
def detect_electronics(frame, model, wrist_position=None, is_lower_body=False):
    if is_lower_body:
        logger.debug("Análise de parte inferior do corpo, pulando detecção de eletrônicos")
        return []
    
    # Usa a confiança definida nas configurações
    CONFIDENCE_THRESHOLD = YOLO_CONFIDENCE
    logger.debug(f"Iniciando detecção de eletrônicos com confiança: {CONFIDENCE_THRESHOLD}")
        
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
        logger.warning("Nenhum dispositivo eletrônico detectado com confiança suficiente")
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

# Função para desenhar detecções de eletrônicos (com transparência)
def draw_electronics_detections(frame, detections):
    # Se não há detecções, retorna o frame sem modificações
    if not detections:
        return frame
        
    # Se a visualização de eletrônicos estiver desativada, retorna o frame sem modificações
    # O cálculo dos ângulos dos olhos será feito independentemente
    if not SHOW_ELECTRONICS:
        return frame
        
    # Cria uma cópia do frame para desenhar as detecções
    overlay = frame.copy()
    
    # Desenha cada detecção
    for detection in detections:
        x1, y1, x2, y2 = detection['bbox']
        cv.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
        label = f"{detection['class']}: {detection['confidence']:.2f}"
        cv.putText(overlay, label, (x1, y1-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Aplica transparência
    alpha = 0.7
    cv.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    return frame

# Função para determinar se deve processar parte inferior do corpo
def should_process_lower_body(landmarks):
    # Se o processamento da parte inferior estiver desativado nas configurações, retorna False
    if not PROCESS_LOWER_BODY:
        return False
        
    # Verifica a visibilidade dos tornozelos
    right_ankle_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_ANKLE.value].visibility
    left_ankle_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_ANKLE.value].visibility
    ankle_visibility = max(right_ankle_visibility, left_ankle_visibility)
    
    # Se a visibilidade do tornozelo for 0, processa como imagem de perfil (ângulos superiores)
    if ankle_visibility == 0:
        return False
    
    # Para ângulos inferiores, verifica a visibilidade do joelho, tornozelo e foot index
    right_knee_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_KNEE.value].visibility
    left_knee_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_KNEE.value].visibility
    right_foot_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value].visibility
    left_foot_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value].visibility
    
    # Calcula a visibilidade média dos pontos necessários para ângulos inferiores
    knee_visibility = max(right_knee_visibility, left_knee_visibility)
    foot_visibility = max(right_foot_visibility, left_foot_visibility)
    
    # Retorna True apenas se todos os pontos necessários estiverem visíveis
    return all(v > 0.5 for v in [knee_visibility, ankle_visibility, foot_visibility]) 

# Função para ajustar posição do texto para evitar sobreposição
def adjust_text_position(frame, text, position, bbox=None):
    h, w = frame.shape[:2]
    x, y = position
    
    # Se houver uma bbox, verificar se a posição está dentro
    if bbox:
        bx1, by1, bx2, by2 = bbox
        if x >= bx1 and x <= bx2 and y >= by1 and y <= by2:
            # Mover para cima da bbox
            y = by1 - 30 if by1 - 30 > 0 else by2 + 30
    
    # Garantir que o texto não saia da imagem
    (text_width, text_height), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    x = max(10, min(x, w - text_width - 10))
    y = max(text_height + 10, min(y, h - 10))
    
    return (x, y)

# Define a pasta de saída
output_folder = "Output"

# Verifica se a pasta já existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    logger.info(f"Pasta '{output_folder}' criada com sucesso.")
else:
    logger.info(f"Pasta '{output_folder}' já existe. As imagens serão salvas nela.")

# Obtém o caminho do arquivo passado como argumento
input_path = sys.argv[1]

# Verificar se o conteúdo é uma imagem
logger.info(f"Iniciando processamento do arquivo: {input_path}")
image = cv.imread(input_path)
is_image = image is not None

if is_image:
    logger.info(f"Arquivo detectado como imagem")
    frames = [image]
else:
    logger.info(f"Tentando abrir como vídeo")
    cap = cv.VideoCapture(input_path)
    if not cap.isOpened():
        logger.error(f"Erro ao carregar o vídeo: {input_path}. Verifique o caminho e o arquivo.")
        frames = []
    else:
        logger.info(f"Vídeo carregado com sucesso, extraindo frames")
        frames = []
        while cap.isOpened() and deve_continuar:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        logger.info(f"Total de {len(frames)} frames extraídos do vídeo")

for frame_idx, frame in enumerate(frames):
    if not deve_continuar:
        break
        
    # Redimensiona o frame mantendo a proporção usando a largura configurada
    frame = resize_with_aspect_ratio(frame, width=RESIZE_WIDTH)
    
    # Processamento com MediaPipe primeiro
    imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = holistic.process(imgRGB)
    
    # Validação e suavização dos landmarks
    if results.pose_landmarks:
        current_landmarks = [(lm.x, lm.y, lm.z, lm.visibility) for lm in results.pose_landmarks.landmark]
        
        # Atualiza o buffer de landmarks
        landmark_buffer.append(current_landmarks)
        if len(landmark_buffer) > MOVING_AVERAGE_WINDOW:
            landmark_buffer.pop(0)
        
        # Aplica média móvel se houver landmarks suficientes
        if len(landmark_buffer) >= 3:
            # Calcula a média das posições dos landmarks
            avg_landmarks = []
            for i in range(len(current_landmarks)):
                x_avg = sum(frame[i][0] for frame in landmark_buffer) / len(landmark_buffer)
                y_avg = sum(frame[i][1] for frame in landmark_buffer) / len(landmark_buffer)
                z_avg = sum(frame[i][2] for frame in landmark_buffer) / len(landmark_buffer)
                vis_avg = sum(frame[i][3] for frame in landmark_buffer) / len(landmark_buffer)
                
                # Atualiza os landmarks com os valores suavizados
                results.pose_landmarks.landmark[i].x = x_avg
                results.pose_landmarks.landmark[i].y = y_avg
                results.pose_landmarks.landmark[i].z = z_avg
                results.pose_landmarks.landmark[i].visibility = vis_avg
    
    # Inicializa as variáveis
    landmarks = None
    wrist_position = None
    side = "right"  # valor padrão
    
    # Verifica se os landmarks principais foram detectados
    if not results.pose_landmarks:
        logger.error(f"Frame {frame_idx}: Não foi possível detectar os landmarks principais do corpo na imagem.")
        # Salva a imagem original sem processamento
        output_path = os.path.join(output_folder, f"error_{os.path.basename(input_path)}")
        cv.imwrite(output_path, frame)
        logger.info(f"Imagem original salva em: {output_path}")
        continue
    
    # Verifica se há landmarks da pose
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        # Determina qual lado está mais visível e define a posição do pulso
        if landmarks:
            right_visibility = landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].visibility
            left_visibility = landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].visibility
            
            side = "right" if right_visibility > left_visibility else "left"
            if side == "right":
                wrist_position = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].x * frame.shape[1]),
                                int(landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].y * frame.shape[0]))
            else:
                wrist_position = (int(landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].x * frame.shape[1]),
                                int(landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].y * frame.shape[0]))
    
    # Verificar se é análise da parte inferior do corpo
    is_lower_body = should_process_lower_body(results.pose_landmarks.landmark) if results.pose_landmarks else False
    logger.info(f"Frame {frame_idx}: Tipo de análise: {'parte inferior do corpo' if is_lower_body else 'parte superior do corpo'}")

    # Detectar objetos eletrônicos apenas se não for análise da parte inferior
    logger.info(f"Frame {frame_idx}: Iniciando detecção de dispositivos eletrônicos")
    electronics_detections = detect_electronics(frame, yolo_model, wrist_position, is_lower_body)
    if electronics_detections:
        logger.info(f"Frame {frame_idx}: {len(electronics_detections)} dispositivo(s) eletrônico(s) detectado(s)")
        for i, det in enumerate(electronics_detections):
            logger.debug(f"Dispositivo {i+1}: {det['class']} (confiança: {det['confidence']:.2f})")
    else:
        logger.warning(f"Frame {frame_idx}: Nenhum dispositivo eletrônico detectado")
    
    # Cria uma cópia limpa do frame para desenhar os landmarks
    frame_clean = frame.copy()

    # Verificar se os landmarks da face foram detectados e se a tarja está ativada
    if results.face_landmarks and SHOW_FACE_BLUR:
        landmarks = results.face_landmarks.landmark
        h, w, _ = frame.shape

        face_points = []
        for landmark in landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            face_points.append((x, y))

        x_coords = [p[0] for p in face_points]
        y_coords = [p[1] for p in face_points]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)

        padding = 20
        x_min = max(0, x_min - padding)
        x_max = min(w, x_max + padding)
        y_min = max(0, y_min - padding)
        y_max = min(h, y_max + padding)

        cv.rectangle(frame_clean, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
    elif SHOW_FACE_BLUR:
        print("Landmarks do rosto não detectados. Usando landmarks dos olhos da pose como alternativa.")

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape

            left_eye = (int(landmarks[mpHolistic.PoseLandmark.LEFT_EYE.value].x * w),
                        int(landmarks[mpHolistic.PoseLandmark.LEFT_EYE.value].y * h))
            right_eye = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_EYE.value].x * w),
                         int(landmarks[mpHolistic.PoseLandmark.RIGHT_EYE.value].y * h))

            x_min = min(left_eye[0], right_eye[0])
            x_max = max(left_eye[0], right_eye[0])
            y_min = min(left_eye[1], right_eye[1])
            y_max = max(left_eye[1], right_eye[1])

            # Garante um tamanho mínimo para a tarja
            tarja_width = max(x_max - x_min, int(w * 0.20))  # Mínimo de 20% da largura da imagem
            tarja_height = int(tarja_width * 1.0)  # Altura igual à largura para melhor cobertura
            
            # Centraliza a tarja horizontalmente
            center_x = (x_min + x_max) // 2
            x_min = max(0, center_x - tarja_width // 2)
            x_max = min(w, center_x + tarja_width // 2)
            
            # Ajusta a altura da tarja
            y_min = max(0, y_min - tarja_height // 2)
            y_max = min(h, y_max + tarja_height // 2)

            cv.rectangle(frame_clean, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        else:
            print("Landmarks da pose também não detectados. Não foi possível desenhar a tarja.")

    try:
        landmarks = results.pose_landmarks.landmark
    except:
        landmarks = None

    if landmarks and deve_continuar:
        process_lower = should_process_lower_body(landmarks)
        
        if process_lower:
            # Process lower body
            right_leg_indices = [
                mpHolistic.PoseLandmark.RIGHT_HIP.value,
                mpHolistic.PoseLandmark.RIGHT_KNEE.value,
                mpHolistic.PoseLandmark.RIGHT_ANKLE.value,
                mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value
            ]
            
            left_leg_indices = [
                mpHolistic.PoseLandmark.LEFT_HIP.value,
                mpHolistic.PoseLandmark.LEFT_KNEE.value,
                mpHolistic.PoseLandmark.LEFT_ANKLE.value,
                mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value
            ]

            right_leg_visibility = calculate_visibility(landmarks, right_leg_indices)
            left_leg_visibility = calculate_visibility(landmarks, left_leg_indices)

            visible_landmarks = results.pose_landmarks
            
            if right_leg_visibility > left_leg_visibility:
                print("Perna direita mais visível. Processando lado direito.")
                side = "right"
                indices_manter = right_leg_indices
            else:
                print("Perna esquerda mais visível. Processando lado esquerdo.")
                side = "left"
                indices_manter = left_leg_indices

            # Hide unwanted landmarks
            for i in range(len(visible_landmarks.landmark)):
                if i not in indices_manter:
                    visible_landmarks.landmark[i].visibility = 0

            # Filtra as conexões com base nas configurações
            filtered_connections = []
            if SHOW_LOWER_BODY:
                filtered_connections.extend([
                    conn for conn in custom_pose_connections 
                    if conn[0] in [mpHolistic.PoseLandmark.RIGHT_HIP.value, mpHolistic.PoseLandmark.LEFT_HIP.value,
                                   mpHolistic.PoseLandmark.RIGHT_KNEE.value, mpHolistic.PoseLandmark.LEFT_KNEE.value,
                                   mpHolistic.PoseLandmark.RIGHT_ANKLE.value, mpHolistic.PoseLandmark.LEFT_ANKLE.value,
                                   mpHolistic.PoseLandmark.RIGHT_HEEL.value, mpHolistic.PoseLandmark.LEFT_HEEL.value,
                                   mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value, mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value]
                ])
            
            # Draw landmarks and connections with increased thickness for legs
            mpDraw.draw_landmarks(
                frame_clean,
                visible_landmarks,
                filtered_connections,
                mpDraw.DrawingSpec(color=(245, 117, 66), thickness=4, circle_radius=4),
                mpDraw.DrawingSpec(color=(214, 121, 108), thickness=4, circle_radius=4)
            )

            # Process angles for the selected leg first
            if side == "right":
                hip = [landmarks[mpHolistic.PoseLandmark.RIGHT_HIP.value].x,
                      landmarks[mpHolistic.PoseLandmark.RIGHT_HIP.value].y]
                knee = [landmarks[mpHolistic.PoseLandmark.RIGHT_KNEE.value].x,
                     landmarks[mpHolistic.PoseLandmark.RIGHT_KNEE.value].y]
                ankle = [landmarks[mpHolistic.PoseLandmark.RIGHT_ANKLE.value].x,
                        landmarks[mpHolistic.PoseLandmark.RIGHT_ANKLE.value].y]
                foot_index = [landmarks[mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value].x,
                            landmarks[mpHolistic.PoseLandmark.RIGHT_FOOT_INDEX.value].y]
            else:
                hip = [landmarks[mpHolistic.PoseLandmark.LEFT_HIP.value].x,
                      landmarks[mpHolistic.PoseLandmark.LEFT_HIP.value].y]
                knee = [landmarks[mpHolistic.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks[mpHolistic.PoseLandmark.LEFT_KNEE.value].y]
                ankle = [landmarks[mpHolistic.PoseLandmark.LEFT_ANKLE.value].x,
                        landmarks[mpHolistic.PoseLandmark.LEFT_ANKLE.value].y]
                foot_index = [landmarks[mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value].x,
                            landmarks[mpHolistic.PoseLandmark.LEFT_FOOT_INDEX.value].y]

            # Draw face mesh if detected and face blur is enabled
            if results.face_landmarks and not SHOW_FACE_BLUR:
                mpDraw.draw_landmarks(
                    frame_clean,
                    results.face_landmarks,
                    mp.solutions.face_mesh.FACEMESH_TESSELATION,
                    mpDraw.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                    mpDraw.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                )

            # Convert coordinates to pixels
            h, w, _ = frame_clean.shape
            knee_px = (int(knee[0] * w), int(knee[1] * h))
            ankle_px = (int(ankle[0] * w), int(ankle[1] * h))

            # Calculate angles
            knee_angle = calculate_angle(hip, knee, ankle)
            ankle_angle = calculate_angle(knee, ankle, foot_index)

            # Ajustar posição do texto para evitar sobreposição com detecções
            knee_text = f"{knee_angle:.2f} graus"
            ankle_text = f"{ankle_angle:.2f} graus"
            
            knee_pos = adjust_text_position(frame_clean, knee_text, (knee_px[0], knee_px[1] - 10))
            ankle_pos = adjust_text_position(frame_clean, ankle_text, (ankle_px[0], ankle_px[1] - 10))

            # Draw angles if enabled
            if SHOW_ANGLES:
                cv.putText(frame_clean, knee_text, knee_pos,
                          cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv.putText(frame_clean, ankle_text, ankle_pos,
                          cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Crop the frame to show only from above hip to bottom
            h, w, _ = frame_clean.shape
            if side == "right":
                hip_y = int(landmarks[mpHolistic.PoseLandmark.RIGHT_HIP.value].y * h)
            else:
                hip_y = int(landmarks[mpHolistic.PoseLandmark.LEFT_HIP.value].y * h)
            
            margin_above_hip = 150
            crop_y_start = max(0, hip_y - margin_above_hip)
            frame_clean = frame_clean[crop_y_start:h, 0:w]

        else:
            # Original upper body processing
            right_indices = [
                mpHolistic.PoseLandmark.RIGHT_SHOULDER.value,
                mpHolistic.PoseLandmark.RIGHT_ELBOW.value,
                mpHolistic.PoseLandmark.RIGHT_WRIST.value,
                mpHolistic.PoseLandmark.RIGHT_EYE.value
            ]
            
            left_indices = [
                mpHolistic.PoseLandmark.LEFT_SHOULDER.value,
                mpHolistic.PoseLandmark.LEFT_ELBOW.value,
                mpHolistic.PoseLandmark.LEFT_WRIST.value,
                mpHolistic.PoseLandmark.LEFT_EYE.value
            ]

            # Calcula qual lado é mais visível
            right_visibility = calculate_visibility(landmarks, right_indices)
            left_visibility = calculate_visibility(landmarks, left_indices)

            # Cria uma cópia dos landmarks para manipulação
            visible_landmarks = results.pose_landmarks

            if right_visibility > left_visibility:
                logger.info(f"Frame {frame_idx}: Lado direito mais visível. Processando lado direito.")
                side = "right"
                indices_manter = right_indices
                eye_position = (int(landmarks[mpHolistic.PoseLandmark.RIGHT_EYE.value].x * frame_clean.shape[1]),
                               int(landmarks[mpHolistic.PoseLandmark.RIGHT_EYE.value].y * frame_clean.shape[0]))
                logger.debug(f"Posição do olho direito: {eye_position}")
            else:
                logger.info(f"Frame {frame_idx}: Lado esquerdo mais visível. Processando lado esquerdo.")
                side = "left"
                indices_manter = left_indices
                eye_position = (int(landmarks[mpHolistic.PoseLandmark.LEFT_EYE.value].x * frame_clean.shape[1]),
                               int(landmarks[mpHolistic.PoseLandmark.LEFT_EYE.value].y * frame_clean.shape[0]))
                logger.debug(f"Posição do olho esquerdo: {eye_position}")

            # Oculta todos os landmarks exceto os do lado selecionado
            for i in range(len(visible_landmarks.landmark)):
                if i not in indices_manter:
                    visible_landmarks.landmark[i].visibility = 0

            # Desenha apenas os landmarks visíveis com conexões personalizadas
            mpDraw.draw_landmarks(
                frame_clean,
                visible_landmarks,
                custom_pose_connections,
                mpDraw.DrawingSpec(color=(245, 117, 66), thickness=4, circle_radius=4),
                mpDraw.DrawingSpec(color=(214, 121, 108), thickness=4, circle_radius=4)
            )

            # Calcula o ângulo de abertura dos olhos em relação ao dispositivo eletrônico
            # Sempre calcula os ângulos dos olhos, independente da configuração SHOW_ELECTRONICS
            if electronics_detections:
                logger.info(f"Frame {frame_idx}: Dispositivo eletrônico detectado, calculando ângulo dos olhos")
                detection = electronics_detections[0]
                x1, y1, x2, y2 = detection['bbox']
                logger.debug(f"Bounding box do dispositivo: ({x1}, {y1}, {x2}, {y2})")
                
                if side == "left":
                    # Para pessoa virada à esquerda: superior esquerdo e inferior direito
                    top_left = (x1, y1)
                    bottom_right = (x2, y2)
                    
                    # Usa os vértices da caixa como pontos finais das retas
                    prolonged_top = prolongar_reta(eye_position, top_left)
                    prolonged_bottom = prolongar_reta(eye_position, bottom_right)
                    logger.debug(f"Pontos para cálculo (lado esquerdo): olho={eye_position}, topo={top_left}, base={bottom_right}")
                else:
                    # Para pessoa virada à direita: superior direito e inferior esquerdo
                    top_right = (x2, y1)
                    bottom_left = (x1, y2)
                    
                    # Usa os vértices da caixa como pontos finais das retas
                    prolonged_top = prolongar_reta(eye_position, top_right)
                    prolonged_bottom = prolongar_reta(eye_position, bottom_left)
                    logger.debug(f"Pontos para cálculo (lado direito): olho={eye_position}, topo={top_right}, base={bottom_left}")
                
                # Desenha as retas prolongadas apenas se SHOW_ANGLES estiver ativado
                if SHOW_ANGLES:
                    cv.line(frame_clean, eye_position, prolonged_top, (0, 0, 255), 2)
                    cv.line(frame_clean, eye_position, prolonged_bottom, (0, 0, 255), 2)
                
                try:
                    # Calcula o ângulo entre as retas
                    eye_angle = calculate_angle(prolonged_top, eye_position, prolonged_bottom)
                    logger.info(f"Frame {frame_idx}: Ângulo dos olhos calculado: {eye_angle:.2f} graus")
                    
                    # Adiciona o texto do ângulo próximo ao olho se SHOW_ANGLES estiver ativado
                    if SHOW_ANGLES:
                        eye_text = f"{eye_angle:.2f}graus"
                        text_position = (eye_position[0] + 10, eye_position[1] - 10)
                        cv.putText(frame_clean, eye_text, text_position,
                                  cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                except Exception as e:
                    logger.error(f"Frame {frame_idx}: Erro ao calcular ângulo dos olhos: {str(e)}")
                    logger.error(f"Dados para debug: eye_position={eye_position}, prolonged_top={prolonged_top}, prolonged_bottom={prolonged_bottom}")
            else:
                logger.warning(f"Frame {frame_idx}: Nenhum dispositivo eletrônico detectado, não foi possível calcular o ângulo dos olhos")

            # Cálculo dos ângulos
            if side == "right":
                shoulder = [landmarks[mpHolistic.PoseLandmark.RIGHT_SHOULDER.value].x,
                           landmarks[mpHolistic.PoseLandmark.RIGHT_SHOULDER.value].y]
                elbow = [landmarks[mpHolistic.PoseLandmark.RIGHT_ELBOW.value].x,
                         landmarks[mpHolistic.PoseLandmark.RIGHT_ELBOW.value].y]
                wrist = [landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].x,
                         landmarks[mpHolistic.PoseLandmark.RIGHT_WRIST.value].y]
                middle_finger = [landmarks[mpHolistic.PoseLandmark.RIGHT_INDEX.value].x,
                                landmarks[mpHolistic.PoseLandmark.RIGHT_INDEX.value].y]
            else:
                shoulder = [landmarks[mpHolistic.PoseLandmark.LEFT_SHOULDER.value].x,
                           landmarks[mpHolistic.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[mpHolistic.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[mpHolistic.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mpHolistic.PoseLandmark.LEFT_WRIST.value].y]
                middle_finger = [landmarks[mpHolistic.PoseLandmark.LEFT_INDEX.value].x,
                                landmarks[mpHolistic.PoseLandmark.LEFT_INDEX.value].y]

            # Converter coordenadas e exibir ângulos
            h, w, _ = frame_clean.shape
            shoulder_px = (int(shoulder[0] * w), int(shoulder[1] * h))
            elbow_px = (int(elbow[0] * w), int(elbow[1] * h))
            wrist_px = (int(wrist[0] * w), int(wrist[1] * h))
            middle_finger_px = (int(middle_finger[0] * w), int(middle_finger[1] * h))

            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            logger.info(f"Frame {frame_idx}: Ângulo do cotovelo {side}: {elbow_angle:.2f} graus")

            wrist_angle = calculate_angle(elbow, wrist, middle_finger)
            logger.info(f"Frame {frame_idx}: Ângulo do pulso {side}: {wrist_angle:.2f} graus")

            # Ajustar posição do texto para evitar sobreposição
            elbow_text = f"{elbow_angle:.2f} graus"
            wrist_text = f"{wrist_angle:.2f} graus"
            
            elbow_pos = adjust_text_position(frame_clean, elbow_text, (elbow_px[0], elbow_px[1] - 10))
            wrist_pos = adjust_text_position(frame_clean, wrist_text, (wrist_px[0], wrist_px[1] - 10))

            # Draw angles for upper body
            cv.putText(frame_clean, elbow_text, elbow_pos,
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv.putText(frame_clean, wrist_text, wrist_pos,
                       cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Desenhar os eletrônicos detectados anteriormente
        frame_final = draw_electronics_detections(frame_clean, electronics_detections)

        if deve_continuar:
            output_path = os.path.join(output_folder, f"processed_{os.path.basename(input_path)}_{frame_idx}.jpg")
            cv.imwrite(output_path, frame_final)
            logger.info(f"Frame {frame_idx}: Imagem processada salva em: {output_path}")
        else:
            logger.warning("Processamento cancelado - arquivo não salvo")
            break

logger.info("Processamento finalizado")
print(f"\nProcessamento finalizado. Log detalhado salvo em: {log_file}")


def process_frames_parallel(frames):
    with Pool() as pool:
        return pool.map(process_single_frame, frames)