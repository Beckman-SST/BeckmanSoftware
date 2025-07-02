# Arquitetura do Sistema de Processamento de Vídeos

## Visão Geral

O Sistema de Processamento de Vídeos é projetado com uma arquitetura modular que separa as responsabilidades em componentes distintos. Esta abordagem facilita a manutenção, extensão e teste do sistema.

## Diagrama de Arquitetura

```
+---------------------+     +---------------------+     +---------------------+
|                     |     |                     |     |                     |
|  Entrada de Vídeo   | --> |  Processamento de   | --> |  Saída de Vídeo     |
|                     |     |  Vídeo              |     |  Processado         |
+---------------------+     +---------------------+     +---------------------+
                                      |
                                      v
                            +---------------------+
                            |                     |
                            |  Detecção de Pose   |
                            |  (MediaPipe)        |
                            |                     |
                            +---------------------+
                                      |
                                      v
                            +---------------------+
                            |                     |
                            |  Análise de Ângulos |
                            |                     |
                            +---------------------+
                                      |
                                      v
                            +---------------------+
                            |                     |
                            |  Visualização       |
                            |                     |
                            +---------------------+
```

## Componentes Principais

### 1. Módulo de Detecção (`detection`)

Responsável pela detecção de pose usando MediaPipe. Este módulo encapsula toda a lógica relacionada à detecção de landmarks do corpo.

**Componentes:**
- `PoseDetector`: Classe principal que utiliza MediaPipe para detectar landmarks do corpo em frames de vídeo.

**Responsabilidades:**
- Detectar landmarks do corpo em frames de vídeo
- Aplicar suavização de landmarks para reduzir ruído
- Converter landmarks para coordenadas de pixel

### 2. Módulo de Análise (`analysis`)

Responsável pela análise de ângulos entre articulações. Este módulo implementa algoritmos para calcular ângulos entre landmarks e avaliar a postura com base em critérios estabelecidos.

**Componentes:**
- `AngleAnalyzer`: Classe principal que implementa métodos para calcular e avaliar ângulos entre landmarks.

**Responsabilidades:**
- Calcular ângulos entre landmarks
- Avaliar ângulos com base em critérios ergonômicos
- Classificar ângulos em níveis de risco

### 3. Módulo de Visualização (`visualization`)

Responsável pela visualização dos resultados da análise. Este módulo implementa métodos para desenhar landmarks, conexões e ângulos no vídeo.

**Componentes:**
- `VideoVisualizer`: Classe principal que implementa métodos para desenhar elementos visuais no vídeo.

**Responsabilidades:**
- Desenhar landmarks e conexões
- Desenhar ângulos com códigos de cores
- Aplicar tarjas no rosto para privacidade (se configurado)

### 4. Módulo de Processamento (`processors`)

Responsável pelo processamento de vídeos. Este módulo coordena todo o fluxo de processamento, desde a leitura do vídeo até a escrita do vídeo processado.

**Componentes:**
- `VideoProcessor`: Classe principal que coordena o fluxo de processamento de vídeos.

**Responsabilidades:**
- Ler frames do vídeo de entrada
- Coordenar o processamento de frames
- Escrever frames processados no vídeo de saída
- Implementar processamento paralelo (se configurado)

### 5. Módulo Core (`core`)

Contém funções e classes utilitárias usadas por outros módulos, como funções para cálculo de ângulos, conversão de coordenadas, etc.

**Responsabilidades:**
- Fornecer funções matemáticas para cálculos
- Implementar utilitários para manipulação de dados
- Fornecer constantes e configurações compartilhadas

## Fluxo de Dados

1. **Entrada**: O vídeo é lido frame a frame pelo `VideoProcessor`.
2. **Detecção**: Cada frame é processado pelo `PoseDetector` para detectar landmarks do corpo.
3. **Análise**: Os landmarks detectados são analisados pelo `AngleAnalyzer` para calcular ângulos entre articulações.
4. **Visualização**: Os resultados da análise são visualizados pelo `VideoVisualizer`, que desenha landmarks, conexões e ângulos no frame.
5. **Saída**: O frame processado é escrito no vídeo de saída pelo `VideoProcessor`.

## Interações entre Componentes

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
| VideoProcessor | --> | PoseDetector   | --> | AngleAnalyzer  |
|                |     |                |     |                |
+----------------+     +----------------+     +----------------+
        |                                            |
        |                                            v
        |                                   +----------------+
        |                                   |                |
        +---------------------------------> | VideoVisualizer|
                                            |                |
                                            +----------------+
```

1. O `VideoProcessor` lê um frame do vídeo de entrada.
2. O frame é passado para o `PoseDetector` para detecção de landmarks.
3. Os landmarks detectados são passados para o `AngleAnalyzer` para cálculo e avaliação de ângulos.
4. Os resultados da análise são passados para o `VideoVisualizer` para visualização.
5. O frame processado é retornado ao `VideoProcessor` para ser escrito no vídeo de saída.

## Extensibilidade

A arquitetura modular do sistema facilita a extensão e modificação de componentes individuais sem afetar o restante do sistema. Por exemplo:

- Novos ângulos podem ser adicionados implementando novos métodos no `AngleAnalyzer` e `VideoVisualizer`.
- Novos critérios de avaliação podem ser adicionados modificando os métodos de avaliação no `AngleAnalyzer`.
- Novas visualizações podem ser adicionadas implementando novos métodos no `VideoVisualizer`.
- Novos algoritmos de detecção podem ser adicionados implementando novas classes no módulo `detection`.

## Configuração

O sistema é altamente configurável, permitindo ajustar parâmetros como:

- Resolução de processamento
- Confiança mínima para detecção e rastreamento
- Tamanho da janela para suavização de landmarks
- Quais partes do corpo mostrar (superior/inferior)
- Se aplicar tarja no rosto para privacidade
- Modo de processamento (sequencial/paralelo)

Estas configurações são definidas no construtor da classe `VideoProcessor` e podem ser personalizadas para cada instância do processador.