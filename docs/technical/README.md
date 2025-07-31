# Documentação Técnica do Sistema BeckmanSoftware

## Visão Geral

Esta seção contém a documentação técnica detalhada do Sistema BeckmanSoftware, incluindo informações sobre a implementação, algoritmos, estrutura de código e otimizações para os módulos de processamento de imagens e vídeos.

## Conteúdo

### [Processamento de Imagens](./processamento_imagens.md)

Documentação completa sobre o sistema de processamento de imagens, incluindo:

- Arquitetura do sistema e componentes principais
- Detecção de pose com MediaPipe (33 landmarks)
- Detecção de dispositivos eletrônicos com YOLOv8
- Análise de ângulos ergonômicos (cotovelo, antebraço, pulso, joelho, coluna)
- Sistema de pontuação baseado em critérios de Suzanne Rodgers
- Visualização de landmarks, conexões e ângulos
- Processamento adaptativo (parte superior/inferior do corpo)
- Algoritmos de suavização e otimizações
- Configurações e personalização
- Casos de uso e troubleshooting

### [Processamento de Vídeos](./processamento_videos.md)

Documentação detalhada sobre o sistema de processamento de vídeos, incluindo:

- Arquitetura do sistema
- Fluxo de processamento
- Detecção de pose (MediaPipe)
- Análise de ângulos
- Visualização
- Processamento de vídeos (sequencial e paralelo)
- Configurações

### [Suavização Temporal Avançada](./suavizacao_temporal_avancada.md)

Documentação técnica completa sobre o sistema avançado de suavização temporal, incluindo:

- Arquitetura e componentes (Filtro de Kalman, Detecção de Outliers, Média Móvel Ponderada)
- Algoritmos detalhados e implementação matemática
- Configurações e parâmetros de ajuste
- Métricas de performance e benchmarks comparativos
- Integração com o sistema existente
- Casos de uso e troubleshooting
- Extensibilidade e desenvolvimento futuro
- Resultados: 2.7% melhoria no jitter, 88% detecção de outliers

### [Implementação](./implementacao.md)

Detalhes técnicos da implementação, incluindo:

- Estrutura de código (módulos `detection`, `analysis`, `visualization`, `processors`, `core`)
- Dependências (OpenCV, MediaPipe, NumPy, multiprocessing)
- Implementação de componentes
  - `PoseDetector` (detecção de pose com MediaPipe)
  - `AngleAnalyzer` (cálculo e avaliação de ângulos)
  - `VideoVisualizer` (visualização de landmarks e ângulos)
  - `VideoProcessor` (processamento de vídeos)
- Fluxo de dados
- Algoritmos principais
- Otimizações
- Tratamento de erros
- Extensibilidade

## Tecnologias Utilizadas

### MediaPipe

O sistema utiliza o MediaPipe para detecção de pose, que é uma biblioteca de machine learning desenvolvida pelo Google para detecção de landmarks do corpo em tempo real. O MediaPipe Pose fornece 33 landmarks do corpo, que são utilizados para calcular ângulos entre articulações.

### OpenCV

O OpenCV (Open Source Computer Vision Library) é utilizado para processamento de imagem e vídeo, incluindo leitura e escrita de vídeos, manipulação de frames, desenho de elementos visuais, etc.

### NumPy

O NumPy é utilizado para operações matemáticas eficientes, como cálculo de ângulos, manipulação de arrays, etc.

### Multiprocessing

A biblioteca padrão `multiprocessing` do Python é utilizada para implementar processamento paralelo de vídeos, melhorando o desempenho em sistemas com múltiplos núcleos de CPU.

## Algoritmos Principais

### Cálculo de Ângulos

O sistema implementa dois tipos principais de cálculo de ângulos:

1. **Ângulo entre três pontos**: Utilizado para calcular o ângulo formado por três landmarks, como o ângulo do cotovelo formado pelo ombro, cotovelo e pulso.

2. **Ângulo com a vertical**: Utilizado para calcular o ângulo formado por dois landmarks em relação à vertical, como o ângulo da coluna formado pelos landmarks do ombro e do quadril em relação à vertical.

### Suavização de Landmarks

Para reduzir o ruído na detecção de landmarks, o sistema implementa dois níveis de suavização:

#### Suavização Simples (Média Móvel)
Algoritmo básico que utiliza uma janela deslizante para calcular a média móvel das posições dos landmarks ao longo do tempo.

#### Suavização Temporal Avançada
Sistema avançado que combina múltiplas técnicas para maior estabilidade:
- **Filtro de Kalman**: Predição e correção baseada em modelo de movimento
- **Detecção de Outliers**: Identificação automática de medições anômalas
- **Média Móvel Ponderada**: Pesos adaptativos com fator de decaimento
- **Melhorias**: 2.7% redução no jitter, detecção de até 88% de outliers

### Processamento Paralelo

O sistema implementa processamento paralelo de vídeos utilizando a biblioteca `multiprocessing` do Python. O vídeo é dividido em chunks, que são processados em paralelo por múltiplos processos, e os resultados são combinados para formar o vídeo de saída.

## Otimizações

O sistema implementa várias otimizações para melhorar o desempenho:

1. **Redimensionamento de frames**: Os frames são redimensionados para uma resolução menor antes do processamento, melhorando o desempenho sem comprometer significativamente a qualidade da detecção.

2. **Suavização de landmarks**: A suavização de landmarks reduz o ruído na detecção, melhorando a estabilidade da análise de ângulos.

3. **Processamento paralelo**: O processamento paralelo melhora o desempenho em sistemas com múltiplos núcleos de CPU.

4. **Verificação de landmarks**: O sistema verifica a presença de landmarks antes de calcular ângulos, evitando erros quando landmarks não são detectados.

## Extensibilidade

O sistema foi projetado para ser extensível, permitindo a adição de novos ângulos, critérios de avaliação e visualizações. Para detalhes sobre como estender o sistema, consulte o [guia de manutenção](../guias/manutencao.md).