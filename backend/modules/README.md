# Estrutura Modularizada do Projeto

Este documento descreve a estrutura modularizada do projeto de análise de postura.

## Visão Geral

O projeto foi reorganizado em uma estrutura modular para melhorar a manutenção, legibilidade e extensibilidade do código. A estrutura de diretórios é a seguinte:

```
modules/
├── core/                  # Funcionalidades centrais e utilitários
│   ├── __init__.py
│   ├── config.py          # Gerenciamento de configurações
│   └── utils.py           # Funções utilitárias
├── detection/             # Detecção de pose e objetos
│   ├── __init__.py
│   ├── pose_detector.py   # Detector de pose usando MediaPipe
│   └── electronics_detector.py  # Detector de dispositivos eletrônicos
├── analysis/              # Análise de ângulos e postura
│   ├── __init__.py
│   └── angle_analyzer.py  # Analisador de ângulos
├── visualization/         # Visualização e renderização
│   ├── __init__.py
│   └── pose_visualizer.py # Visualizador de pose
├── processors/            # Processadores de imagem e vídeo
│   ├── __init__.py
│   ├── image_processor.py # Processador de imagens
│   └── video_processor.py # Processador de vídeos
└── processamento.py       # Script principal
```

## Descrição dos Módulos

### Core

- **config.py**: Gerencia as configurações do aplicativo, incluindo carregamento e salvamento de configurações.
- **utils.py**: Contém funções utilitárias usadas em todo o projeto, como cálculo de ângulos, ajuste de posição de texto, etc.

### Detection

- **pose_detector.py**: Implementa a detecção de pose usando MediaPipe Holistic.
- **electronics_detector.py**: Implementa a detecção de dispositivos eletrônicos usando YOLO.

### Analysis

- **angle_analyzer.py**: Implementa a análise de ângulos entre diferentes partes do corpo.

### Visualization

- **pose_visualizer.py**: Implementa a visualização de landmarks, conexões e ângulos.

### Processors

- **image_processor.py**: Implementa o processamento de imagens.
- **video_processor.py**: Implementa o processamento de vídeos, incluindo processamento paralelo.

### Script Principal

- **processamento.py**: Script principal que coordena o processamento de arquivos.

## Como Usar

### Processamento de Arquivos

```python
from modules.core.config import ConfigManager
from modules.processors.image_processor import ImageProcessor
from modules.processors.video_processor import VideoProcessor

# Carrega as configurações
config_manager = ConfigManager()
config = config_manager.get_config()

# Processa uma imagem
image_processor = ImageProcessor(config)
result = image_processor.process_image('caminho/para/imagem.jpg', 'pasta/de/saida')
image_processor.release()

# Processa um vídeo
video_processor = VideoProcessor(config)
result = video_processor.process_video('caminho/para/video.mp4', 'pasta/de/saida')
video_processor.release()
```

### Usando o Script Principal

```bash
python -m modules.processamento caminho/para/arquivo -o pasta/de/saida -c arquivo_de_configuracao
```

## Benefícios da Modularização

1. **Manutenção Simplificada**: Cada módulo tem uma responsabilidade clara e bem definida.
2. **Testabilidade**: É mais fácil escrever testes unitários para módulos isolados.
3. **Reutilização de Código**: Os módulos podem ser reutilizados em diferentes partes do projeto.
4. **Extensibilidade**: Novos recursos podem ser adicionados sem modificar o código existente.
5. **Legibilidade**: O código é mais fácil de entender e navegar.