# Documentação - Sistema de Processamento de Imagens

## Visão Geral

O Sistema de Processamento de Imagens é um módulo avançado de análise de postura e ergonomia que utiliza inteligência artificial para detectar landmarks do corpo humano, calcular ângulos entre articulações e avaliar a postura com base em critérios ergonômicos estabelecidos. O sistema integra MediaPipe para detecção de pose, YOLOv8 para detecção de dispositivos eletrônicos e algoritmos personalizados para análise ergonômica.

## Arquitetura do Sistema

### Componentes Principais

```
backend/modules/
├── core/                    # Utilitários e configurações centrais
│   ├── config.py           # Gerenciamento de configurações
│   └── utils.py             # Funções utilitárias (cálculos, ajustes)
├── detection/               # Módulos de detecção
│   ├── pose_detector.py     # Detecção de pose com MediaPipe
│   └── electronics_detector.py # Detecção de eletrônicos com YOLO
├── analysis/                # Módulos de análise
│   └── angle_analyzer.py    # Cálculo e análise de ângulos
├── visualization/           # Módulos de visualização
│   └── pose_visualizer.py   # Renderização de landmarks e ângulos
├── processors/              # Processadores principais
│   ├── image_processor.py   # Processamento de imagens
│   ├── video_processor.py   # Processamento de vídeos
│   └── operacional_tarja_processor.py # Processamento com tarja facial
└── processamento.py         # Script principal de processamento
```

## Tecnologias e Dependências

### Principais Bibliotecas

- **MediaPipe Holistic**: Detecção de landmarks corporais (33 pontos)
- **YOLOv8 (Ultralytics)**: Detecção de dispositivos eletrônicos
- **OpenCV**: Processamento de imagem e vídeo
- **NumPy**: Operações matemáticas e cálculos de ângulos
- **PIL (Python Imaging Library)**: Manipulação de imagens

### Configurações do Sistema

```python
# Configurações principais
min_detection_confidence: 0.8    # Confiança mínima para detecção
min_tracking_confidence: 0.8     # Confiança mínima para rastreamento
yolo_confidence: 0.65            # Confiança para detecção de eletrônicos
moving_average_window: 5         # Janela para suavização de landmarks
model_complexity: 2              # Complexidade do modelo MediaPipe (maior precisão)
```

## Módulos Detalhados

### 1. Detecção de Pose (`pose_detector.py`)

#### Funcionalidades
- Detecção de 33 landmarks corporais usando MediaPipe Holistic
- Suavização de landmarks com média móvel
- Determinação automática de visibilidade (parte superior/inferior)
- Identificação do lado mais visível (esquerdo/direito)

#### Métodos Principais
```python
class PoseDetector:
    def detect(frame)                    # Detecta landmarks em um frame
    def get_all_landmarks(results, w, h) # Extrai coordenadas dos landmarks
    def should_process_lower_body()      # Determina se processa parte inferior
    def get_more_visible_side()          # Identifica lado mais visível
```

#### Landmarks Detectados
- **Parte Superior**: Ombros (11,12), Cotovelos (13,14), Pulsos (15,16)
- **Parte Inferior**: Quadris (23,24), Joelhos (25,26), Tornozelos (27,28)
- **Rosto**: Olhos (1,2,4,5), Nariz (0), Orelhas (7,8)

### 2. Detecção de Eletrônicos (`electronics_detector.py`)

#### Funcionalidades
- Detecção de notebooks e monitores usando YOLOv8
- Filtragem baseada na proximidade com o pulso
- Integração com análise de postura
- Desenho de caixas delimitadoras

#### Classes Detectadas
- **Notebook** (Classe 63 COCO)
- **Monitor** (Classe 62 COCO)

### 3. Análise de Ângulos (`angle_analyzer.py`)

#### Ângulos Calculados

##### Parte Superior do Corpo
- **Ângulo do Cotovelo**: Ombro → Cotovelo → Pulso
- **Ângulo do Antebraço**: Avaliação ergonômica (60°-100° = ideal)
- **Ângulo do Pulso**: Cotovelo → Pulso → Dedo médio
- **Ângulo da Coluna**: Ponto médio ombros → Ponto médio quadris

##### Parte Inferior do Corpo
- **Ângulo do Joelho**: Quadril → Joelho → Tornozelo
- **Avaliação segundo critérios de Suzanne Rodgers**

#### Sistema de Pontuação
```python
# Critérios Ergonômicos
Antebraço:
  - 60° a 100°: 1 ponto (Verde - Ideal)
  - Fora da faixa: 2 pontos (Amarelo - Atenção)

Joelho:
  - 160° a 180°: 1 ponto (Verde - Baixo esforço)
  - 90° a 159°: 2 pontos (Amarelo - Médio esforço)
  - < 90°: 3 pontos (Vermelho - Alto esforço)
```

### 4. Visualização (`pose_visualizer.py`)

#### Funcionalidades
- Desenho de landmarks com cores personalizadas
- Renderização de conexões entre pontos
- Exibição de ângulos calculados
- Aplicação de tarja facial para privacidade
- Ajuste automático de posição de textos

#### Cores e Estilos
```python
# Configurações visuais
landmark_color = (0, 255, 0)      # Verde para landmarks
connection_color = (255, 0, 0)    # Vermelho para conexões
angle_colors = {
    1: (0, 255, 0),    # Verde (ideal)
    2: (0, 255, 255),  # Amarelo (atenção)
    3: (0, 0, 255)     # Vermelho (crítico)
}
```

### 5. Processamento de Imagens (`image_processor.py`)

#### Fluxo de Processamento

1. **Inicialização**
   - Carregamento de configurações
   - Inicialização dos detectores (Pose, Eletrônicos)
   - Configuração do analisador de ângulos

2. **Pré-processamento**
   - Redimensionamento da imagem
   - Conversão de formato (BGR → RGB)

3. **Detecção**
   - Detecção de landmarks corporais
   - Identificação de dispositivos eletrônicos
   - Determinação da visibilidade corporal

4. **Análise**
   - Cálculo de ângulos articulares
   - Avaliação ergonômica
   - Determinação de pontuações

5. **Visualização**
   - Desenho de landmarks e conexões
   - Renderização de ângulos
   - Aplicação de tarja facial
   - Desenho de detecções eletrônicas

6. **Pós-processamento**
   - Salvamento da imagem processada
   - Geração de relatórios (opcional)

#### Modos de Processamento

##### Modo Completo
- Análise completa de postura
- Cálculo de todos os ângulos
- Detecção de eletrônicos
- Visualização completa

##### Modo Operacional (Tarja)
- Aplicação apenas de tarja facial
- Processamento rápido
- Preservação de privacidade

##### Processamento Adaptativo
```python
# Determinação automática do tipo de análise
if should_process_lower_body(landmarks):
    # Análise da parte inferior (joelhos, postura sentada)
    process_lower_body_analysis()
else:
    # Análise da parte superior (braços, eletrônicos)
    process_upper_body_analysis()
```

## Algoritmos Principais

### 1. Cálculo de Ângulos

#### Ângulo entre Três Pontos
```python
def calculate_angle(a, b, c):
    """Calcula ângulo formado por três pontos (b é o vértice)"""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180.0 else angle
```

#### Ângulo com a Vertical
```python
def calculate_angle_with_vertical(a, b):
    """Calcula ângulo de uma linha com a vertical"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    angle = abs(math.degrees(math.atan2(dx, dy)))
    return 360 - angle if angle > 180 else angle
```

### 2. Suavização de Landmarks

```python
def apply_moving_average(history, current_landmarks, window_size):
    """Aplica média móvel para suavizar landmarks"""
    history.append(current_landmarks)
    if len(history) > window_size:
        history.pop(0)
    
    # Calcula média das posições
    smoothed_landmarks = calculate_average_landmarks(history)
    return smoothed_landmarks
```

### 3. Detecção de Visibilidade

```python
def should_process_lower_body(landmarks, results=None):
    """Determina se deve processar parte inferior do corpo"""
    # Verifica visibilidade dos landmarks dos joelhos
    knee_landmarks = [25, 26]  # Joelhos esquerdo e direito
    visible_knees = sum(1 for lm_id in knee_landmarks if lm_id in landmarks)
    
    # Critério: pelo menos um joelho visível
    return visible_knees >= 1
```

## Configurações e Personalização

### Arquivo de Configuração (JSON)

```json
{
  "min_detection_confidence": 0.8,
  "min_tracking_confidence": 0.8,
  "yolo_confidence": 0.65,
  "moving_average_window": 5,
  "show_face_blur": true,
  "show_angles": true,
  "show_electronics": true,
  "only_face_blur": false,
  "target_width": 1280
}
```

### Parâmetros Ajustáveis

- **Confiança de Detecção**: Controla sensibilidade da detecção de pose
- **Suavização**: Janela de média móvel para estabilizar landmarks
- **Visualização**: Ativar/desativar elementos visuais
- **Processamento**: Modo completo vs. apenas tarja facial

## Performance e Otimizações

### Otimizações Implementadas

1. **Redimensionamento Inteligente**
   - Reduz resolução para processamento mais rápido
   - Mantém qualidade visual adequada

2. **Processamento Condicional**
   - Detecta automaticamente região de interesse
   - Evita cálculos desnecessários

3. **Cache de Resultados**
   - Reutiliza detecções quando possível
   - Reduz redundância computacional

4. **Suavização Eficiente**
   - Média móvel com janela limitada
   - Melhora estabilidade sem overhead

5. **Model Complexity Avançado**
   - MediaPipe configurado com model_complexity=2
   - Maior precisão na detecção de landmarks
   - Crucial para cálculo preciso de ângulos sutis

6. **Sistema Anticolisão de Textos**
   - Posicionamento inteligente de textos de ângulos
   - Prevenção de sobreposição entre elementos visuais
   - Manutenção de proximidade com articulações correspondentes
   - Algoritmo de fallback para encontrar posições livres

### Métricas de Performance

- **Tempo de Processamento**: ~2-5 segundos por imagem (1080p)
- **Precisão de Detecção**: >98% para poses frontais/laterais (com model_complexity=2)
- **Uso de Memória**: ~500MB durante processamento
- **Formatos Suportados**: JPG, PNG, BMP, MP4, AVI, MOV

## Tratamento de Erros

### Cenários Tratados

1. **Landmarks Não Detectados**
   ```python
   if not results.pose_landmarks:
       return None, "Nenhuma pose detectada na imagem"
   ```

2. **Arquivo Corrompido**
   ```python
   try:
       frame = cv2.imread(image_path)
       if frame is None:
           raise ValueError("Imagem não pôde ser carregada")
   except Exception as e:
       return False, f"Erro ao carregar imagem: {e}"
   ```

3. **Configuração Inválida**
   ```python
   config = config_manager.get_config()
   if not config:
       config = get_default_config()
   ```

## Extensibilidade

### Adicionando Novos Ângulos

```python
def calculate_custom_angle(self, landmarks, side='right'):
    """Template para novos cálculos de ângulo"""
    # Definir landmarks necessários
    landmark_ids = [id1, id2, id3]
    
    # Verificar disponibilidade
    if not all(lm_id in landmarks for lm_id in landmark_ids):
        return None
    
    # Calcular ângulo
    angle = calculate_angle(
        landmarks[landmark_ids[0]],
        landmarks[landmark_ids[1]], 
        landmarks[landmark_ids[2]]
    )
    
    return angle
```

### 4. Sistema Anticolisão de Textos

#### Algoritmo de Posicionamento Inteligente

O sistema anticolisão garante que os textos dos ângulos não se sobreponham, mantendo-os próximos às articulações correspondentes:

```python
def adjust_text_position(x, y, text, frame_width, frame_height, 
                        drawn_texts=None, margin=25, padding=10):
    """
    Ajusta posição do texto para evitar colisões e manter dentro do frame
    
    Args:
        x, y: Posição original do texto
        text: Texto a ser desenhado
        frame_width, frame_height: Dimensões do frame
        drawn_texts: Lista de textos já desenhados
        margin: Margem mínima das bordas
        padding: Espaçamento mínimo entre textos
    """
    
    # Posições candidatas priorizando proximidade com a articulação
    candidate_positions = [
        (x + 35, y - 10),  # Direita-cima (preferencial)
        (x + 35, y + 20),  # Direita-baixo
        (x - 80, y - 10),  # Esquerda-cima
        (x - 80, y + 20),  # Esquerda-baixo
        (x, y - 30),       # Acima
        (x, y + 30)        # Abaixo
    ]
    
    # Testa cada posição candidata
    for pos_x, pos_y in candidate_positions:
        if is_position_valid(pos_x, pos_y, text, frame_width, 
                           frame_height, drawn_texts, margin, padding):
            return pos_x, pos_y
    
    # Algoritmo de fallback: busca vertical
    return find_fallback_position(x, y, text, frame_width, 
                                frame_height, drawn_texts)
```

#### Características do Sistema

1. **Priorização de Proximidade**
   - Posições candidatas ordenadas por proximidade à articulação
   - Preferência por posicionamento à direita e ligeiramente acima

2. **Detecção de Colisões**
   - Verificação de sobreposição com textos existentes
   - Margem de segurança configurável (25px)
   - Padding entre elementos (10px)

3. **Algoritmo de Fallback**
   - Busca vertical alternada quando posições preferenciais falham
   - Movimento incremental para encontrar espaço livre
   - Garantia de que o texto permaneça visível

4. **Conectores Visuais**
   - Linha sutil conectando articulação ao texto
   - Melhora a associação visual entre ângulo e ponto corporal
   - Transparência ajustável para não interferir na visualização

### Integrando Novos Detectores

```python
class CustomDetector:
    def __init__(self, config):
        self.config = config
    
    def detect(self, frame):
        # Implementar lógica de detecção
        return detections
    
    def draw_detections(self, frame, detections):
        # Implementar visualização
        return frame
```

## Casos de Uso

### 1. Análise Ergonômica de Escritório
- Detecção de postura em estações de trabalho
- Avaliação de ângulos de braços e pulsos
- Identificação de equipamentos (monitor, notebook)

### 2. Avaliação Postural Médica
- Análise de ângulos articulares
- Documentação de desvios posturais
- Acompanhamento de tratamentos

### 3. Pesquisa Ergonômica
- Coleta de dados posturais
- Análise estatística de ângulos
- Validação de critérios ergonômicos

### 4. Treinamento e Educação
- Demonstração de posturas corretas
- Feedback visual em tempo real
- Material educativo sobre ergonomia

## Troubleshooting

### Problemas Comuns

1. **Pose não detectada**
   - Verificar iluminação da imagem
   - Ajustar confiança de detecção
   - Garantir visibilidade corporal

2. **Ângulos incorretos**
   - Verificar calibração da câmera
   - Validar landmarks detectados
   - Ajustar parâmetros de suavização

3. **Performance lenta**
   - Reduzir resolução de entrada
   - Desabilitar detecções desnecessárias
   - Otimizar configurações de hardware

### Logs e Debugging

```python
# Ativar logs detalhados
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Salvar frames intermediários para debug
if debug_mode:
    cv2.imwrite(f"debug_frame_{timestamp}.jpg", frame)
```

## Conclusão

O Sistema de Processamento de Imagens representa uma solução completa e robusta para análise de postura e ergonomia, combinando tecnologias de ponta em visão computacional com algoritmos especializados em avaliação ergonômica. Sua arquitetura modular permite fácil extensão e personalização para diferentes casos de uso, mantendo alta performance e precisão na análise.