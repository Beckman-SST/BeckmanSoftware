# Documentação do Sistema de Processamento de Vídeos

## Visão Geral

Bem-vindo à documentação do Sistema de Processamento de Vídeos. Este sistema foi desenvolvido para analisar a postura de pessoas em vídeos, detectando landmarks do corpo usando MediaPipe, calculando ângulos entre articulações e avaliando a ergonomia da postura com base em critérios estabelecidos.

## Estrutura da Documentação

A documentação está organizada nas seguintes seções:

### [Arquitetura](./arquitetura/)

Descrição da arquitetura do sistema, incluindo componentes, fluxo de dados e interações entre módulos.

### [Técnico](./tecnico/)

- [Processamento de Vídeos](./tecnico/processamento_videos.md) - Documentação detalhada sobre o sistema de processamento de vídeos, incluindo fluxo de processamento, detecção de pose, análise de ângulos e visualização.
- [Implementação](./tecnico/implementacao.md) - Detalhes técnicos da implementação, incluindo estrutura de código, algoritmos e otimizações.

### [Critérios](./criterios/)

- [Angulação](./criterios/angulacao.md) - Critérios de avaliação de ângulos e parâmetros de saúde, incluindo metodologia, critérios por articulação e sistema de pontuação.

### [Guias](./guias/)

- [Manutenção](./guias/manutencao.md) - Guia de manutenção do sistema, incluindo modificação de componentes existentes, adição de novos recursos e resolução de problemas comuns.

### [API](./api/)

Documentação da API do sistema, incluindo classes, métodos e parâmetros.

## Começando

Para começar a usar o sistema, recomendamos seguir estes passos:

1. Leia a [documentação de processamento de vídeos](./tecnico/processamento_videos.md) para entender o funcionamento geral do sistema.
2. Consulte a [documentação de implementação](./tecnico/implementacao.md) para detalhes técnicos sobre a implementação.
3. Verifique os [critérios de angulação](./criterios/angulacao.md) para entender como os ângulos são avaliados.
4. Siga o [guia de manutenção](./guias/manutencao.md) para modificar ou estender o sistema.

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