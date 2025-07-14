# Documentação Técnica de Implementação

## Índice

1. [Arquitetura de Código](#arquitetura-de-código)
2. [Dependências](#dependências)
3. [Implementação de Componentes](#implementação-de-componentes)
   - [PoseDetector](#posedetector)
   - [AngleAnalyzer](#angleanalyzer)
   - [VideoVisualizer](#videovisualizer)
   - [VideoProcessor](#videoprocessor)
4. [Fluxo de Dados](#fluxo-de-dados)
5. [Algoritmos Principais](#algoritmos-principais)
6. [Otimizações](#otimizações)
7. [Tratamento de Erros](#tratamento-de-erros)
8. [Extensibilidade](#extensibilidade)
9. [Referências Técnicas](#referências-técnicas)

## Arquitetura de Código

O sistema de processamento de vídeos é organizado em uma arquitetura modular, com os seguintes módulos principais:

### Módulo `detection`

Responsável pela detecção de pose usando MediaPipe. Contém a classe `PoseDetector` que encapsula a funcionalidade de detecção de landmarks do corpo.

### Módulo `analysis`

Responsável pela análise de ângulos entre articulações. Contém a classe `AngleAnalyzer` que implementa métodos para calcular e avaliar ângulos entre landmarks.

### Módulo `visualization`

Responsável pela visualização dos resultados da análise. Contém a classe `VideoVisualizer` que implementa métodos para desenhar landmarks, conexões e ângulos no vídeo.

### Módulo `processors`

Responsável pelo processamento de vídeos. Contém a classe `VideoProcessor` que coordena todo o fluxo de processamento, desde a leitura do vídeo até a escrita do vídeo processado.

### Módulo `core`

Contém funções e classes utilitárias usadas por outros módulos, como funções para cálculo de ângulos, conversão de coordenadas, etc.

## Dependências

O sistema depende das seguintes bibliotecas externas:

- **OpenCV**: Para processamento de imagens e vídeos.
- **MediaPipe**: Para detecção de pose.
- **NumPy**: Para operações matemáticas e manipulação de arrays.
- **multiprocessing**: Para processamento paralelo de frames.

## Implementação de Componentes

### PoseDetector

A classe `PoseDetector` encapsula a funcionalidade de detecção de pose usando MediaPipe. Ela é responsável por detectar landmarks do corpo em frames de vídeo.

```python
class PoseDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5, moving_average_window=3):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.moving_average_window = moving_average_window
        self.landmark_history = []
        
    def detect_pose(self, frame):
        # Converter BGR para RGB (MediaPipe usa RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Processar o frame com MediaPipe
        results = self.pose.process(frame_rgb)
        
        # Aplicar suavização de landmarks se configurado
        if results.pose_landmarks and self.moving_average_window > 1:
            self._apply_landmark_smoothing(results)
            
        return results
    
    def _apply_landmark_smoothing(self, results):
        # Implementação da suavização de landmarks usando média móvel
        current_landmarks = [(lm.x, lm.y, lm.z, lm.visibility) for lm in results.pose_landmarks.landmark]
        
        self.landmark_history.append(current_landmarks)
        if len(self.landmark_history) > self.moving_average_window:
            self.landmark_history.pop(0)
        
        # Calcular média móvel para cada landmark
        avg_landmarks = []
        for i in range(len(current_landmarks)):
            x_avg = sum(history[i][0] for history in self.landmark_history) / len(self.landmark_history)
            y_avg = sum(history[i][1] for history in self.landmark_history) / len(self.landmark_history)
            z_avg = sum(history[i][2] for history in self.landmark_history) / len(self.landmark_history)
            v_avg = sum(history[i][3] for history in self.landmark_history) / len(self.landmark_history)
            
            results.pose_landmarks.landmark[i].x = x_avg
            results.pose_landmarks.landmark[i].y = y_avg
            results.pose_landmarks.landmark[i].z = z_avg
            results.pose_landmarks.landmark[i].visibility = v_avg
```

### AngleAnalyzer

A classe `AngleAnalyzer` implementa métodos para calcular e avaliar ângulos entre landmarks. Ela utiliza funções do módulo `core` para cálculos matemáticos.

```python
class AngleAnalyzer:
    def __init__(self):
        pass
    
    def calculate_angle(self, a, b, c):
        # Calcular ângulo entre três pontos
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def calculate_angle_with_vertical(self, a, b):
        # Calcular ângulo com a vertical
        a = np.array(a)
        b = np.array(b)
        
        vector = b - a
        vertical = np.array([0, -1])  # Vetor vertical para cima
        
        cosine_angle = np.dot(vector, vertical) / (np.linalg.norm(vector) * np.linalg.norm(vertical))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def calculate_spine_angle(self, landmarks, use_vertical_reference=True):
        # Calcular ângulo da coluna
        if not self._check_landmarks(landmarks, [11, 12, 23, 24]):
            return None
        
        # Calcular ponto médio dos ombros
        shoulders_mid = (
            (landmarks[11][0] + landmarks[12][0]) / 2,
            (landmarks[11][1] + landmarks[12][1]) / 2
        )
        
        # Calcular ponto médio dos quadris
        hips_mid = (
            (landmarks[23][0] + landmarks[24][0]) / 2,
            (landmarks[23][1] + landmarks[24][1]) / 2
        )
        
        if use_vertical_reference:
            # Calcular ângulo com a vertical
            angle = self.calculate_angle_with_vertical(hips_mid, shoulders_mid)
        else:
            # Calcular ângulo interno (não implementado neste exemplo)
            angle = 0
        
        return angle
    
    def evaluate_spine_angle(self, angle):
        # Avaliar ângulo da coluna
        if angle is None:
            return None
        
        if angle <= 5:
            return 1  # Verde - Postura excelente
        elif angle <= 10:
            return 2  # Amarelo - Postura com atenção
        else:
            return 3  # Vermelho - Postura ruim
    
    def calculate_shoulder_angle(self, landmarks, side='right'):
        # Calcular ângulo do ombro
        if side == 'right':
            if not self._check_landmarks(landmarks, [12, 14]):
                return None
            shoulder = landmarks[12]
            elbow = landmarks[14]
        else:  # left
            if not self._check_landmarks(landmarks, [11, 13]):
                return None
            shoulder = landmarks[11]
            elbow = landmarks[13]
        
        # Calcular ângulo com a vertical
        angle = self.calculate_angle_with_vertical(shoulder, elbow)
        
        # Verificar se o braço está em abdução (para o lado)
        if side == 'right':
            if not self._check_landmarks(landmarks, [11]):
                return angle
            other_shoulder = landmarks[11]
        else:  # left
            if not self._check_landmarks(landmarks, [12]):
                return angle
            other_shoulder = landmarks[12]
        
        # Se o cotovelo está mais para fora que o ombro, considerar como abdução
        if (side == 'right' and elbow[0] > shoulder[0]) or (side == 'left' and elbow[0] < shoulder[0]):
            # Calcular vetor do ombro para o cotovelo
            vector = (elbow[0] - shoulder[0], elbow[1] - shoulder[1])
            
            # Calcular vetor entre os ombros
            shoulder_vector = (other_shoulder[0] - shoulder[0], other_shoulder[1] - shoulder[1])
            
            # Calcular ângulo entre os vetores
            cosine_angle = np.dot(vector, shoulder_vector) / (np.linalg.norm(vector) * np.linalg.norm(shoulder_vector))
            abdution_angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
            
            # Usar o ângulo de abdução se for maior que o ângulo com a vertical
            if abdution_angle > angle:
                angle = abdution_angle
        
        return angle
    
    def evaluate_shoulder_angle(self, angle):
        # Avaliar ângulo do ombro
        if angle is None:
            return None
        
        if angle <= 20:
            return 1  # Verde - Nível 1
        elif angle <= 45:
            return 2  # Amarelo - Nível 2
        elif angle <= 90:
            return 3  # Laranja - Nível 3
        else:
            return 4  # Vermelho - Nível 4
    
    def calculate_forearm_angle(self, landmarks, side='right'):
        # Calcular ângulo do cotovelo/antebraço
        if side == 'right':
            if not self._check_landmarks(landmarks, [12, 14, 16]):
                return None
            shoulder = landmarks[12]
            elbow = landmarks[14]
            wrist = landmarks[16]
        else:  # left
            if not self._check_landmarks(landmarks, [11, 13, 15]):
                return None
            shoulder = landmarks[11]
            elbow = landmarks[13]
            wrist = landmarks[15]
        
        # Calcular ângulo entre ombro, cotovelo e pulso
        angle = self.calculate_angle(shoulder, elbow, wrist)
        
        return angle
    
    def evaluate_forearm_angle(self, angle):
        # Avaliar ângulo do cotovelo/antebraço
        if angle is None:
            return None
        
        if 60 <= angle <= 100:
            return 1  # Verde - Nível 1
        else:
            return 2  # Amarelo - Nível 2
    
    def calculate_knee_angle(self, landmarks, side='right'):
        # Calcular ângulo do joelho
        if side == 'right':
            if not self._check_landmarks(landmarks, [24, 26, 28]):
                return None
            hip = landmarks[24]
            knee = landmarks[26]
            ankle = landmarks[28]
        else:  # left
            if not self._check_landmarks(landmarks, [23, 25, 27]):
                return None
            hip = landmarks[23]
            knee = landmarks[25]
            ankle = landmarks[27]
        
        # Calcular ângulo entre quadril, joelho e tornozelo
        angle = self.calculate_angle(hip, knee, ankle)
        
        return angle
    
    def evaluate_knee_angle(self, angle):
        # Avaliar ângulo do joelho usando critérios de Suzanne Rodgers
        if angle is None:
            return None
        
        if 160 <= angle <= 180:
            return 1  # Verde - Baixo Esforço (Nível 1)
        elif 45 <= angle <= 80 or 80 < angle < 160:
            return 2  # Amarelo - Moderado Esforço (Nível 2)
        else:  # angle < 45
            return 3  # Vermelho - Alto/Muito Alto Esforço (Nível 3+)
    
    def _check_landmarks(self, landmarks, indices):
        # Verificar se os landmarks necessários estão disponíveis
        for idx in indices:
            if idx not in landmarks or landmarks[idx] is None:
                return False
        return True
```

### VideoVisualizer

A classe `VideoVisualizer` implementa métodos para desenhar landmarks, conexões e ângulos no vídeo. Ela utiliza funções do OpenCV para desenho.

```python
class VideoVisualizer:
    def __init__(self, angle_analyzer):
        self.angle_analyzer = angle_analyzer
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        
        # Definir cores para níveis de risco
        self.colors = {
            1: (0, 255, 0),    # Verde - Baixo risco
            2: (0, 255, 255),  # Amarelo - Risco moderado
            3: (0, 165, 255),  # Laranja - Alto risco
            4: (0, 0, 255)     # Vermelho - Muito alto risco
        }
    
    def draw_video_landmarks(self, frame, results, show_upper_body=True, show_lower_body=True):
        # Desenhar landmarks e conexões
        if not results.pose_landmarks:
            return frame
        
        # Criar cópia do frame para desenho
        annotated_frame = frame.copy()
        
        # Definir quais landmarks desenhar com base nas configurações
        connections = []
        if show_upper_body:
            connections.extend([
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
                (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_ELBOW),
                (self.mp_pose.PoseLandmark.LEFT_ELBOW, self.mp_pose.PoseLandmark.LEFT_WRIST),
                (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_ELBOW),
                (self.mp_pose.PoseLandmark.RIGHT_ELBOW, self.mp_pose.PoseLandmark.RIGHT_WRIST),
                # Adicionar mais conexões do corpo superior conforme necessário
            ])
        
        if show_lower_body:
            connections.extend([
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.RIGHT_HIP),
                (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.LEFT_KNEE),
                (self.mp_pose.PoseLandmark.LEFT_KNEE, self.mp_pose.PoseLandmark.LEFT_ANKLE),
                (self.mp_pose.PoseLandmark.RIGHT_HIP, self.mp_pose.PoseLandmark.RIGHT_KNEE),
                (self.mp_pose.PoseLandmark.RIGHT_KNEE, self.mp_pose.PoseLandmark.RIGHT_ANKLE),
                # Adicionar mais conexões do corpo inferior conforme necessário
            ])
        
        # Desenhar conexões personalizadas
        h, w, _ = frame.shape
        landmarks_dict = {}
        
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks_dict[idx] = (int(landmark.x * w), int(landmark.y * h))
        
        for connection in connections:
            start_idx = connection[0].value
            end_idx = connection[1].value
            
            if start_idx in landmarks_dict and end_idx in landmarks_dict:
                cv2.line(annotated_frame, landmarks_dict[start_idx], landmarks_dict[end_idx], (255, 255, 255), 2)
        
        # Desenhar landmarks
        for idx, point in landmarks_dict.items():
            cv2.circle(annotated_frame, point, 5, (0, 255, 0), -1)
        
        return annotated_frame, landmarks_dict
    
    def draw_spine_angle(self, frame, landmarks_dict, use_vertical_reference=True):
        # Desenhar ângulo da coluna
        angle = self.angle_analyzer.calculate_spine_angle(landmarks_dict, use_vertical_reference)
        if angle is None:
            return frame
        
        # Avaliar ângulo
        risk_level = self.angle_analyzer.evaluate_spine_angle(angle)
        color = self.colors.get(risk_level, (255, 255, 255))  # Branco como fallback
        
        # Calcular pontos para desenho
        shoulders_mid = (
            int((landmarks_dict[11][0] + landmarks_dict[12][0]) / 2),
            int((landmarks_dict[11][1] + landmarks_dict[12][1]) / 2)
        )
        
        hips_mid = (
            int((landmarks_dict[23][0] + landmarks_dict[24][0]) / 2),
            int((landmarks_dict[23][1] + landmarks_dict[24][1]) / 2)
        )
        
        # Desenhar linha da coluna
        cv2.line(frame, shoulders_mid, hips_mid, color, 2)
        
        # Desenhar ângulo
        text_pos = self._adjust_text_position(shoulders_mid, 10, 30)
        cv2.putText(frame, f"Coluna: {angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def draw_shoulder_angle(self, frame, landmarks_dict, side='right'):
        # Desenhar ângulo do ombro
        angle = self.angle_analyzer.calculate_shoulder_angle(landmarks_dict, side)
        if angle is None:
            return frame
        
        # Avaliar ângulo
        risk_level = self.angle_analyzer.evaluate_shoulder_angle(angle)
        color = self.colors.get(risk_level, (255, 255, 255))  # Branco como fallback
        
        # Obter pontos para desenho
        if side == 'right':
            shoulder = landmarks_dict[12]
            elbow = landmarks_dict[14]
        else:  # left
            shoulder = landmarks_dict[11]
            elbow = landmarks_dict[13]
        
        # Desenhar linha do ombro
        cv2.line(frame, shoulder, elbow, color, 2)
        
        # Desenhar ângulo
        text_pos = self._adjust_text_position(shoulder, 10, -10)
        cv2.putText(frame, f"Ombro {side}: {angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def draw_forearm_angle(self, frame, landmarks_dict, side='right'):
        # Desenhar ângulo do cotovelo/antebraço
        angle = self.angle_analyzer.calculate_forearm_angle(landmarks_dict, side)
        if angle is None:
            return frame
        
        # Avaliar ângulo
        risk_level = self.angle_analyzer.evaluate_forearm_angle(angle)
        color = self.colors.get(risk_level, (255, 255, 255))  # Branco como fallback
        
        # Obter pontos para desenho
        if side == 'right':
            shoulder = landmarks_dict[12]
            elbow = landmarks_dict[14]
            wrist = landmarks_dict[16]
        else:  # left
            shoulder = landmarks_dict[11]
            elbow = landmarks_dict[13]
            wrist = landmarks_dict[15]
        
        # Desenhar linhas do cotovelo
        cv2.line(frame, elbow, shoulder, color, 2)
        cv2.line(frame, elbow, wrist, color, 2)
        
        # Desenhar ângulo
        text_pos = self._adjust_text_position(elbow, 10, 10)
        cv2.putText(frame, f"Cotovelo {side}: {angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def draw_knee_angle(self, frame, landmarks_dict, side='right'):
        # Desenhar ângulo do joelho
        angle = self.angle_analyzer.calculate_knee_angle(landmarks_dict, side)
        if angle is None:
            return frame
        
        # Avaliar ângulo
        risk_level = self.angle_analyzer.evaluate_knee_angle(angle)
        color = self.colors.get(risk_level, (255, 255, 255))  # Branco como fallback
        
        # Obter pontos para desenho
        if side == 'right':
            hip = landmarks_dict[24]
            knee = landmarks_dict[26]
            ankle = landmarks_dict[28]
        else:  # left
            hip = landmarks_dict[23]
            knee = landmarks_dict[25]
            ankle = landmarks_dict[27]
        
        # Desenhar linhas do joelho
        cv2.line(frame, knee, hip, color, 2)
        cv2.line(frame, knee, ankle, color, 2)
        
        # Desenhar ângulo
        text_pos = self._adjust_text_position(knee, 10, 10)
        cv2.putText(frame, f"Joelho {side}: {angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def _adjust_text_position(self, point, offset_x, offset_y):
        # Ajustar posição do texto para evitar sobreposição
        return (point[0] + offset_x, point[1] + offset_y)
```

### VideoProcessor

A classe `VideoProcessor` coordena todo o fluxo de processamento de vídeos, desde a leitura do vídeo até a escrita do vídeo processado.

```python
class VideoProcessor:
    def __init__(self, pose_detector, angle_analyzer, visualizer, config=None):
        self.pose_detector = pose_detector
        self.angle_analyzer = angle_analyzer
        self.visualizer = visualizer
        
        # Configurações padrão
        self.config = {
            'resize_width': 640,
            'resize_height': 480,
            'show_upper_body': True,
            'show_lower_body': True,
            'apply_face_blur': True
        }
        
        # Atualizar configurações se fornecidas
        if config:
            self.config.update(config)
    
    def process_video(self, video_path, output_folder, progress_callback=None):
        # Processar vídeo sequencialmente
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
        
        # Obter propriedades do vídeo
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Criar diretório de saída se não existir
        os.makedirs(output_folder, exist_ok=True)
        
        # Definir nome do arquivo de saída
        video_name = os.path.basename(video_path)
        output_path = os.path.join(output_folder, f"processed_{video_name}")
        
        # Configurar writer para o vídeo de saída
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec para MP4
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Processar frame
            processed_frame = self._process_frame(frame)
            
            # Escrever frame processado
            out.write(processed_frame)
            
            # Atualizar contador e callback de progresso
            frame_count += 1
            if progress_callback and frame_count % 10 == 0:  # Atualizar a cada 10 frames
                progress_callback(frame_count / total_frames * 100)
        
        # Liberar recursos
        cap.release()
        out.release()
        
        return output_path
    
    def process_video_parallel(self, video_path, output_folder, num_workers=4, progress_callback=None):
        # Processar vídeo em paralelo usando múltiplos workers
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")
        
        # Obter propriedades do vídeo
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Criar diretório de saída se não existir
        os.makedirs(output_folder, exist_ok=True)
        
        # Definir nome do arquivo de saída
        video_name = os.path.basename(video_path)
        output_path = os.path.join(output_folder, f"processed_{video_name}")
        
        # Configurar writer para o vídeo de saída
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec para MP4
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # Dividir o vídeo em chunks para processamento paralelo
        chunk_size = total_frames // num_workers
        chunks = []
        
        for i in range(num_workers):
            start_frame = i * chunk_size
            end_frame = (i + 1) * chunk_size if i < num_workers - 1 else total_frames
            chunks.append((start_frame, end_frame))
        
        # Criar pool de processos
        with multiprocessing.Pool(processes=num_workers) as pool:
            # Mapear chunks para workers
            results = pool.starmap(
                self._process_video_chunk,
                [(video_path, chunk, i) for i, chunk in enumerate(chunks)]
            )
        
        # Ordenar resultados por índice de chunk
        results.sort(key=lambda x: x[0])
        
        # Escrever frames processados no vídeo de saída
        for _, frames in results:
            for frame in frames:
                out.write(frame)
        
        # Liberar recursos
        cap.release()
        out.release()
        
        return output_path
    
    def _process_video_chunk(self, video_path, chunk, chunk_idx):
        # Processar um chunk do vídeo
        start_frame, end_frame = chunk
        
        cap = cv2.VideoCapture(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        
        frames = []
        frame_count = start_frame
        
        while frame_count < end_frame and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Processar frame
            processed_frame = self._process_frame(frame)
            frames.append(processed_frame)
            
            frame_count += 1
        
        cap.release()
        
        return chunk_idx, frames
    
    def _process_frame(self, frame):
        # Processar um frame do vídeo
        original_height, original_width = frame.shape[:2]
        
        # Redimensionar frame mantendo proporção
        if self.config['resize_width'] and self.config['resize_height']:
            scale = min(self.config['resize_width'] / original_width, self.config['resize_height'] / original_height)
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            frame_resized = cv2.resize(frame, (new_width, new_height))
        else:
            frame_resized = frame
            new_width, new_height = original_width, original_height
        
        # Detectar pose
        results = self.pose_detector.detect_pose(frame_resized)
        
        # Se não detectou pose, retornar frame original
        if not results.pose_landmarks:
            return frame
        
        # Converter landmarks para coordenadas de pixel
        frame_annotated, landmarks_dict = self.visualizer.draw_video_landmarks(
            frame_resized, 
            results, 
            show_upper_body=self.config['show_upper_body'],
            show_lower_body=self.config['show_lower_body']
        )
        
        # Aplicar tarja no rosto se configurado
        if self.config['apply_face_blur'] and 0 in landmarks_dict and 1 in landmarks_dict:
            # Calcular região do rosto
            face_landmarks = [landmarks_dict[i] for i in range(10) if i in landmarks_dict]
            if face_landmarks:
                x_min = min(point[0] for point in face_landmarks)
                y_min = min(point[1] for point in face_landmarks)
                x_max = max(point[0] for point in face_landmarks)
                y_max = max(point[1] for point in face_landmarks)
                
                # Adicionar margem
                margin = 20
                x_min = max(0, x_min - margin)
                y_min = max(0, y_min - margin)
                x_max = min(new_width, x_max + margin)
                y_max = min(new_height, y_max + margin)
                
                # Aplicar tarja
                cv2.rectangle(frame_annotated, (x_min, y_min), (x_max, y_max), (0, 0, 0), -1)
        
        # Desenhar ângulos
        if self.config['show_upper_body']:
            # Desenhar ângulo da coluna
            frame_annotated = self.visualizer.draw_spine_angle(frame_annotated, landmarks_dict)
            
            # Desenhar ângulos dos ombros
            frame_annotated = self.visualizer.draw_shoulder_angle(frame_annotated, landmarks_dict, 'right')
            frame_annotated = self.visualizer.draw_shoulder_angle(frame_annotated, landmarks_dict, 'left')
            
            # Desenhar ângulos dos cotovelos
            frame_annotated = self.visualizer.draw_forearm_angle(frame_annotated, landmarks_dict, 'right')
            frame_annotated = self.visualizer.draw_forearm_angle(frame_annotated, landmarks_dict, 'left')
        
        if self.config['show_lower_body']:
            # Desenhar ângulos dos joelhos
            frame_annotated = self.visualizer.draw_knee_angle(frame_annotated, landmarks_dict, 'right')
            frame_annotated = self.visualizer.draw_knee_angle(frame_annotated, landmarks_dict, 'left')
        
        # Redimensionar de volta para o tamanho original se necessário
        if new_width != original_width or new_height != original_height:
            frame_annotated = cv2.resize(frame_annotated, (original_width, original_height))
        
        return frame_annotated
```

## Fluxo de Dados

O fluxo de dados no sistema segue estas etapas:

1. **Entrada**: O vídeo é lido frame a frame usando OpenCV.
2. **Detecção**: Cada frame é processado pelo `PoseDetector` para detectar landmarks do corpo.
3. **Análise**: Os landmarks detectados são analisados pelo `AngleAnalyzer` para calcular ângulos entre articulações.
4. **Visualização**: Os resultados da análise são visualizados pelo `VideoVisualizer`, que desenha landmarks, conexões e ângulos no frame.
5. **Saída**: O frame processado é escrito no vídeo de saída.

O fluxo pode ser sequencial ou paralelo, dependendo do método de processamento escolhido.

## Algoritmos Principais

### Cálculo de Ângulo entre Três Pontos

O algoritmo para calcular o ângulo entre três pontos (A, B, C) é implementado no método `calculate_angle` da classe `AngleAnalyzer`:

```python
def calculate_angle(self, a, b, c):
    # Calcular ângulo entre três pontos
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)
```

O algoritmo calcula o ângulo entre os vetores BA e BC usando o produto escalar e a lei dos cossenos.

### Cálculo de Ângulo com a Vertical

O algoritmo para calcular o ângulo com a vertical é implementado no método `calculate_angle_with_vertical` da classe `AngleAnalyzer`:

```python
def calculate_angle_with_vertical(self, a, b):
    # Calcular ângulo com a vertical
    a = np.array(a)
    b = np.array(b)
    
    vector = b - a
    vertical = np.array([0, -1])  # Vetor vertical para cima
    
    cosine_angle = np.dot(vector, vertical) / (np.linalg.norm(vector) * np.linalg.norm(vertical))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    
    return np.degrees(angle)
```

O algoritmo calcula o ângulo entre o vetor AB e o vetor vertical [0, -1] usando o produto escalar.

### Ajuste de Posição de Texto

O algoritmo para ajustar a posição do texto é implementado no método `_adjust_text_position` da classe `VideoVisualizer`:

```python
def _adjust_text_position(self, point, offset_x, offset_y):
    # Ajustar posição do texto para evitar sobreposição
    return (point[0] + offset_x, point[1] + offset_y)
```

O algoritmo ajusta a posição do texto para evitar sobreposição com outros elementos do vídeo.

## Otimizações

O sistema implementa várias otimizações para melhorar o desempenho e a qualidade dos resultados:

### Processamento Paralelo

O método `process_video_parallel` da classe `VideoProcessor` implementa processamento paralelo de frames usando a biblioteca `multiprocessing`. O vídeo é dividido em chunks, que são processados em paralelo por múltiplos workers.

### Redimensionamento de Frames

O método `_process_frame` da classe `VideoProcessor` implementa redimensionamento de frames para melhorar o desempenho. Os frames são redimensionados mantendo a proporção antes do processamento e redimensionados de volta para o tamanho original após o processamento.

### Suavização de Landmarks

A classe `PoseDetector` implementa suavização de landmarks usando média móvel. Isso ajuda a reduzir o ruído e melhorar a estabilidade dos landmarks detectados.

### Verificação de Landmarks

O método `_check_landmarks` da classe `AngleAnalyzer` verifica se os landmarks necessários para o cálculo de ângulos estão disponíveis. Isso evita erros quando landmarks não são detectados corretamente.

## Tratamento de Erros

O sistema implementa tratamento de erros em vários níveis:

### Verificação de Entrada

O método `process_video` da classe `VideoProcessor` verifica se o vídeo de entrada pode ser aberto antes de iniciar o processamento.

### Verificação de Landmarks

O método `_check_landmarks` da classe `AngleAnalyzer` verifica se os landmarks necessários para o cálculo de ângulos estão disponíveis. Se não estiverem, o método retorna `None` e o sistema continua o processamento sem calcular o ângulo.

### Tratamento de Frames sem Detecção

O método `_process_frame` da classe `VideoProcessor` verifica se a pose foi detectada no frame. Se não foi, o método retorna o frame original sem processamento adicional.

## Extensibilidade

O sistema foi projetado para ser facilmente extensível:

### Adição de Novos Ângulos

Para adicionar um novo ângulo, basta implementar novos métodos na classe `AngleAnalyzer` para calcular e avaliar o ângulo, e novos métodos na classe `VideoVisualizer` para desenhar o ângulo.

### Adição de Novos Critérios de Avaliação

Para adicionar novos critérios de avaliação, basta modificar os métodos de avaliação na classe `AngleAnalyzer` para usar os novos critérios.

### Adição de Novas Visualizações

Para adicionar novas visualizações, basta implementar novos métodos na classe `VideoVisualizer` para desenhar os elementos desejados.

## Referências Técnicas

### OpenCV

OpenCV é uma biblioteca de visão computacional de código aberto que fornece ferramentas para processamento de imagens e vídeos. O sistema utiliza OpenCV para leitura e escrita de vídeos, desenho de elementos visuais e manipulação de imagens.

### MediaPipe

MediaPipe é uma biblioteca de código aberto desenvolvida pelo Google que fornece soluções para detecção de pose, face, mãos e outros elementos em imagens e vídeos. O sistema utiliza MediaPipe Pose para detecção de landmarks do corpo.

### NumPy

NumPy é uma biblioteca de código aberto para computação científica em Python. O sistema utiliza NumPy para operações matemáticas e manipulação de arrays.

### Multiprocessing

Multiprocessing é uma biblioteca padrão do Python que fornece suporte para processamento paralelo. O sistema utiliza Multiprocessing para implementar processamento paralelo de frames.