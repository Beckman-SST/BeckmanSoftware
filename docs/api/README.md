# Documentação da API do Sistema de Processamento de Vídeos

## Visão Geral

Esta seção documenta a API do Sistema de Processamento de Vídeos, incluindo classes, métodos e parâmetros. A API é projetada para ser modular e extensível, permitindo que os desenvolvedores utilizem componentes individuais ou o sistema completo.

## Módulos

### Módulo de Detecção (`detection`)

#### Classe `PoseDetector`

```python
class PoseDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1, smoothing_window=5):
        """
        Inicializa o detector de pose.
        
        Args:
            min_detection_confidence (float): Confiança mínima para detecção (0.0-1.0).
            min_tracking_confidence (float): Confiança mínima para rastreamento (0.0-1.0).
            model_complexity (int): Complexidade do modelo (0, 1 ou 2).
            smoothing_window (int): Tamanho da janela para suavização de landmarks.
        """
        pass
    
    def detect_pose(self, frame):
        """
        Detecta landmarks de pose em um frame.
        
        Args:
            frame (numpy.ndarray): Frame de vídeo.
            
        Returns:
            tuple: (landmarks, frame_with_landmarks)
                landmarks: Lista de landmarks detectados.
                frame_with_landmarks: Frame com landmarks desenhados.
        """
        pass
    
    def get_landmark_coordinates(self, landmarks, frame_shape):
        """
        Converte landmarks para coordenadas de pixel.
        
        Args:
            landmarks (list): Lista de landmarks detectados.
            frame_shape (tuple): Forma do frame (altura, largura).
            
        Returns:
            dict: Dicionário de coordenadas de landmarks.
        """
        pass
    
    def smooth_landmarks(self, landmarks):
        """
        Aplica suavização aos landmarks.
        
        Args:
            landmarks (dict): Dicionário de coordenadas de landmarks.
            
        Returns:
            dict: Dicionário de coordenadas de landmarks suavizados.
        """
        pass
```

### Módulo de Análise (`analysis`)

#### Classe `AngleAnalyzer`

```python
class AngleAnalyzer:
    def __init__(self):
        """
        Inicializa o analisador de ângulos.
        """
        pass
    
    def calculate_angle(self, a, b, c):
        """
        Calcula o ângulo entre três pontos.
        
        Args:
            a (tuple): Coordenadas do primeiro ponto (x, y).
            b (tuple): Coordenadas do segundo ponto (x, y).
            c (tuple): Coordenadas do terceiro ponto (x, y).
            
        Returns:
            float: Ângulo em graus.
        """
        pass
    
    def calculate_vertical_angle(self, a, b):
        """
        Calcula o ângulo entre dois pontos e a vertical.
        
        Args:
            a (tuple): Coordenadas do primeiro ponto (x, y).
            b (tuple): Coordenadas do segundo ponto (x, y).
            
        Returns:
            float: Ângulo em graus.
        """
        pass
    
    def evaluate_spine_angle(self, landmarks):
        """
        Avalia o ângulo da coluna.
        
        Args:
            landmarks (dict): Dicionário de coordenadas de landmarks.
            
        Returns:
            tuple: (angle, score, color)
                angle: Ângulo em graus.
                score: Pontuação (1-3).
                color: Cor (BGR).
        """
        pass
    
    def evaluate_shoulder_angle(self, landmarks, side="right"):
        """
        Avalia o ângulo do ombro.
        
        Args:
            landmarks (dict): Dicionário de coordenadas de landmarks.
            side (str): Lado do corpo ("right" ou "left").
            
        Returns:
            tuple: (angle, score, color)
                angle: Ângulo em graus.
                score: Pontuação (1-3).
                color: Cor (BGR).
        """
        pass
    
    def evaluate_elbow_angle(self, landmarks, side="right"):
        """
        Avalia o ângulo do cotovelo.
        
        Args:
            landmarks (dict): Dicionário de coordenadas de landmarks.
            side (str): Lado do corpo ("right" ou "left").
            
        Returns:
            tuple: (angle, score, color)
                angle: Ângulo em graus.
                score: Pontuação (1-3).
                color: Cor (BGR).
        """
        pass
    
    def evaluate_wrist_angle(self, landmarks, side="right"):
        """
        Avalia o ângulo do pulso.
        
        Args:
            landmarks (dict): Dicionário de coordenadas de landmarks.
            side (str): Lado do corpo ("right" ou "left").
            
        Returns:
            tuple: (angle, score, color)
                angle: Ângulo em graus.
                score: Pontuação (1-3).
                color: Cor (BGR).
        """
        pass
    
    def evaluate_knee_angle(self, landmarks, side="right"):
        """
        Avalia o ângulo do joelho.
        
        Args:
            landmarks (dict): Dicionário de coordenadas de landmarks.
            side (str): Lado do corpo ("right" ou "left").
            
        Returns:
            tuple: (angle, score, color)
                angle: Ângulo em graus.
                score: Pontuação (1-3).
                color: Cor (BGR).
        """
        pass
    
    def evaluate_ankle_angle(self, landmarks, side="right"):
        """
        Avalia o ângulo do tornozelo.
        
        Args:
            landmarks (dict): Dicionário de coordenadas de landmarks.
            side (str): Lado do corpo ("right" ou "left").
            
        Returns:
            tuple: (angle, score, color)
                angle: Ângulo em graus.
                score: Pontuação (1-3).
                color: Cor (BGR).
        """
        pass
```

### Módulo de Visualização (`visualization`)

#### Classe `VideoVisualizer`

```python
class VideoVisualizer:
    def __init__(self, show_landmarks=True, show_connections=True, show_angles=True, blur_face=True):
        """
        Inicializa o visualizador de vídeo.
        
        Args:
            show_landmarks (bool): Se deve mostrar landmarks.
            show_connections (bool): Se deve mostrar conexões entre landmarks.
            show_angles (bool): Se deve mostrar ângulos.
            blur_face (bool): Se deve aplicar tarja no rosto.
        """
        pass
    
    def draw_landmarks(self, frame, landmarks, show_upper_body=True, show_lower_body=True):
        """
        Desenha landmarks no frame.
        
        Args:
            frame (numpy.ndarray): Frame de vídeo.
            landmarks (dict): Dicionário de coordenadas de landmarks.
            show_upper_body (bool): Se deve mostrar parte superior do corpo.
            show_lower_body (bool): Se deve mostrar parte inferior do corpo.
            
        Returns:
            numpy.ndarray: Frame com landmarks desenhados.
        """
        pass
    
    def draw_connections(self, frame, landmarks, show_upper_body=True, show_lower_body=True):
        """
        Desenha conexões entre landmarks no frame.
        
        Args:
            frame (numpy.ndarray): Frame de vídeo.
            landmarks (dict): Dicionário de coordenadas de landmarks.
            show_upper_body (bool): Se deve mostrar parte superior do corpo.
            show_lower_body (bool): Se deve mostrar parte inferior do corpo.
            
        Returns:
            numpy.ndarray: Frame com conexões desenhadas.
        """
        pass
    
    def draw_angle(self, frame, angle_point, angle_text, color):
        """
        Desenha ângulo no frame.
        
        Args:
            frame (numpy.ndarray): Frame de vídeo.
            angle_point (tuple): Coordenadas do ponto do ângulo (x, y).
            angle_text (str): Texto do ângulo.
            color (tuple): Cor (BGR).
            
        Returns:
            numpy.ndarray: Frame com ângulo desenhado.
        """
        pass
    
    def blur_face_region(self, frame, landmarks):
        """
        Aplica tarja no rosto.
        
        Args:
            frame (numpy.ndarray): Frame de vídeo.
            landmarks (dict): Dicionário de coordenadas de landmarks.
            
        Returns:
            numpy.ndarray: Frame com tarja no rosto.
        """
        pass
```

### Módulo de Processamento (`processors`)

#### Classe `VideoProcessor`

```python
class VideoProcessor:
    def __init__(self, input_path, output_path, process_resolution=(640, 480), output_resolution=None,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=1,
                 smoothing_window=5, show_upper_body=True, show_lower_body=True,
                 show_angles=True, show_landmarks=True, show_connections=True,
                 blur_face=True, parallel_processing=False, num_processes=None, chunk_size=100):
        """
        Inicializa o processador de vídeo.
        
        Args:
            input_path (str): Caminho para o vídeo de entrada.
            output_path (str): Caminho para o vídeo de saída.
            process_resolution (tuple): Resolução de processamento (largura, altura).
            output_resolution (tuple): Resolução de saída (largura, altura). Se None, usa a mesma da entrada.
            min_detection_confidence (float): Confiança mínima para detecção (0.0-1.0).
            min_tracking_confidence (float): Confiança mínima para rastreamento (0.0-1.0).
            model_complexity (int): Complexidade do modelo (0, 1 ou 2).
            smoothing_window (int): Tamanho da janela para suavização de landmarks.
            show_upper_body (bool): Se deve mostrar parte superior do corpo.
            show_lower_body (bool): Se deve mostrar parte inferior do corpo.
            show_angles (bool): Se deve mostrar ângulos.
            show_landmarks (bool): Se deve mostrar landmarks.
            show_connections (bool): Se deve mostrar conexões entre landmarks.
            blur_face (bool): Se deve aplicar tarja no rosto.
            parallel_processing (bool): Se deve usar processamento paralelo.
            num_processes (int): Número de processos para processamento paralelo. Se None, usa o número de CPUs.
            chunk_size (int): Tamanho do chunk para processamento paralelo.
        """
        pass
    
    def process(self):
        """
        Processa o vídeo.
        
        Returns:
            str: Caminho para o vídeo de saída.
        """
        pass
    
    def process_frame(self, frame):
        """
        Processa um frame.
        
        Args:
            frame (numpy.ndarray): Frame de vídeo.
            
        Returns:
            numpy.ndarray: Frame processado.
        """
        pass
    
    def process_chunk(self, chunk):
        """
        Processa um chunk de frames.
        
        Args:
            chunk (list): Lista de frames.
            
        Returns:
            list: Lista de frames processados.
        """
        pass
```

### Módulo Core (`core`)

#### Funções Utilitárias

```python
def calculate_angle(a, b, c):
    """
    Calcula o ângulo entre três pontos.
    
    Args:
        a (tuple): Coordenadas do primeiro ponto (x, y).
        b (tuple): Coordenadas do segundo ponto (x, y).
        c (tuple): Coordenadas do terceiro ponto (x, y).
        
    Returns:
        float: Ângulo em graus.
    """
    pass

def calculate_vertical_angle(a, b):
    """
    Calcula o ângulo entre dois pontos e a vertical.
    
    Args:
        a (tuple): Coordenadas do primeiro ponto (x, y).
        b (tuple): Coordenadas do segundo ponto (x, y).
        
    Returns:
        float: Ângulo em graus.
    """
    pass

def adjust_text_position(frame, text, position, font, font_scale, color, thickness):
    """
    Ajusta a posição do texto para evitar que saia do frame.
    
    Args:
        frame (numpy.ndarray): Frame de vídeo.
        text (str): Texto a ser desenhado.
        position (tuple): Posição inicial do texto (x, y).
        font (int): Fonte do texto.
        font_scale (float): Escala da fonte.
        color (tuple): Cor do texto (BGR).
        thickness (int): Espessura do texto.
        
    Returns:
        tuple: Posição ajustada do texto (x, y).
    """
    pass
```

## Exemplos de Uso

### Uso Básico

```python
from processors.video_processor import VideoProcessor

# Crie uma instância do processador de vídeo
processor = VideoProcessor(
    input_path="caminho/para/video/entrada.mp4",
    output_path="caminho/para/video/saida.mp4"
)

# Processe o vídeo
processor.process()
```

### Uso Avançado

```python
from detection.pose_detector import PoseDetector
from analysis.angle_analyzer import AngleAnalyzer
from visualization.video_visualizer import VideoVisualizer
import cv2

# Crie instâncias dos componentes
detector = PoseDetector(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    model_complexity=2,
    smoothing_window=10
)

analyzer = AngleAnalyzer()

visualizer = VideoVisualizer(
    show_landmarks=True,
    show_connections=True,
    show_angles=True,
    blur_face=True
)

# Abra o vídeo de entrada
cap = cv2.VideoCapture("caminho/para/video/entrada.mp4")

# Crie o vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(
    "caminho/para/video/saida.mp4",
    fourcc,
    cap.get(cv2.CAP_PROP_FPS),
    (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
)

# Processe o vídeo frame a frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detecte landmarks
    landmarks, _ = detector.detect_pose(frame)
    
    # Converta landmarks para coordenadas de pixel
    landmark_coords = detector.get_landmark_coordinates(landmarks, frame.shape)
    
    # Suavize landmarks
    smoothed_landmarks = detector.smooth_landmarks(landmark_coords)
    
    # Avalie ângulos
    spine_angle, spine_score, spine_color = analyzer.evaluate_spine_angle(smoothed_landmarks)
    right_shoulder_angle, right_shoulder_score, right_shoulder_color = analyzer.evaluate_shoulder_angle(smoothed_landmarks, side="right")
    left_shoulder_angle, left_shoulder_score, left_shoulder_color = analyzer.evaluate_shoulder_angle(smoothed_landmarks, side="left")
    
    # Desenhe landmarks e conexões
    frame = visualizer.draw_landmarks(frame, smoothed_landmarks)
    frame = visualizer.draw_connections(frame, smoothed_landmarks)
    
    # Desenhe ângulos
    frame = visualizer.draw_angle(frame, smoothed_landmarks[11], f"Spine: {spine_angle:.1f}°", spine_color)
    frame = visualizer.draw_angle(frame, smoothed_landmarks[12], f"R Shoulder: {right_shoulder_angle:.1f}°", right_shoulder_color)
    frame = visualizer.draw_angle(frame, smoothed_landmarks[11], f"L Shoulder: {left_shoulder_angle:.1f}°", left_shoulder_color)
    
    # Aplique tarja no rosto
    frame = visualizer.blur_face_region(frame, smoothed_landmarks)
    
    # Escreva o frame no vídeo de saída
    out.write(frame)

# Libere recursos
cap.release()
out.release()
```

## Extensibilidade

A API foi projetada para ser extensível, permitindo a adição de novos ângulos, critérios de avaliação e visualizações. Para detalhes sobre como estender a API, consulte o [guia de manutenção](../guias/manutencao.md).