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

Contém funções e classes utilitárias usadas por outros módulos, incluindo sistemas avançados de otimização e cache.

**Componentes:**
- `IntelligentCache`: Sistema de cache adaptativo ultra-eficiente
- `HierarchicalProcessor`: Processador hierárquico por prioridade anatômica
- `EnhancedLandmarkProcessor`: Processador aprimorado de landmarks
- `AdaptiveKalman`: Sistema de Kalman adaptativo

**Responsabilidades:**
- Fornecer funções matemáticas para cálculos
- Implementar utilitários para manipulação de dados
- Fornecer constantes e configurações compartilhadas
- **Cache Inteligente**: Acelerar processamento com múltiplas estratégias de cache
- **Processamento Hierárquico**: Otimizar performance por níveis de prioridade
- **Suavização Avançada**: Filtro de Kalman e detecção de outliers

## Fluxo de Dados

### Fluxo Tradicional
1. **Entrada**: O vídeo é lido frame a frame pelo `VideoProcessor`.
2. **Detecção**: Cada frame é processado pelo `PoseDetector` para detectar landmarks do corpo.
3. **Análise**: Os landmarks detectados são analisados pelo `AngleAnalyzer` para calcular ângulos entre articulações.
4. **Visualização**: Os resultados da análise são visualizados pelo `VideoVisualizer`, que desenha landmarks, conexões e ângulos no frame.
5. **Saída**: O frame processado é escrito no vídeo de saída pelo `VideoProcessor`.

### Fluxo Otimizado (com Cache Inteligente e Processamento Hierárquico)
1. **Entrada**: O vídeo é lido frame a frame pelo `VideoProcessor`.
2. **Cache Check**: O `IntelligentCache` verifica se o frame já foi processado.
3. **Detecção**: Se não estiver em cache, o frame é processado pelo `PoseDetector`.
4. **Processamento Hierárquico**: O `HierarchicalProcessor` processa landmarks por níveis de prioridade:
   - **Nível 1 (Crítico)**: Face e pose central - sempre processado
   - **Nível 2 (Alto)**: Mãos - alta prioridade
   - **Nível 3 (Médio)**: Detalhes faciais - pode ser pulado
   - **Nível 4 (Baixo)**: Auxiliares - primeiro a ser pulado
5. **Suavização Avançada**: `EnhancedLandmarkProcessor` aplica filtro de Kalman e detecção de outliers.
6. **Cache Store**: Resultados são armazenados no `IntelligentCache` para reutilização.
7. **Análise**: Os landmarks otimizados são analisados pelo `AngleAnalyzer`.
8. **Visualização**: Resultados visualizados pelo `VideoVisualizer`.
9. **Saída**: Frame processado escrito no vídeo de saída.

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

O sistema foi projetado com extensibilidade em mente:

- **Novos Detectores**: Fácil integração de novos modelos de detecção
- **Algoritmos Personalizados**: Interface para algoritmos de análise customizados  
- **Visualizações**: Sistema de plugins para novas formas de visualização
- **Exportação**: Suporte a novos formatos de saída

## Configuração

O sistema permite configuração através de:

- **Arquivos de Configuração**: JSON/YAML para parâmetros do sistema
- **Interface Gráfica**: Configuração interativa de parâmetros
- **Linha de Comando**: Argumentos para execução automatizada
- **Variáveis de Ambiente**: Configuração de ambiente de produção

## Documentação Adicional

### Arquitetura de Classes Otimizadas
- **Arquivo**: [classes_otimizadas.md](classes_otimizadas.md)
- **Descrição**: Documentação detalhada da arquitetura das classes otimizadas implementadas
- **Conteúdo**: 
  - Diagramas de classes e relacionamentos
  - Padrões de design utilizados (Strategy, Observer, Template Method, etc.)
  - Estruturas de dados otimizadas
  - Algoritmos de otimização implementados
  - Extensibilidade e plugin system
  - Testes e validação