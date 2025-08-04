# Guias do Sistema de Processamento de Vídeos

## Visão Geral

Esta seção contém guias práticos para trabalhar com o Sistema de Processamento de Vídeos, incluindo instruções para manutenção, extensão e resolução de problemas.

## Conteúdo

### [Guia de Manutenção](./manutencao.md)

Guia detalhado para manutenção do sistema, incluindo:

- Estrutura do projeto
- Modificação de componentes existentes
  - Critérios de avaliação
  - Visualização
  - Parâmetros
- Adição de novos recursos
  - Novos ângulos
  - Novos critérios
  - Novas visualizações
- Resolução de problemas comuns
  - Problemas de detecção
  - Problemas de desempenho
  - Problemas de visualização
- Testes e validação
- Boas práticas de codificação

### [Guia de Desenvolvimento - Otimizações](./desenvolvimento_otimizacoes.md)

Guia completo para desenvolvedores trabalhando com as otimizações implementadas:

- **Estrutura do Código Otimizado**: Localização e organização dos arquivos
- **IntelligentCache**: Como adicionar estratégias, debugging e configuração
- **HierarchicalProcessor**: Criação de níveis customizados e monitoramento
- **AdaptiveKalman**: Configuração personalizada e filtros customizados
- **Otimizações de Performance**: Profiling, benchmarking e otimizações de memória
- **Testes e Validação**: Testes unitários, integração e debugging
- **Melhores Práticas**: Configuração para produção e monitoramento contínuo

## Guia de Uso

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/sistema-processamento-videos.git
   cd sistema-processamento-videos
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

### Uso Básico

```python
from processors.video_processor import VideoProcessor

# Crie uma instância do processador de vídeo
processor = VideoProcessor(
    input_path="caminho/para/video/entrada.mp4",
    output_path="caminho/para/video/saida.mp4",
    process_resolution=(640, 480),  # Resolução de processamento
    min_detection_confidence=0.5,   # Confiança mínima para detecção
    min_tracking_confidence=0.5,    # Confiança mínima para rastreamento
    smoothing_window=5,             # Tamanho da janela para suavização
    show_upper_body=True,           # Mostrar parte superior do corpo
    show_lower_body=True,           # Mostrar parte inferior do corpo
    blur_face=True,                 # Aplicar tarja no rosto
    parallel_processing=True        # Usar processamento paralelo
)

# Processe o vídeo
processor.process()
```

### Configurações Avançadas

O sistema oferece várias configurações avançadas que podem ser ajustadas para atender a necessidades específicas:

```python
processor = VideoProcessor(
    # Configurações básicas
    input_path="caminho/para/video/entrada.mp4",
    output_path="caminho/para/video/saida.mp4",
    
    # Configurações de resolução
    process_resolution=(640, 480),  # Resolução de processamento
    output_resolution=None,         # Resolução de saída (None = mesma da entrada)
    
    # Configurações de detecção
    min_detection_confidence=0.5,   # Confiança mínima para detecção
    min_tracking_confidence=0.5,    # Confiança mínima para rastreamento
    model_complexity=1,             # Complexidade do modelo (0, 1 ou 2)
    
    # Configurações de suavização
    smoothing_window=5,             # Tamanho da janela para suavização
    
    # Configurações de visualização
    show_upper_body=True,           # Mostrar parte superior do corpo
    show_lower_body=True,           # Mostrar parte inferior do corpo
    show_angles=True,               # Mostrar ângulos
    show_landmarks=True,            # Mostrar landmarks
    show_connections=True,          # Mostrar conexões
    blur_face=True,                 # Aplicar tarja no rosto
    
    # Configurações de processamento
    parallel_processing=True,       # Usar processamento paralelo
    num_processes=None,             # Número de processos (None = número de CPUs)
    chunk_size=100                  # Tamanho do chunk para processamento paralelo
)
```

## Resolução de Problemas

### Problemas de Detecção

Se o sistema não estiver detectando landmarks corretamente, tente:

1. Aumentar a confiança mínima para detecção e rastreamento
2. Aumentar a complexidade do modelo
3. Melhorar a iluminação do vídeo
4. Garantir que a pessoa esteja completamente visível no vídeo

### Problemas de Desempenho

Se o sistema estiver lento, tente:

1. Reduzir a resolução de processamento
2. Ativar o processamento paralelo
3. Reduzir a complexidade do modelo
4. Desativar a visualização de elementos não essenciais

### Problemas de Visualização

Se a visualização não estiver correta, tente:

1. Verificar se os landmarks estão sendo detectados corretamente
2. Ajustar as configurações de visualização
3. Verificar se o vídeo de entrada está correto

## Exemplos

### Análise de Postura em Vídeo

```python
from processors.video_processor import VideoProcessor

# Crie uma instância do processador de vídeo
processor = VideoProcessor(
    input_path="videos/postura.mp4",
    output_path="resultados/postura_analisada.mp4",
    process_resolution=(640, 480),
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    smoothing_window=5,
    show_upper_body=True,
    show_lower_body=True,
    blur_face=True,
    parallel_processing=True
)

# Processe o vídeo
processor.process()
```

### Análise de Membros Superiores

```python
from processors.video_processor import VideoProcessor

# Crie uma instância do processador de vídeo
processor = VideoProcessor(
    input_path="videos/membros_superiores.mp4",
    output_path="resultados/membros_superiores_analisados.mp4",
    process_resolution=(640, 480),
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    smoothing_window=5,
    show_upper_body=True,
    show_lower_body=False,  # Não mostrar parte inferior do corpo
    blur_face=True,
    parallel_processing=True
)

# Processe o vídeo
processor.process()
```

## Próximos Passos

Depois de se familiarizar com o sistema, você pode querer:

1. Adicionar novos ângulos para análise
2. Implementar novos critérios de avaliação
3. Melhorar a visualização dos resultados
4. Otimizar o desempenho do sistema

Para instruções sobre como fazer isso, consulte o [guia de manutenção](./manutencao.md).