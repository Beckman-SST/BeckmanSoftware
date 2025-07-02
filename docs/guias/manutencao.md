# Guia de Manutenção do Sistema

## Índice

1. [Estrutura do Projeto](#estrutura-do-projeto)
2. [Modificação de Componentes Existentes](#modificação-de-componentes-existentes)
   - [Critérios de Avaliação](#critérios-de-avaliação)
   - [Visualização](#visualização)
   - [Parâmetros](#parâmetros)
3. [Adição de Novos Recursos](#adição-de-novos-recursos)
   - [Novos Ângulos](#novos-ângulos)
   - [Novos Critérios](#novos-critérios)
   - [Novas Visualizações](#novas-visualizações)
4. [Resolução de Problemas Comuns](#resolução-de-problemas-comuns)
   - [Problemas de Detecção](#problemas-de-detecção)
   - [Problemas de Desempenho](#problemas-de-desempenho)
   - [Problemas de Visualização](#problemas-de-visualização)
5. [Testes e Validação](#testes-e-validação)
6. [Boas Práticas de Codificação](#boas-práticas-de-codificação)

## Estrutura do Projeto

O sistema de processamento de vídeos é organizado em uma arquitetura modular, com os seguintes módulos principais:

- **detection/**: Contém a classe `PoseDetector` para detecção de pose usando MediaPipe.
- **analysis/**: Contém a classe `AngleAnalyzer` para análise de ângulos entre articulações.
- **visualization/**: Contém a classe `VideoVisualizer` para visualização dos resultados da análise.
- **processors/**: Contém a classe `VideoProcessor` para processamento de vídeos.
- **core/**: Contém funções e classes utilitárias usadas por outros módulos.

Ao realizar manutenção no sistema, é importante entender como esses módulos interagem entre si e como as alterações em um módulo podem afetar outros módulos.

## Modificação de Componentes Existentes

### Critérios de Avaliação

Os critérios de avaliação de ângulos são definidos nos métodos `evaluate_*` da classe `AngleAnalyzer`. Para modificar um critério existente, localize o método correspondente e ajuste os valores de referência e níveis de risco.

**Exemplo: Modificação dos critérios de avaliação do ângulo do ombro**

```python
def evaluate_shoulder_angle(self, angle):
    # Avaliar ângulo do ombro
    if angle is None:
        return None
    
    # Critérios originais
    # if angle <= 20:
    #     return 1  # Verde - Nível 1
    # elif angle <= 45:
    #     return 2  # Amarelo - Nível 2
    # elif angle <= 90:
    #     return 3  # Laranja - Nível 3
    # else:
    #     return 4  # Vermelho - Nível 4
    
    # Novos critérios mais rigorosos
    if angle <= 15:  # Reduzido de 20 para 15
        return 1  # Verde - Nível 1
    elif angle <= 40:  # Reduzido de 45 para 40
        return 2  # Amarelo - Nível 2
    elif angle <= 80:  # Reduzido de 90 para 80
        return 3  # Laranja - Nível 3
    else:
        return 4  # Vermelho - Nível 4
```

### Visualização

A visualização dos resultados da análise é definida nos métodos `draw_*` da classe `VideoVisualizer`. Para modificar uma visualização existente, localize o método correspondente e ajuste os parâmetros de desenho.

**Exemplo: Modificação da visualização do ângulo da coluna**

```python
def draw_spine_angle(self, frame, landmarks_dict, use_vertical_reference=True):
    # Desenhar ângulo da coluna
    angle = self.angle_analyzer.calculate_spine_angle(landmarks_dict, use_vertical_reference)
    if angle is None:
        return frame
    
    # Avaliar ângulo
    risk_level = self.angle_analyzer.evaluate_spine_angle(angle)
    
    # Cores originais
    # color = self.colors.get(risk_level, (255, 255, 255))  # Branco como fallback
    
    # Novas cores mais vibrantes
    new_colors = {
        1: (0, 255, 0),     # Verde mais brilhante
        2: (0, 255, 255),    # Amarelo mais brilhante
        3: (0, 128, 255),    # Laranja mais escuro
        4: (0, 0, 255)       # Vermelho padrão
    }
    color = new_colors.get(risk_level, (255, 255, 255))  # Branco como fallback
    
    # Calcular pontos para desenho
    shoulders_mid = (
        int((landmarks_dict[11][0] + landmarks_dict[12][0]) / 2),
        int((landmarks_dict[11][1] + landmarks_dict[12][1]) / 2)
    )
    
    hips_mid = (
        int((landmarks_dict[23][0] + landmarks_dict[24][0]) / 2),
        int((landmarks_dict[23][1] + landmarks_dict[24][1]) / 2)
    )
    
    # Desenhar linha da coluna com espessura maior
    cv2.line(frame, shoulders_mid, hips_mid, color, 3)  # Aumentado de 2 para 3
    
    # Desenhar ângulo com fonte maior
    text_pos = self._adjust_text_position(shoulders_mid, 10, 30)
    cv2.putText(frame, f"Coluna: {angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)  # Aumentado de 0.5 para 0.7
    
    return frame
```

### Parâmetros

Os parâmetros de configuração do sistema são definidos no construtor da classe `VideoProcessor`. Para modificar um parâmetro existente, ajuste o dicionário `config` no construtor.

**Exemplo: Modificação dos parâmetros de redimensionamento**

```python
def __init__(self, pose_detector, angle_analyzer, visualizer, config=None):
    self.pose_detector = pose_detector
    self.angle_analyzer = angle_analyzer
    self.visualizer = visualizer
    
    # Configurações padrão originais
    # self.config = {
    #     'resize_width': 640,
    #     'resize_height': 480,
    #     'show_upper_body': True,
    #     'show_lower_body': True,
    #     'apply_face_blur': True
    # }
    
    # Novas configurações padrão com resolução maior
    self.config = {
        'resize_width': 1280,  # Aumentado de 640 para 1280
        'resize_height': 720,  # Aumentado de 480 para 720
        'show_upper_body': True,
        'show_lower_body': True,
        'apply_face_blur': True,
        'show_text_labels': True  # Novo parâmetro
    }
    
    # Atualizar configurações se fornecidas
    if config:
        self.config.update(config)
```

## Adição de Novos Recursos

### Novos Ângulos

Para adicionar um novo ângulo, siga estas etapas:

1. Adicione um método `calculate_*` na classe `AngleAnalyzer` para calcular o novo ângulo.
2. Adicione um método `evaluate_*` na classe `AngleAnalyzer` para avaliar o novo ângulo.
3. Adicione um método `draw_*` na classe `VideoVisualizer` para desenhar o novo ângulo.
4. Atualize o método `_process_frame` da classe `VideoProcessor` para incluir o novo ângulo no processamento.

**Exemplo: Adição de um novo ângulo para o pescoço**

```python
# Na classe AngleAnalyzer
def calculate_neck_angle(self, landmarks):
    # Calcular ângulo do pescoço
    if not self._check_landmarks(landmarks, [0, 11, 12]):
        return None
    
    # Ponto médio dos ombros
    shoulders_mid = (
        (landmarks[11][0] + landmarks[12][0]) / 2,
        (landmarks[11][1] + landmarks[12][1]) / 2
    )
    
    # Nariz
    nose = landmarks[0]
    
    # Calcular ângulo com a vertical
    angle = self.calculate_angle_with_vertical(shoulders_mid, nose)
    
    return angle

def evaluate_neck_angle(self, angle):
    # Avaliar ângulo do pescoço
    if angle is None:
        return None
    
    if angle <= 10:
        return 1  # Verde - Nível 1
    elif angle <= 20:
        return 2  # Amarelo - Nível 2
    elif angle <= 30:
        return 3  # Laranja - Nível 3
    else:
        return 4  # Vermelho - Nível 4

# Na classe VideoVisualizer
def draw_neck_angle(self, frame, landmarks_dict):
    # Desenhar ângulo do pescoço
    angle = self.angle_analyzer.calculate_neck_angle(landmarks_dict)
    if angle is None:
        return frame
    
    # Avaliar ângulo
    risk_level = self.angle_analyzer.evaluate_neck_angle(angle)
    color = self.colors.get(risk_level, (255, 255, 255))  # Branco como fallback
    
    # Calcular pontos para desenho
    shoulders_mid = (
        int((landmarks_dict[11][0] + landmarks_dict[12][0]) / 2),
        int((landmarks_dict[11][1] + landmarks_dict[12][1]) / 2)
    )
    
    nose = landmarks_dict[0]
    
    # Desenhar linha do pescoço
    cv2.line(frame, shoulders_mid, nose, color, 2)
    
    # Desenhar ângulo
    text_pos = self._adjust_text_position(nose, 10, -10)
    cv2.putText(frame, f"Pescoço: {angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return frame

# Na classe VideoProcessor, método _process_frame
# Adicionar após o desenho de outros ângulos
if self.config['show_upper_body']:
    # ... código existente ...
    
    # Desenhar ângulo do pescoço
    frame_annotated = self.visualizer.draw_neck_angle(frame_annotated, landmarks_dict)
```

### Novos Critérios

Para adicionar novos critérios de avaliação, siga estas etapas:

1. Identifique o método `evaluate_*` correspondente ao ângulo que deseja modificar.
2. Ajuste os valores de referência e níveis de risco conforme necessário.
3. Atualize a documentação para refletir os novos critérios.

**Exemplo: Adição de novos critérios para o ângulo do pulso**

```python
def evaluate_wrist_angle(self, angle):
    # Avaliar ângulo do pulso
    if angle is None:
        return None
    
    # Critérios originais simples
    # if -15 <= angle <= 15:
    #     return 1  # Verde - Nível 1
    # else:
    #     return 2  # Amarelo - Nível 2
    
    # Novos critérios mais detalhados
    if -15 <= angle <= 15:
        return 1  # Verde - Nível 1 (Posição neutra)
    elif (-30 <= angle < -15) or (15 < angle <= 30):
        return 2  # Amarelo - Nível 2 (Desvio moderado)
    elif (-45 <= angle < -30) or (30 < angle <= 45):
        return 3  # Laranja - Nível 3 (Desvio significativo)
    else:
        return 4  # Vermelho - Nível 4 (Desvio extremo)
```

### Novas Visualizações

Para adicionar novas visualizações, siga estas etapas:

1. Adicione um novo método `draw_*` na classe `VideoVisualizer`.
2. Atualize o método `_process_frame` da classe `VideoProcessor` para incluir a nova visualização no processamento.

**Exemplo: Adição de uma visualização para o centro de massa**

```python
# Na classe VideoVisualizer
def draw_center_of_mass(self, frame, landmarks_dict):
    # Desenhar centro de massa
    if not all(idx in landmarks_dict for idx in [11, 12, 23, 24]):
        return frame
    
    # Calcular centro de massa como média dos ombros e quadris
    x_sum = landmarks_dict[11][0] + landmarks_dict[12][0] + landmarks_dict[23][0] + landmarks_dict[24][0]
    y_sum = landmarks_dict[11][1] + landmarks_dict[12][1] + landmarks_dict[23][1] + landmarks_dict[24][1]
    
    center_x = int(x_sum / 4)
    center_y = int(y_sum / 4)
    
    # Desenhar círculo no centro de massa
    cv2.circle(frame, (center_x, center_y), 10, (255, 0, 255), -1)  # Magenta
    
    # Desenhar texto
    text_pos = self._adjust_text_position((center_x, center_y), 15, 15)
    cv2.putText(frame, "Centro de Massa", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
    
    return frame

# Na classe VideoProcessor, método _process_frame
# Adicionar após o desenho de outros elementos
# Desenhar centro de massa
frame_annotated = self.visualizer.draw_center_of_mass(frame_annotated, landmarks_dict)
```

## Resolução de Problemas Comuns

### Problemas de Detecção

#### Problema: Landmarks não são detectados corretamente

**Possíveis causas:**
- Iluminação inadequada
- Pessoa parcialmente fora do quadro
- Roupa que dificulta a detecção
- Configurações de confiança muito altas

**Soluções:**
1. Ajuste os parâmetros `min_detection_confidence` e `min_tracking_confidence` da classe `PoseDetector`:

```python
pose_detector = PoseDetector(
    min_detection_confidence=0.3,  # Reduzido de 0.5 para 0.3
    min_tracking_confidence=0.3    # Reduzido de 0.5 para 0.3
)
```

2. Implemente uma lógica de fallback para usar landmarks de frames anteriores quando a detecção falha:

```python
def detect_pose(self, frame):
    # ... código existente ...
    
    # Se não detectou landmarks e temos histórico, usar o último conjunto de landmarks
    if not results.pose_landmarks and self.landmark_history:
        last_landmarks = self.landmark_history[-1]
        for i, (x, y, z, v) in enumerate(last_landmarks):
            if not results.pose_landmarks:
                results.pose_landmarks = self.mp_pose.PoseLandmark()
            results.pose_landmarks.landmark[i].x = x
            results.pose_landmarks.landmark[i].y = y
            results.pose_landmarks.landmark[i].z = z
            results.pose_landmarks.landmark[i].visibility = v * 0.8  # Reduzir confiança
    
    # ... resto do código ...
```

3. Pré-processe o frame para melhorar o contraste e a iluminação:

```python
def detect_pose(self, frame):
    # Pré-processar o frame para melhorar a detecção
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Aumentar contraste
    alpha = 1.5  # Contraste (1.0 é neutro)
    beta = 0     # Brilho (0 é neutro)
    frame_rgb = cv2.convertScaleAbs(frame_rgb, alpha=alpha, beta=beta)
    
    # Processar o frame com MediaPipe
    results = self.pose.process(frame_rgb)
    
    # ... resto do código ...
```

### Problemas de Desempenho

#### Problema: Processamento lento

**Possíveis causas:**
- Resolução do vídeo muito alta
- Muitos ângulos sendo calculados e visualizados
- Hardware insuficiente

**Soluções:**
1. Reduza a resolução de processamento:

```python
# Na classe VideoProcessor
self.config = {
    'resize_width': 480,  # Reduzido de 640 para 480
    'resize_height': 360,  # Reduzido de 480 para 360
    # ... outras configurações ...
}
```

2. Processe apenas um subconjunto de frames:

```python
def process_video(self, video_path, output_folder, progress_callback=None):
    # ... código existente ...
    
    frame_count = 0
    process_every_n_frames = 2  # Processar apenas um a cada 2 frames
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Processar apenas um a cada N frames
        if frame_count % process_every_n_frames == 0:
            processed_frame = self._process_frame(frame)
        else:
            processed_frame = frame
        
        # Escrever frame processado
        out.write(processed_frame)
        
        # ... resto do código ...
```

3. Otimize o processamento paralelo ajustando o número de workers:

```python
def process_video_parallel(self, video_path, output_folder, num_workers=None, progress_callback=None):
    # Determinar número ótimo de workers com base no hardware
    if num_workers is None:
        num_workers = max(1, multiprocessing.cpu_count() - 1)  # Deixar um CPU livre para o sistema
    
    # ... resto do código ...
```

### Problemas de Visualização

#### Problema: Texto e linhas sobrepostos ou difíceis de ler

**Possíveis causas:**
- Muitos ângulos sendo visualizados simultaneamente
- Posicionamento inadequado do texto
- Cores que não contrastam com o fundo

**Soluções:**
1. Melhore o posicionamento do texto com um algoritmo mais sofisticado:

```python
def _adjust_text_position(self, point, offset_x, offset_y):
    # Versão mais sofisticada para evitar sobreposição
    # Verificar se o ponto está na metade superior ou inferior da imagem
    h, w, _ = self.last_frame_shape  # Armazenar shape do último frame processado
    
    if point[1] < h / 2:  # Ponto na metade superior
        return (point[0] + offset_x, point[1] + abs(offset_y))  # Texto abaixo do ponto
    else:  # Ponto na metade inferior
        return (point[0] + offset_x, point[1] - abs(offset_y))  # Texto acima do ponto
```

2. Adicione um fundo ao texto para melhorar a legibilidade:

```python
def _draw_text_with_background(self, frame, text, position, font, scale, color, thickness):
    # Desenhar texto com fundo para melhorar legibilidade
    text_size, _ = cv2.getTextSize(text, font, scale, thickness)
    text_w, text_h = text_size
    
    # Coordenadas do retângulo de fundo
    x, y = position
    bg_rect = (x, y - text_h - 5, x + text_w, y + 5)
    
    # Desenhar retângulo de fundo semi-transparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (bg_rect[0], bg_rect[1]), (bg_rect[2], bg_rect[3]), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)  # 60% opaco
    
    # Desenhar texto
    cv2.putText(frame, text, position, font, scale, color, thickness)
```

3. Implemente um sistema de alternância para mostrar apenas um subconjunto de ângulos de cada vez:

```python
# Na classe VideoProcessor
def __init__(self, pose_detector, angle_analyzer, visualizer, config=None):
    # ... código existente ...
    
    self.config = {
        # ... outras configurações ...
        'visualization_mode': 'all'  # Opções: 'all', 'upper_body', 'lower_body', 'spine', 'limbs'
    }
    
    # ... resto do código ...

def _process_frame(self, frame):
    # ... código existente ...
    
    # Desenhar ângulos com base no modo de visualização
    if self.config['visualization_mode'] == 'all' or self.config['visualization_mode'] == 'upper_body':
        # Desenhar ângulos do corpo superior
        frame_annotated = self.visualizer.draw_spine_angle(frame_annotated, landmarks_dict)
        frame_annotated = self.visualizer.draw_shoulder_angle(frame_annotated, landmarks_dict, 'right')
        frame_annotated = self.visualizer.draw_shoulder_angle(frame_annotated, landmarks_dict, 'left')
        frame_annotated = self.visualizer.draw_forearm_angle(frame_annotated, landmarks_dict, 'right')
        frame_annotated = self.visualizer.draw_forearm_angle(frame_annotated, landmarks_dict, 'left')
    
    if self.config['visualization_mode'] == 'all' or self.config['visualization_mode'] == 'lower_body':
        # Desenhar ângulos do corpo inferior
        frame_annotated = self.visualizer.draw_knee_angle(frame_annotated, landmarks_dict, 'right')
        frame_annotated = self.visualizer.draw_knee_angle(frame_annotated, landmarks_dict, 'left')
    
    if self.config['visualization_mode'] == 'spine':
        # Desenhar apenas ângulo da coluna
        frame_annotated = self.visualizer.draw_spine_angle(frame_annotated, landmarks_dict)
    
    if self.config['visualization_mode'] == 'limbs':
        # Desenhar apenas ângulos dos membros
        frame_annotated = self.visualizer.draw_shoulder_angle(frame_annotated, landmarks_dict, 'right')
        frame_annotated = self.visualizer.draw_shoulder_angle(frame_annotated, landmarks_dict, 'left')
        frame_annotated = self.visualizer.draw_knee_angle(frame_annotated, landmarks_dict, 'right')
        frame_annotated = self.visualizer.draw_knee_angle(frame_annotated, landmarks_dict, 'left')
    
    # ... resto do código ...
```

## Testes e Validação

Ao fazer alterações no sistema, é importante testá-las adequadamente para garantir que não introduzam regressões ou novos bugs. Aqui estão algumas estratégias de teste:

### Testes Unitários

Implemente testes unitários para funções críticas, como cálculo de ângulos e avaliação de critérios:

```python
import unittest
import numpy as np
from analysis.angle_analyzer import AngleAnalyzer

class TestAngleAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = AngleAnalyzer()
    
    def test_calculate_angle(self):
        # Teste com ângulo de 90 graus
        a = (0, 0)
        b = (0, 1)
        c = (1, 1)
        angle = self.analyzer.calculate_angle(a, b, c)
        self.assertAlmostEqual(angle, 90.0, places=1)
        
        # Teste com ângulo de 45 graus
        a = (0, 0)
        b = (0, 1)
        c = (1, 2)
        angle = self.analyzer.calculate_angle(a, b, c)
        self.assertAlmostEqual(angle, 45.0, places=1)
    
    def test_evaluate_spine_angle(self):
        # Teste com ângulo verde
        self.assertEqual(self.analyzer.evaluate_spine_angle(3.0), 1)
        
        # Teste com ângulo amarelo
        self.assertEqual(self.analyzer.evaluate_spine_angle(7.0), 2)
        
        # Teste com ângulo vermelho
        self.assertEqual(self.analyzer.evaluate_spine_angle(15.0), 3)

if __name__ == '__main__':
    unittest.main()
```

### Testes de Integração

Implemente testes de integração para verificar se os componentes funcionam corretamente juntos:

```python
import unittest
import cv2
import numpy as np
import mediapipe as mp
from detection.pose_detector import PoseDetector
from analysis.angle_analyzer import AngleAnalyzer
from visualization.video_visualizer import VideoVisualizer

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.pose_detector = PoseDetector()
        self.angle_analyzer = AngleAnalyzer()
        self.visualizer = VideoVisualizer(self.angle_analyzer)
        
        # Criar uma imagem de teste com uma pessoa em pose conhecida
        self.test_image = cv2.imread('test_data/test_pose.jpg')
    
    def test_detection_and_analysis(self):
        # Detectar pose na imagem de teste
        results = self.pose_detector.detect_pose(self.test_image)
        
        # Verificar se a pose foi detectada
        self.assertIsNotNone(results.pose_landmarks)
        
        # Converter landmarks para coordenadas de pixel
        h, w, _ = self.test_image.shape
        landmarks_dict = {}
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks_dict[idx] = (int(landmark.x * w), int(landmark.y * h))
        
        # Calcular ângulo da coluna
        spine_angle = self.angle_analyzer.calculate_spine_angle(landmarks_dict)
        
        # Verificar se o ângulo foi calculado
        self.assertIsNotNone(spine_angle)
        
        # Verificar se o ângulo está dentro de um intervalo esperado
        self.assertTrue(0 <= spine_angle <= 90)

if __name__ == '__main__':
    unittest.main()
```

### Testes de Regressão

Implemente testes de regressão para verificar se as alterações não quebram funcionalidades existentes:

```python
import unittest
import cv2
import os
import filecmp
from processors.video_processor import VideoProcessor
from detection.pose_detector import PoseDetector
from analysis.angle_analyzer import AngleAnalyzer
from visualization.video_visualizer import VideoVisualizer

class TestRegression(unittest.TestCase):
    def setUp(self):
        self.pose_detector = PoseDetector()
        self.angle_analyzer = AngleAnalyzer()
        self.visualizer = VideoVisualizer(self.angle_analyzer)
        self.processor = VideoProcessor(self.pose_detector, self.angle_analyzer, self.visualizer)
        
        # Criar diretórios de teste se não existirem
        os.makedirs('test_data/output', exist_ok=True)
        os.makedirs('test_data/expected', exist_ok=True)
    
    def test_video_processing(self):
        # Processar vídeo de teste
        output_path = self.processor.process_video('test_data/test_video.mp4', 'test_data/output')
        
        # Verificar se o arquivo de saída foi criado
        self.assertTrue(os.path.exists(output_path))
        
        # Comparar com resultado esperado (se disponível)
        expected_path = 'test_data/expected/processed_test_video.mp4'
        if os.path.exists(expected_path):
            # Comparar frames dos vídeos
            cap_output = cv2.VideoCapture(output_path)
            cap_expected = cv2.VideoCapture(expected_path)
            
            frame_count = 0
            max_diff = 0
            
            while True:
                ret1, frame1 = cap_output.read()
                ret2, frame2 = cap_expected.read()
                
                if not ret1 or not ret2:
                    break
                
                # Calcular diferença entre frames
                diff = cv2.absdiff(frame1, frame2)
                diff_mean = diff.mean()
                max_diff = max(max_diff, diff_mean)
                
                frame_count += 1
            
            cap_output.release()
            cap_expected.release()
            
            # Verificar se a diferença média está abaixo de um limiar
            self.assertLess(max_diff, 5.0, "Diferença significativa detectada entre o resultado atual e o esperado")

if __name__ == '__main__':
    unittest.main()
```

## Boas Práticas de Codificação

Ao fazer alterações no sistema, siga estas boas práticas de codificação:

### Documentação

Mantenha a documentação atualizada, incluindo docstrings para classes e métodos:

```python
def calculate_angle(self, a, b, c):
    """
    Calcula o ângulo entre três pontos (A, B, C).
    
    O ângulo é calculado entre os vetores BA e BC, ou seja, o ângulo no ponto B.
    
    Args:
        a (tuple): Coordenadas do ponto A (x, y).
        b (tuple): Coordenadas do ponto B (x, y).
        c (tuple): Coordenadas do ponto C (x, y).
    
    Returns:
        float: Ângulo em graus entre os vetores BA e BC.
    """
    # ... implementação ...
```

### Tratamento de Erros

Implemente tratamento de erros adequado para lidar com casos excepcionais:

```python
def calculate_spine_angle(self, landmarks, use_vertical_reference=True):
    """
    Calcula o ângulo da coluna.
    
    Args:
        landmarks (dict): Dicionário de landmarks.
        use_vertical_reference (bool): Se True, calcula o ângulo com a vertical.
    
    Returns:
        float or None: Ângulo da coluna em graus, ou None se os landmarks necessários não estiverem disponíveis.
    """
    try:
        if not self._check_landmarks(landmarks, [11, 12, 23, 24]):
            return None
        
        # ... implementação ...
        
        return angle
    except Exception as e:
        print(f"Erro ao calcular ângulo da coluna: {e}")
        return None
```

### Modularização

Mantenha o código modular e evite duplicação:

```python
# Antes: Código duplicado para desenhar ângulos
def draw_shoulder_angle(self, frame, landmarks_dict, side='right'):
    # ... implementação específica para ombro ...

def draw_forearm_angle(self, frame, landmarks_dict, side='right'):
    # ... implementação específica para antebraço ...

# Depois: Função genérica reutilizável
def draw_angle(self, frame, landmarks_dict, angle_type, side='right'):
    """
    Desenha um ângulo no frame.
    
    Args:
        frame (numpy.ndarray): Frame do vídeo.
        landmarks_dict (dict): Dicionário de landmarks.
        angle_type (str): Tipo de ângulo ('spine', 'shoulder', 'forearm', 'knee').
        side (str): Lado do corpo ('right' ou 'left').
    
    Returns:
        numpy.ndarray: Frame com o ângulo desenhado.
    """
    # Calcular ângulo com base no tipo
    if angle_type == 'spine':
        angle = self.angle_analyzer.calculate_spine_angle(landmarks_dict)
        risk_level = self.angle_analyzer.evaluate_spine_angle(angle)
        label = "Coluna"
    elif angle_type == 'shoulder':
        angle = self.angle_analyzer.calculate_shoulder_angle(landmarks_dict, side)
        risk_level = self.angle_analyzer.evaluate_shoulder_angle(angle)
        label = f"Ombro {side}"
    # ... outros tipos de ângulo ...
    
    if angle is None:
        return frame
    
    # Obter cor com base no nível de risco
    color = self.colors.get(risk_level, (255, 255, 255))
    
    # ... desenho específico para cada tipo de ângulo ...
    
    # Desenhar texto
    text_pos = self._adjust_text_position(point, 10, 10)
    cv2.putText(frame, f"{label}: {angle:.1f}°", text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    return frame
```

### Configuração

Use arquivos de configuração para parâmetros que podem precisar ser ajustados:

```python
import json

# Carregar configuração de arquivo
def load_config(config_path):
    """
    Carrega configuração de um arquivo JSON.
    
    Args:
        config_path (str): Caminho para o arquivo de configuração.
    
    Returns:
        dict: Configuração carregada.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Erro ao carregar configuração: {e}")
        return {}

# Usar configuração carregada
config = load_config('config.json')
processor = VideoProcessor(pose_detector, angle_analyzer, visualizer, config)
```

### Versionamento

Mantenha um registro de alterações para facilitar o rastreamento de mudanças:

```python
"""
Sistema de Processamento de Vídeos

Versão: 1.2.0

Histórico de Alterações:
- 1.2.0: Adicionado suporte para ângulo do pescoço e melhorias na visualização
- 1.1.0: Implementado processamento paralelo e otimizações de desempenho
- 1.0.0: Versão inicial com suporte para ângulos básicos
"""
```

Seguindo estas boas práticas, você manterá o código limpo, legível e fácil de manter, facilitando futuras modificações e extensões do sistema.