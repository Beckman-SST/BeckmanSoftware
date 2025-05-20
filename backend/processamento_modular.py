import cv2 as cv
import numpy as np
import sys
import os

# Importando os módulos criados
from modules import config
from modules import image_utils
from modules import pose_detection
from modules import electronics_detection
from modules import angle_calculation
from modules import parallel_processing

# Define a pasta de saída
output_folder = "Output"

# Verifica se a pasta já existe
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Pasta '{output_folder}' criada com sucesso.")
else:
    print(f"Pasta '{output_folder}' já existe. As imagens serão salvas nela.")

# Função para processar um único frame
def process_single_frame(frame):
    if not parallel_processing.should_continue():
        return None
        
    # Redimensiona o frame mantendo a proporção usando a largura configurada
    frame = image_utils.resize_with_aspect_ratio(frame, width=config.RESIZE_WIDTH)
    
    # Processamento com MediaPipe primeiro
    imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = pose_detection.holistic.process(imgRGB)
    
    # Aplicar suavização de landmarks
    results = pose_detection.process_landmarks(results, config.MOVING_AVERAGE_WINDOW)
    
    # Inicializa as variáveis
    landmarks = None
    wrist_position = None
    side = "right"  # valor padrão
    
    # Verifica se os landmarks principais foram detectados
    if not results.pose_landmarks:
        print("\nERRO: Não foi possível detectar os landmarks principais do corpo na imagem.")
        return frame
    
    # Verifica se há landmarks da pose
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        # Determina qual lado está mais visível e define a posição do pulso
        if landmarks:
            right_visibility = landmarks[pose_detection.mpHolistic.PoseLandmark.RIGHT_WRIST.value].visibility
            left_visibility = landmarks[pose_detection.mpHolistic.PoseLandmark.LEFT_WRIST.value].visibility
            
            side = "right" if right_visibility > left_visibility else "left"
            if side == "right":
                wrist_position = (int(landmarks[pose_detection.mpHolistic.PoseLandmark.RIGHT_WRIST.value].x * frame.shape[1]),
                                int(landmarks[pose_detection.mpHolistic.PoseLandmark.RIGHT_WRIST.value].y * frame.shape[0]))
            else:
                wrist_position = (int(landmarks[pose_detection.mpHolistic.PoseLandmark.LEFT_WRIST.value].x * frame.shape[1]),
                                int(landmarks[pose_detection.mpHolistic.PoseLandmark.LEFT_WRIST.value].y * frame.shape[0]))
    
    # Verificar se é análise da parte inferior do corpo
    is_lower_body = pose_detection.should_process_lower_body(results.pose_landmarks.landmark, config.PROCESS_LOWER_BODY) if results.pose_landmarks else False

    # Detectar objetos eletrônicos apenas se não for análise da parte inferior
    electronics_detections = electronics_detection.detect_electronics(frame, electronics_detection.yolo_model, wrist_position, is_lower_body)
    
    # Cria uma cópia limpa do frame para desenhar os landmarks
    frame_clean = frame.copy()

    # Verificar se os landmarks da face foram detectados e se a tarja está ativada
    if results.face_landmarks and config.SHOW_FACE_BLUR:
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
    elif config.SHOW_FACE_BLUR:
        print("Landmarks do rosto não detectados. Usando landmarks dos olhos da pose como alternativa.")

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape

            left_eye = (int(landmarks[pose_detection.mpHolistic.PoseLandmark.LEFT_EYE.value].x * w),
                        int(landmarks[pose_detection.mpHolistic.PoseLandmark.LEFT_EYE.value].y * h))
            right_eye = (int(landmarks[pose_detection.mpHolistic.PoseLandmark.RIGHT_EYE.value].x * w),
                         int(landmarks[pose_detection.mpHolistic.PoseLandmark.RIGHT_EYE.value].y * h))

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

    # Desenhar os landmarks da pose
    if results.pose_landmarks and landmarks:
        # Desenhar conexões personalizadas
        for connection in pose_detection.custom_pose_connections:
            start_idx, end_idx = connection
            if (config.SHOW_UPPER_BODY and start_idx < 23) or (config.SHOW_LOWER_BODY and start_idx >= 23):
                start_point = (int(landmarks[start_idx].x * frame.shape[1]), int(landmarks[start_idx].y * frame.shape[0]))
                end_point = (int(landmarks[end_idx].x * frame.shape[1]), int(landmarks[end_idx].y * frame.shape[0]))
                cv.line(frame_clean, start_point, end_point, (0, 255, 0), 2)
        
        # Desenhar os pontos dos landmarks
        for i, landmark in enumerate(landmarks):
            if (config.SHOW_UPPER_BODY and i < 23) or (config.SHOW_LOWER_BODY and i >= 23):
                x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                cv.circle(frame_clean, (x, y), 5, (255, 0, 0), -1)
        
        # Desenhar ângulos se configurado
        if config.SHOW_ANGLES:
            frame_clean = angle_calculation.draw_angles(frame_clean, landmarks, pose_detection.mpHolistic, 
                                                      config.SHOW_ANGLES, config.SHOW_UPPER_BODY, config.SHOW_LOWER_BODY)
    
    # Desenhar detecções de eletrônicos
    frame_clean = image_utils.draw_electronics_detections(frame_clean, electronics_detections, config.SHOW_ELECTRONICS)
    
    return frame_clean

# Função principal
def main():
    # Verifica se foi passado um argumento (caminho do arquivo)
    if len(sys.argv) < 2:
        print("Uso: python processamento.py <caminho_do_arquivo>")
        return
    
    # Obtém o caminho do arquivo passado como argumento
    input_path = sys.argv[1]
    
    # Verificar se o conteúdo é uma imagem
    image = cv.imread(input_path)
    is_image = image is not None
    
    if is_image:
        frames = [image]
    else:
        cap = cv.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Erro ao carregar o vídeo: {input_path}. Verifique o caminho e o arquivo.")
            return
        
        frames = []
        while cap.isOpened() and parallel_processing.should_continue():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
    
    # Processar frames em paralelo ou sequencialmente
    if len(frames) > 1:
        processed_frames = parallel_processing.process_frames_parallel(frames, process_single_frame)
    else:
        processed_frames = [process_single_frame(frame) for frame in frames]
    
    # Salvar resultados
    for i, processed_frame in enumerate(processed_frames):
        if processed_frame is None:
            continue
            
        if is_image:
            output_path = os.path.join(output_folder, f"processed_{os.path.basename(input_path)}")
            cv.imwrite(output_path, processed_frame)
            print(f"Imagem processada salva em: {output_path}")
        else:
            output_path = os.path.join(output_folder, f"frame_{i:04d}.jpg")
            cv.imwrite(output_path, processed_frame)
    
    if not is_image:
        print(f"Todos os frames processados foram salvos na pasta: {output_folder}")

# Executar o programa se for o script principal
if __name__ == "__main__":
    main()