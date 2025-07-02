# Documentação do Sistema de Processamento de Vídeos

## Índice

1. [Introdução](#introdução)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Fluxo de Processamento](#fluxo-de-processamento)
4. [Detecção de Pose](#detecção-de-pose)
5. [Análise de Ângulos](#análise-de-ângulos)
   - [Ângulo da Coluna](#ângulo-da-coluna)
   - [Ângulo do Ombro](#ângulo-do-ombro)
   - [Ângulo do Cotovelo/Antebraço](#ângulo-do-cotelovoantebraço)
   - [Ângulo do Pulso](#ângulo-do-pulso)
   - [Ângulo do Joelho](#ângulo-do-joelho)
   - [Ângulo do Tornozelo](#ângulo-do-tornozelo)
   - [Ângulo entre Olhos e Dispositivo](#ângulo-entre-olhos-e-dispositivo)
6. [Visualização](#visualização)
7. [Processamento de Vídeos](#processamento-de-vídeos)
8. [Configurações](#configurações)
9. [Referências](#referências)

## Introdução

O sistema de processamento de vídeos foi desenvolvido para analisar a postura de pessoas em vídeos, detectando landmarks do corpo usando MediaPipe, calculando ângulos entre articulações e avaliando a ergonomia da postura com base em critérios estabelecidos. O sistema é capaz de processar vídeos, aplicar tarjas no rosto para privacidade, e visualizar os resultados da análise com códigos de cores para indicar níveis de esforço e risco ergonômico.

## Arquitetura do Sistema

O sistema é composto por vários módulos que trabalham em conjunto:

1. **Módulos de Detecção**: Responsáveis por detectar landmarks do corpo usando MediaPipe.
2. **Módulos de Análise**: Calculam ângulos entre articulações e avaliam a postura.
3. **Módulos de Visualização**: Desenham landmarks, conexões e ângulos no vídeo.
4. **Módulos de Processamento**: Coordenam o fluxo de processamento de vídeos.

## Fluxo de Processamento

O fluxo de processamento de vídeos segue estas etapas:

1. **Entrada de Dados**: O sistema recebe um vídeo como entrada.
2. **Preparação**: O vídeo é aberto e suas propriedades (largura, altura, FPS) são obtidas.
3. **Processamento de Frames**: Para cada frame do vídeo:
   - O frame é redimensionado mantendo a proporção (se configurado).
   - O frame é convertido para RGB e processado com MediaPipe para detecção de pose.
   - Os landmarks detectados são convertidos para coordenadas de pixel.
   - Se configurado, uma tarja é aplicada no rosto para privacidade.
   - Os landmarks do corpo são desenhados conforme configuração (corpo superior/inferior).
   - Os ângulos entre articulações são calculados e visualizados com códigos de cores.
4. **Saída**: O vídeo processado é salvo no diretório de saída.

## Detecção de Pose

A detecção de pose é realizada usando o MediaPipe Pose, que fornece 33 landmarks do corpo. Os landmarks são usados para calcular ângulos entre articulações e avaliar a postura.

O sistema utiliza a classe `PoseDetector` para detectar landmarks do corpo. A detecção é configurada com os seguintes parâmetros:

- `min_detection_confidence`: Confiança mínima para considerar uma detecção válida (padrão: 0.5).
- `min_tracking_confidence`: Confiança mínima para continuar rastreando landmarks (padrão: 0.5).
- `moving_average_window`: Tamanho da janela para suavização de landmarks (padrão: 3).

## Análise de Ângulos

A análise de ângulos é realizada pela classe `AngleAnalyzer`, que calcula ângulos entre articulações e avalia a postura com base em critérios estabelecidos. Os ângulos são calculados usando a função `calculate_angle`, que recebe três pontos (landmarks) e retorna o ângulo em graus.

### Ângulo da Coluna

O ângulo da coluna é calculado usando os pontos médios dos ombros e quadris. O ângulo pode ser calculado em relação à vertical (padrão) ou como ângulo interno.

**Método**: `calculate_spine_angle(landmarks, use_vertical_reference=True)`

**Landmarks utilizados**:
- Ombro esquerdo (ID: 11)
- Ombro direito (ID: 12)
- Quadril esquerdo (ID: 23)
- Quadril direito (ID: 24)

**Critérios de avaliação**:
- **Verde** (Postura excelente): Ângulo ≤ 5°
- **Amarelo** (Postura com atenção): 5° < Ângulo ≤ 10°
- **Vermelho** (Postura ruim): Ângulo > 10°

### Ângulo do Ombro

O ângulo do ombro é calculado entre o ombro, cotovelo e uma referência vertical. O sistema também verifica se o braço está em abdução (para o lado).

**Método**: `calculate_shoulder_angle(landmarks, side='right')`

**Landmarks utilizados**:
- Ombro (ID: 12 para direito, 11 para esquerdo)
- Cotovelo (ID: 14 para direito, 13 para esquerdo)
- Ombro oposto (ID: 11 para direito, 12 para esquerdo) - para verificar abdução

**Critérios de avaliação**:
- **Verde** (Nível 1): Ângulo ≤ 20°
- **Amarelo** (Nível 2): 20° < Ângulo ≤ 45°
- **Laranja** (Nível 3): 45° < Ângulo ≤ 90°
- **Vermelho** (Nível 4): Ângulo > 90°

### Ângulo do Cotovelo/Antebraço

O ângulo do cotovelo/antebraço é calculado entre o ombro, cotovelo e pulso.

**Método**: `calculate_forearm_angle(landmarks, side='right')`

**Landmarks utilizados**:
- Ombro (ID: 12 para direito, 11 para esquerdo)
- Cotovelo (ID: 14 para direito, 13 para esquerdo)
- Pulso (ID: 16 para direito, 15 para esquerdo)

**Critérios de avaliação**:
- **Verde** (Nível 1): 60° ≤ Ângulo ≤ 100°
- **Amarelo** (Nível 2): Ângulo < 60° ou Ângulo > 100°

### Ângulo do Pulso

O ângulo do pulso é calculado entre o cotovelo, pulso e dedo médio.

**Método**: `calculate_wrist_angle(landmarks, side='right')`

**Landmarks utilizados**:
- Cotovelo (ID: 14 para direito, 13 para esquerdo)
- Pulso (ID: 16 para direito, 15 para esquerdo)
- Dedo médio (ID: 18 para direito, 17 para esquerdo)

### Ângulo do Joelho

O ângulo do joelho é calculado entre o quadril, joelho e tornozelo. A avaliação é baseada nos critérios de Suzanne Rodgers.

**Método**: `calculate_knee_angle(landmarks, side='right')`

**Landmarks utilizados**:
- Quadril (ID: 24 para direito, 23 para esquerdo)
- Joelho (ID: 26 para direito, 25 para esquerdo)
- Tornozelo (ID: 28 para direito, 27 para esquerdo)

**Critérios de avaliação (Suzanne Rodgers)**:
- **Verde** (Baixo Esforço - Nível 1): 160° ≤ Ângulo ≤ 180° (quase reto, de pé ou sentado com pernas esticadas)
- **Amarelo** (Moderado Esforço - Nível 2): 45° ≤ Ângulo ≤ 80° (agachamento leve ou joelhos muito dobrados ao sentar) ou 80° < Ângulo < 160° (outros ângulos)
- **Vermelho** (Alto/Muito Alto Esforço - Nível 3+): Ângulo < 45° (agachamento profundo)

### Ângulo do Tornozelo

O ângulo do tornozelo é calculado em relação à horizontal.

**Método**: `calculate_ankle_angle(landmarks, side='right')`

**Landmarks utilizados**:
- Joelho (ID: 26 para direito, 25 para esquerdo)
- Tornozelo (ID: 28 para direito, 27 para esquerdo)

### Ângulo entre Olhos e Dispositivo

O ângulo entre os olhos e o dispositivo eletrônico é calculado para avaliar a postura do pescoço.

**Método**: `calculate_eyes_to_device_angle(landmarks, device_center)`

**Landmarks utilizados**:
- Olho esquerdo (ID: 2)
- Olho direito (ID: 5)
- Centro do dispositivo (fornecido como parâmetro)

## Visualização

A visualização dos resultados da análise é realizada pela classe `VideoVisualizer`, que desenha landmarks, conexões e ângulos no vídeo. A visualização utiliza códigos de cores para indicar níveis de esforço e risco ergonômico.

### Desenho de Landmarks

Os landmarks são desenhados como círculos coloridos no vídeo. As conexões entre landmarks são desenhadas como linhas coloridas.

**Método**: `draw_video_landmarks(frame, results, show_upper_body=True, show_lower_body=True)`

### Desenho de Ângulos

Os ângulos são desenhados como linhas coloridas no vídeo, com a cor indicando o nível de esforço e risco ergonômico.

**Métodos**:
- `draw_spine_angle(frame, landmarks_dict, use_vertical_reference=True)`
- `draw_shoulder_angle(frame, landmarks_dict, side='right')`
- `draw_forearm_angle(frame, landmarks_dict, side='right')`
- `draw_knee_angle(frame, landmarks_dict, side='right')`

### Códigos de Cores

Os códigos de cores utilizados para indicar níveis de esforço e risco ergonômico são:

- **Verde** (BGR: 0, 255, 0): Baixo esforço/risco (Nível 1)
- **Amarelo** (BGR: 0, 255, 255): Moderado esforço/risco (Nível 2)
- **Laranja** (BGR: 0, 165, 255): Alto esforço/risco (Nível 3)
- **Vermelho** (BGR: 0, 0, 255): Muito alto esforço/risco (Nível 4)

## Processamento de Vídeos

O processamento de vídeos é realizado pela classe `VideoProcessor`, que coordena todo o fluxo de processamento. A classe oferece dois métodos principais para processamento de vídeos:

1. **Processamento Sequencial**: `process_video(video_path, output_folder, progress_callback=None)`
2. **Processamento Paralelo**: `process_video_parallel(video_path, output_folder, num_workers=4, progress_callback=None)`

O processamento paralelo utiliza múltiplos workers para processar frames em paralelo, o que pode acelerar significativamente o processamento de vídeos longos.

### Processamento de Frames

O processamento de frames é realizado pelo método `_process_frame`, que executa as seguintes etapas:

1. Redimensiona o frame mantendo a proporção (se configurado).
2. Converte o frame para RGB e processa com MediaPipe para detecção de pose.
3. Converte os landmarks detectados para coordenadas de pixel.
4. Se configurado, aplica uma tarja no rosto para privacidade.
5. Desenha os landmarks do corpo conforme configuração (corpo superior/inferior).
6. Calcula e desenha os ângulos entre articulações com códigos de cores.

## Configurações

O sistema oferece várias configurações para personalizar o processamento de vídeos:

- `resize_width`: Largura para redimensionamento do frame (padrão: 640).
- `resize_height`: Altura para redimensionamento do frame (padrão: 480).
- `show_upper_body`: Se deve mostrar landmarks e ângulos do corpo superior (padrão: True).
- `show_lower_body`: Se deve mostrar landmarks e ângulos do corpo inferior (padrão: True).
- `apply_face_blur`: Se deve aplicar tarja no rosto para privacidade (padrão: True).
- `min_detection_confidence`: Confiança mínima para considerar uma detecção válida (padrão: 0.5).
- `min_tracking_confidence`: Confiança mínima para continuar rastreando landmarks (padrão: 0.5).
- `moving_average_window`: Tamanho da janela para suavização de landmarks (padrão: 3).

## Referências

### Critérios de Suzanne Rodgers para Joelhos

Os critérios de Suzanne Rodgers para avaliação do ângulo do joelho são baseados em estudos ergonômicos e biomecânicos. Os critérios classificam o ângulo do joelho em três níveis de esforço:

- **Baixo Esforço (Verde)**: 160° ≤ Ângulo ≤ 180° (quase reto, de pé ou sentado com pernas esticadas)
- **Moderado Esforço (Amarelo)**: 45° ≤ Ângulo ≤ 80° (agachamento leve ou joelhos muito dobrados ao sentar) ou 80° < Ângulo < 160° (outros ângulos)
- **Alto/Muito Alto Esforço (Vermelho)**: Ângulo < 45° (agachamento profundo)

### MediaPipe Pose Landmarks

O MediaPipe Pose fornece 33 landmarks do corpo, identificados por IDs de 0 a 32. Os landmarks mais relevantes para o sistema são:

- **Olhos**: 2 (esquerdo), 5 (direito)
- **Ombros**: 11 (esquerdo), 12 (direito)
- **Cotovelos**: 13 (esquerdo), 14 (direito)
- **Pulsos**: 15 (esquerdo), 16 (direito)
- **Dedos médios**: 17 (esquerdo), 18 (direito)
- **Quadris**: 23 (esquerdo), 24 (direito)
- **Joelhos**: 25 (esquerdo), 26 (direito)
- **Tornozelos**: 27 (esquerdo), 28 (direito)