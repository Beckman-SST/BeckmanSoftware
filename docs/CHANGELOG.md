# Histórico de Alterações (Changelog)

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não Lançado]

### Adicionado
- Documentação completa do sistema, incluindo:
  - Documentação de arquitetura
  - Documentação técnica
  - Documentação de critérios
  - Guias de uso e manutenção
  - Documentação da API

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