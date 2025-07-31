# Histórico de Alterações (Changelog)

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- **Documentação de Suavização Temporal Avançada**: Criada documentação técnica completa para o sistema avançado de suavização temporal, incluindo:
  - Arquitetura detalhada dos componentes (Filtro de Kalman, Detecção de Outliers, Média Móvel Ponderada)
  - Algoritmos matemáticos e implementação técnica
  - Configurações e parâmetros de ajuste
  - Métricas de performance e benchmarks comparativos
  - Casos de uso e troubleshooting
  - Extensibilidade e desenvolvimento futuro
  - Resultados: 2.7% melhoria no jitter, 88% detecção de outliers
- Documentação completa do sistema, incluindo:
  - Documentação de arquitetura
  - Documentação técnica
  - Documentação de critérios
  - Guias de uso e manutenção
  - Documentação da API
- **Botões de Exclusão Individual**: Adicionado botão de lixo em cada card de arquivo processado para permitir exclusão individual de arquivos da pasta output
- **Modal de Confirmação de Exclusão**: Criado modal moderno para confirmação de exclusão de arquivos individuais com design consistente

### Alterado
- **Interface de Configurações**: Alterado o nome da opção "Mostrar Desfoque Facial" para "Mostrar Tarja" no arquivo `configuracoes.html`
- **Interface de Configurações**: Convertidos os botões de rádio do "Modo de Processamento" para switches (checkboxes) seguindo o padrão dos controles deslizantes
- **Interface de Configurações**: Padronizadas as cores dos botões na parte inferior - botões "Salvar" e "Carregar" agora usam a mesma cor primária (azul), e o botão "Restaurar Padrões" usa a cor de aviso (amarelo) igual ao botão "Limpar Marcações" da página de colagem
- **Botões de Arquivos Processados**: Corrigido o botão "Abrir Pasta" para abrir especificamente a pasta `output` em vez da pasta genérica
- **Modal de Confirmação**: Substituído o popup padrão do navegador por um modal moderno e elegante para confirmação de limpeza de arquivos processados
- **JavaScript de Configurações**: Atualizada a lógica no `configuracoes.js` para lidar com os novos switches de modo de processamento, garantindo que apenas um switch possa estar ativo por vez
- **Otimização da determinação do lado mais visível**: Eliminada a redeterminação local do `more_visible_side` nos visualizadores
  - Modificado `pose_visualizer.py`: Método `draw_landmarks` agora aceita parâmetro `more_visible_side` opcional
  - Modificado `pose_visualizer.py`: Método `_filter_landmarks` agora aceita parâmetro `more_visible_side` opcional
  - Modificado `video_processor.py`: Adicionada determinação de `more_visible_side` usando `pose_detector.determine_more_visible_side`
  - Modificado `video_visualizer.py`: Método `draw_video_landmarks` agora aceita parâmetro `more_visible_side` opcional
  - Modificado `video_visualizer.py`: Implementada filtragem baseada no lado mais visível nos métodos `_filter_video_connections` e `_draw_video_landmarks_points`
  - Melhoria de performance: Evita recálculo desnecessário do lado mais visível
  - Melhoria de consistência: Garante que o mesmo lado mais visível seja usado em todo o pipeline de processamento

### Corrigido
- **Correção da detecção dos ângulos dos olhos**: Corrigida a lógica invertida na determinação dos vértices da caixa do dispositivo eletrônico
  - Modificado `image_processor.py`: Corrigida a lógica para lado esquerdo usar vértices superior esquerdo e inferior direito
  - Modificado `image_processor.py`: Corrigida a lógica para lado direito usar vértices superior direito e inferior esquerdo
  - Correção garante que as retas dos ângulos dos olhos sejam desenhadas nos vértices corretos conforme o lado mais visível detectado

## [1.0.0] - AAAA-MM-DD

### Adicionado
- Sistema de processamento de vídeos com detecção de pose usando MediaPipe
- Análise de ângulos entre articulações
- Avaliação de postura com base em critérios ergonômicos
- Visualização de landmarks, conexões e ângulos
- Processamento paralelo de vídeos
- Suavização de landmarks
- Aplicação de tarja no rosto para privacidade

### Módulos
- Módulo de detecção (`detection`)
- Módulo de análise (`analysis`)
- Módulo de visualização (`visualization`)
- Módulo de processamento (`processors`)
- Módulo core (`core`)

### Critérios de Avaliação
- Avaliação de ângulo da coluna
- Avaliação de ângulo do ombro
- Avaliação de ângulo do cotovelo/antebraço
- Avaliação de ângulo do pulso
- Avaliação de ângulo do joelho
- Avaliação de ângulo do tornozelo
- Avaliação de ângulo olhos-dispositivo

## Guia de Versionamento

O versionamento deste projeto segue o [Versionamento Semântico](https://semver.org/lang/pt-BR/), que utiliza o formato X.Y.Z, onde:

- X: Versão maior (major) - Incrementada quando há mudanças incompatíveis com versões anteriores
- Y: Versão menor (minor) - Incrementada quando há adição de funcionalidades de forma compatível com versões anteriores
- Z: Versão de correção (patch) - Incrementada quando há correções de bugs de forma compatível com versões anteriores

## Categorias de Alterações

- **Adicionado** para novos recursos.
- **Alterado** para alterações em recursos existentes.
- **Descontinuado** para recursos que serão removidos nas próximas versões.
- **Removido** para recursos removidos nesta versão.
- **Corrigido** para correções de bugs.
- **Segurança** para atualizações de segurança.