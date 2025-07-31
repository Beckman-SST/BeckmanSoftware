# Documentação do Sistema BeckmanSoftware

## Visão Geral

Bem-vindo à documentação completa do Sistema BeckmanSoftware. Este sistema integra múltiplas funcionalidades para processamento de imagens e vídeos, incluindo análise de postura, detecção de landmarks do corpo usando MediaPipe, cálculo de ângulos entre articulações, avaliação ergonômica e criação de colagens personalizadas.

## Estrutura da Documentação

A documentação está organizada nas seguintes seções:

### [Arquitetura](./arquitetura/)

Descrição da arquitetura do sistema, incluindo componentes, fluxo de dados e interações entre módulos.

### [Técnico](./technical/)

- [Processamento de Imagens](./technical/processamento_imagens.md) - Documentação completa sobre o sistema de processamento de imagens, incluindo detecção de pose, análise ergonômica, algoritmos de cálculo de ângulos e otimizações.
- [Processamento de Vídeos](./technical/processamento_videos.md) - Documentação detalhada sobre o sistema de processamento de vídeos, incluindo fluxo de processamento, detecção de pose, análise de ângulos e visualização.
- [Suavização Temporal Avançada](./technical/suavizacao_temporal_avancada.md) - Documentação técnica completa sobre o sistema avançado de suavização temporal, incluindo Filtro de Kalman, detecção de outliers, média móvel ponderada e métricas de performance.
- [Implementação](./technical/implementacao.md) - Detalhes técnicos da implementação, incluindo estrutura de código, algoritmos e otimizações.

### [Critérios](./criterios/)

- [Angulação](./criterios/angulacao.md) - Critérios de avaliação de ângulos e parâmetros de saúde, incluindo metodologia, critérios por articulação e sistema de pontuação.

### [Guias](./guias/)

- [Manutenção](./guias/manutencao.md) - Guia de manutenção do sistema, incluindo modificação de componentes existentes, adição de novos recursos e resolução de problemas comuns.

### [Colagem](./colagem/)

- [Visão Geral](./colagem/README.md) - Documentação completa do sistema de colagem, incluindo funcionalidades e arquitetura.
- [Template Frontend](./colagem/template.md) - Documentação detalhada do frontend do sistema de colagem.
- [Backend APIs](./colagem/backend.md) - Documentação das APIs e processamento backend do sistema de colagem.

### [API](./api/)

Documentação da API do sistema, incluindo classes, métodos e parâmetros.

## Começando

Para começar a usar o sistema, recomendamos seguir estes passos:

1. Leia a [documentação de processamento de imagens](./technical/processamento_imagens.md) para entender o funcionamento do sistema de análise de postura e ergonomia.
2. Consulte a [documentação de processamento de vídeos](./technical/processamento_videos.md) para entender o processamento de sequências de vídeo.
3. Explore a [documentação de suavização temporal avançada](./technical/suavizacao_temporal_avancada.md) para entender os algoritmos avançados de estabilização e redução de ruído.
4. Verifique a [documentação do sistema de colagem](./colagem/README.md) para entender as funcionalidades de criação de colagens.
5. Consulte a [documentação de implementação](./technical/implementacao.md) para detalhes técnicos sobre a implementação.
6. Consulte os [critérios de angulação](./criterios/angulacao.md) para entender como os ângulos são avaliados.
7. Siga o [guia de manutenção](./guias/manutencao.md) para modificar ou estender o sistema.

## Requisitos do Sistema

O sistema requer as seguintes dependências:

- Python 3.7 ou superior
- OpenCV
- MediaPipe
- NumPy
- multiprocessing (biblioteca padrão do Python)

## Contribuição

Para contribuir com o desenvolvimento do sistema, siga as diretrizes no [guia de manutenção](./guias/manutencao.md) e certifique-se de seguir as boas práticas de codificação descritas lá.

## Suporte

Para obter suporte ou relatar problemas, entre em contato com a equipe de desenvolvimento.