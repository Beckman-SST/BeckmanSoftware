# Sistema de Processamento de Imagens - Documentação Técnica

## Visão Geral

Este sistema foi desenvolvido para processar imagens e vídeos, realizando a detecção de poses humanas, identificação de dispositivos eletrônicos e cálculo de ângulos entre articulações. O sistema utiliza uma arquitetura modular que facilita a manutenção e extensão do código.

## Estrutura do Projeto

O sistema é composto por um arquivo principal de processamento e diversos módulos especializados:

```
backend/
├── processamento_modular.py  # Script principal de processamento
├── modules/                   # Pasta contendo os módulos
│   ├── __init__.py           # Inicializador do pacote
│   ├── config.py             # Configurações do sistema
│   ├── pose_detection.py     # Detecção de poses humanas
│   ├── electronics_detection.py # Detecção de dispositivos eletrônicos
│   ├── angle_calculation.py  # Cálculo de ângulos entre articulações
│   ├── image_utils.py        # Utilitários para processamento de imagens
│   └── parallel_processing.py # Processamento paralelo de frames
└── Output/                   # Pasta para armazenamento dos resultados
```

## Módulos

### 1. Config (`config.py`)

Este módulo gerencia as configurações do sistema, permitindo ajustar parâmetros como:

- **Configurações de detecção**: Níveis de confiança para detecção e rastreamento
- **Configurações de visualização**: Opções para mostrar/ocultar elementos como ângulos, tarja facial, etc.
- **Configurações de processamento**: Definições para processamento de partes específicas do corpo

As configurações são carregadas de um arquivo JSON e podem ser modificadas durante a execução do programa.

### 2. Pose Detection (`pose_detection.py`)

Responsável pela detecção de poses humanas utilizando o MediaPipe Holistic:

- **Inicialização do modelo**: Configura o modelo Holistic com parâmetros otimizados
- **Detecção de landmarks**: Identifica pontos-chave do corpo humano
- **Suavização de movimentos**: Implementa média móvel para reduzir tremulações
- **Conexões personalizadas**: Define conexões entre landmarks para visualização
- **Análise de visibilidade**: Determina quais partes do corpo estão visíveis

O módulo é capaz de detectar automaticamente se a análise deve focar na parte superior ou inferior do corpo.

### 3. Electronics Detection (`electronics_detection.py`)

Utiliza o modelo YOLOv8 para detectar dispositivos eletrônicos nas imagens:

- **Detecção de objetos**: Identifica notebooks e monitores (classes 63 e 62 do COCO)
- **Filtragem de resultados**: Aplica thresholds de confiança e validações de tamanho
- **Integração com pose**: Relaciona a posição dos dispositivos com a posição do pulso

O módulo é otimizado para ignorar detecções em análises da parte inferior do corpo.

### 4. Angle Calculation (`angle_calculation.py`)

Realiza o cálculo e visualização de ângulos entre articulações:

- **Cálculo de ângulos**: Determina ângulos entre três pontos (articulações)
- **Visualização**: Desenha os ângulos calculados na imagem
- **Análise ergonômica**: Permite avaliar a postura do usuário

O módulo calcula ângulos para cotovelos, joelhos e outras articulações relevantes.

### 5. Image Utils (`image_utils.py`)

Fornece funções utilitárias para processamento de imagens:

- **Redimensionamento**: Ajusta o tamanho das imagens mantendo a proporção
- **Desenho de elementos**: Funções para desenhar detecções e informações na imagem
- **Ajuste de posição**: Otimiza a posição de textos para evitar sobreposições

Este módulo contém funções genéricas que são utilizadas por outros módulos do sistema.

### 6. Parallel Processing (`parallel_processing.py`)

Implementa o processamento paralelo de frames para vídeos:

- **Processamento multiprocessado**: Utiliza múltiplos núcleos para processar frames
- **Controle de interrupção**: Permite cancelar o processamento com CTRL+C
- **Gerenciamento de recursos**: Otimiza a utilização de CPU

Este módulo é especialmente útil para o processamento de vídeos longos.

## Fluxo de Processamento

O arquivo principal `processamento_modular.py` orquestra todo o fluxo de processamento:

1. **Entrada de dados**: Recebe o caminho do arquivo (imagem ou vídeo) como argumento
2. **Preparação**: Verifica o tipo de arquivo e prepara os frames para processamento
3. **Processamento de frames**: Para cada frame:
   - Redimensiona a imagem mantendo a proporção
   - Converte para RGB e processa com MediaPipe
   - Aplica suavização nos landmarks detectados
   - Determina qual lado do corpo está mais visível
   - Verifica se deve processar parte inferior ou superior do corpo
   - Detecta dispositivos eletrônicos (se aplicável)
   - Aplica tarja facial (se configurado)
   - Desenha landmarks e conexões
   - Calcula e desenha ângulos entre articulações
   - Desenha detecções de eletrônicos
4. **Processamento paralelo**: Para vídeos, utiliza múltiplos núcleos para processar frames
5. **Saída**: Salva os resultados na pasta Output

## Como Usar

Para processar uma imagem ou vídeo:

```bash
python processamento_modular.py <caminho_do_arquivo>
```

Os resultados serão salvos na pasta `Output`.

## Personalização

O sistema pode ser personalizado através das configurações em `config.py`. As principais opções incluem:

- `MIN_DETECTION_CONFIDENCE`: Confiança mínima para detecção de poses
- `SHOW_FACE_BLUR`: Ativa/desativa a tarja facial
- `SHOW_ANGLES`: Ativa/desativa a exibição de ângulos
- `SHOW_ELECTRONICS`: Ativa/desativa a exibição de dispositivos eletrônicos
- `PROCESS_LOWER_BODY`: Ativa/desativa o processamento da parte inferior do corpo

## Integração com Interface Web

Este sistema de processamento modular é utilizado pela interface web principal do projeto, permitindo o upload e processamento de múltiplas imagens e vídeos através de uma interface intuitiva.