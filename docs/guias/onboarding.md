# Guia de Onboarding para Novos Membros da Equipe

## Bem-vindo ao Sistema de Processamento de Vídeos!

Este guia foi criado para ajudar novos membros da equipe a se familiarizarem com o Sistema de Processamento de Vídeos. Ele fornece uma visão geral do sistema, instruções para configuração do ambiente de desenvolvimento e recursos para aprendizado.

## Visão Geral do Sistema

O Sistema de Processamento de Vídeos é uma aplicação que analisa a postura de pessoas em vídeos, detectando landmarks do corpo usando MediaPipe, calculando ângulos entre articulações e avaliando a ergonomia da postura com base em critérios estabelecidos.

O sistema é composto por vários módulos:

- **Módulo de Detecção (`detection`)**: Responsável pela detecção de pose usando MediaPipe.
- **Módulo de Análise (`analysis`)**: Responsável pela análise de ângulos entre articulações.
- **Módulo de Visualização (`visualization`)**: Responsável pela visualização dos resultados da análise.
- **Módulo de Processamento (`processors`)**: Responsável pelo processamento de vídeos.
- **Módulo Core (`core`)**: Contém funções e classes utilitárias usadas por outros módulos.

## Configuração do Ambiente de Desenvolvimento

### Requisitos

- Python 3.7 ou superior
- Git
- Editor de código (recomendamos Visual Studio Code ou PyCharm)

### Passos para Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/sistema-processamento-videos.git
   cd sistema-processamento-videos
   ```

2. Crie um ambiente virtual:
   ```bash
   # No Windows
   python -m venv venv
   venv\Scripts\activate
   
   # No macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Verifique a instalação executando um exemplo:
   ```bash
   python examples/basic_example.py
   ```

## Estrutura do Projeto

```
sistema-processamento-videos/
├── analysis/                # Módulo de análise
│   ├── __init__.py
│   └── angle_analyzer.py    # Analisador de ângulos
├── core/                    # Módulo core
│   ├── __init__.py
│   └── utils.py             # Funções utilitárias
├── detection/               # Módulo de detecção
│   ├── __init__.py
│   └── pose_detector.py     # Detector de pose
├── processors/              # Módulo de processamento
│   ├── __init__.py
│   └── video_processor.py   # Processador de vídeo
├── visualization/           # Módulo de visualização
│   ├── __init__.py
│   └── video_visualizer.py  # Visualizador de vídeo
├── examples/                # Exemplos de uso
│   ├── basic_example.py
│   └── advanced_example.py
├── tests/                   # Testes
│   ├── test_analysis.py
│   ├── test_detection.py
│   ├── test_processors.py
│   └── test_visualization.py
├── docs/                    # Documentação
│   ├── api/                 # Documentação da API
│   ├── arquitetura/         # Documentação de arquitetura
│   ├── criterios/           # Documentação de critérios
│   ├── guias/               # Guias
│   └── tecnico/             # Documentação técnica
├── requirements.txt         # Dependências
└── README.md                # Readme principal
```

## Fluxo de Trabalho de Desenvolvimento

### Branches

- `main`: Branch principal, contém código estável e pronto para produção.
- `develop`: Branch de desenvolvimento, contém código em desenvolvimento para a próxima versão.
- `feature/<nome-da-feature>`: Branches para desenvolvimento de novas funcionalidades.
- `bugfix/<nome-do-bug>`: Branches para correção de bugs.
- `release/<versão>`: Branches para preparação de releases.

### Processo de Desenvolvimento

1. Crie uma nova branch a partir de `develop` para sua funcionalidade ou correção:
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/nova-funcionalidade
   ```

2. Desenvolva sua funcionalidade ou correção, fazendo commits frequentes:
   ```bash
   git add .
   git commit -m "Descrição clara do que foi feito"
   ```

3. Quando terminar, faça push da sua branch para o repositório remoto:
   ```bash
   git push origin feature/nova-funcionalidade
   ```

4. Crie um Pull Request para mesclar sua branch com `develop`.

5. Após revisão e aprovação, sua branch será mesclada com `develop`.

### Testes

O projeto utiliza o framework de testes `unittest` do Python. Para executar os testes:

```bash
python -m unittest discover tests
```

Ao desenvolver novas funcionalidades ou corrigir bugs, certifique-se de adicionar ou atualizar os testes correspondentes.

## Recursos para Aprendizado

### Documentação do Sistema

- [Documentação de Arquitetura](../arquitetura/README.md): Visão geral da arquitetura do sistema.
- [Documentação Técnica](../tecnico/README.md): Detalhes técnicos da implementação.
- [Documentação de Critérios](../criterios/README.md): Critérios de avaliação utilizados pelo sistema.
- [Guia de Manutenção](./manutencao.md): Instruções para manutenção do sistema.
- [Documentação da API](../api/README.md): Documentação da API do sistema.

### Recursos Externos

- [MediaPipe Pose](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker): Documentação oficial do MediaPipe Pose.
- [OpenCV](https://docs.opencv.org/): Documentação oficial do OpenCV.
- [NumPy](https://numpy.org/doc/): Documentação oficial do NumPy.
- [Python multiprocessing](https://docs.python.org/3/library/multiprocessing.html): Documentação oficial da biblioteca multiprocessing do Python.

## Boas Práticas de Codificação

### Estilo de Código

O projeto segue o estilo de código PEP 8. Recomendamos o uso de ferramentas como `flake8` e `black` para verificar e formatar o código:

```bash
# Verificar estilo de código
flake8 .

# Formatar código
black .
```

### Docstrings

Utilize docstrings no estilo Google para documentar classes, métodos e funções:

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
    # Implementação
```

### Tratamento de Erros

Utilize tratamento de erros adequado, com mensagens de erro claras e específicas:

```python
def process_frame(self, frame):
    """
    Processa um frame.
    
    Args:
        frame (numpy.ndarray): Frame de vídeo.
        
    Returns:
        numpy.ndarray: Frame processado.
        
    Raises:
        ValueError: Se o frame for None ou vazio.
    """
    if frame is None or frame.size == 0:
        raise ValueError("Frame inválido: None ou vazio")
    
    # Implementação
```

## Suporte e Comunicação

### Canais de Comunicação

- **Slack**: Canal `#sistema-processamento-videos` para comunicação diária.
- **Jira**: Para rastreamento de tarefas e bugs.
- **Confluence**: Para documentação interna e compartilhamento de conhecimento.

### Quem Contatar

- **Questões Técnicas**: [Nome do Líder Técnico]
- **Questões de Projeto**: [Nome do Gerente de Projeto]
- **Questões de Infraestrutura**: [Nome do Responsável por Infraestrutura]

## Próximos Passos

Agora que você está familiarizado com o sistema, recomendamos:

1. Explorar a documentação do sistema para entender melhor sua arquitetura e funcionamento.
2. Executar os exemplos para ver o sistema em ação.
3. Revisar o código-fonte para entender a implementação.
4. Começar com tarefas pequenas para se familiarizar com o fluxo de trabalho de desenvolvimento.

Bem-vindo à equipe e bom trabalho!