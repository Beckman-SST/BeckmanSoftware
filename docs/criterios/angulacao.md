# Critérios de Avaliação de Ângulos e Parâmetros de Saúde

## Índice

1. [Introdução](#introdução)
2. [Metodologia de Avaliação](#metodologia-de-avaliação)
3. [Critérios por Articulação](#critérios-por-articulação)
   - [Coluna Vertebral](#coluna-vertebral)
   - [Ombros](#ombros)
   - [Cotovelos/Antebraços](#cotelovosantebraços)
   - [Pulsos](#pulsos)
   - [Joelhos](#joelhos)
   - [Tornozelos](#tornozelos)
4. [Sistema de Pontuação](#sistema-de-pontuação)
5. [Interpretação dos Resultados](#interpretação-dos-resultados)
6. [Recomendações Ergonômicas](#recomendações-ergonômicas)
7. [Referências](#referências)

## Introdução

Este documento apresenta os critérios de avaliação utilizados para analisar os ângulos das articulações e postura corporal no sistema de processamento de vídeos. Os critérios são baseados em estudos ergonômicos, biomecânicos e recomendações de saúde ocupacional, visando identificar posturas que podem representar riscos à saúde musculoesquelética.

## Metodologia de Avaliação

A avaliação dos ângulos é realizada através da detecção de landmarks (pontos de referência) do corpo usando o MediaPipe Pose, seguida do cálculo dos ângulos entre articulações específicas. Cada ângulo é então classificado em diferentes níveis de risco ergonômico, utilizando um sistema de cores:

- **Verde**: Baixo risco/esforço (Nível 1)
- **Amarelo**: Moderado risco/esforço (Nível 2)
- **Laranja**: Alto risco/esforço (Nível 3)
- **Vermelho**: Muito alto risco/esforço (Nível 4)

A classificação é baseada em valores de referência estabelecidos por estudos ergonômicos, como os critérios de Suzanne Rodgers para joelhos, e adaptações de métodos de avaliação ergonômica como RULA (Rapid Upper Limb Assessment) e REBA (Rapid Entire Body Assessment).

## Critérios por Articulação

### Coluna Vertebral

**Método de cálculo**: O ângulo da coluna é calculado usando os pontos médios dos ombros e quadris, em relação à vertical.

**Landmarks utilizados**:
- Ombro esquerdo (ID: 11)
- Ombro direito (ID: 12)
- Quadril esquerdo (ID: 23)
- Quadril direito (ID: 24)

**Critérios de avaliação**:
- **Verde** (Postura excelente): Ângulo ≤ 5°
  - Coluna quase perfeitamente alinhada com a vertical
  - Mínimo estresse nas vértebras e músculos paravertebrais
  - Distribuição ideal do peso corporal

- **Amarelo** (Postura com atenção): 5° < Ângulo ≤ 10°
  - Leve inclinação da coluna
  - Aumento moderado da tensão muscular
  - Potencial para desconforto em períodos prolongados

- **Vermelho** (Postura ruim): Ângulo > 10°
  - Inclinação significativa da coluna
  - Alta tensão nos músculos paravertebrais
  - Risco aumentado de lesões e dores crônicas
  - Possível compressão de discos intervertebrais

### Ombros

**Método de cálculo**: O ângulo do ombro é calculado entre o ombro, cotovelo e uma referência vertical. O sistema também verifica se o braço está em abdução (para o lado).

**Landmarks utilizados**:
- Ombro (ID: 12 para direito, 11 para esquerdo)
- Cotovelo (ID: 14 para direito, 13 para esquerdo)
- Ombro oposto (ID: 11 para direito, 12 para esquerdo) - para verificar abdução

**Critérios de avaliação**:
- **Verde** (Nível 1): Ângulo ≤ 20°
  - Posição neutra ou próxima do neutro
  - Mínima tensão nos músculos do ombro
  - Baixo risco de lesões por esforço repetitivo

- **Amarelo** (Nível 2): 20° < Ângulo ≤ 45°
  - Elevação moderada do braço
  - Aumento da atividade muscular no trapézio e deltóide
  - Potencial para fadiga em tarefas prolongadas

- **Laranja** (Nível 3): 45° < Ângulo ≤ 90°
  - Elevação significativa do braço
  - Alta atividade muscular no complexo do ombro
  - Risco aumentado de impacto no espaço subacromial
  - Potencial para tendinites e bursites

- **Vermelho** (Nível 4): Ângulo > 90°
  - Elevação extrema do braço
  - Máxima tensão nos músculos do ombro
  - Alto risco de síndrome do impacto e lesões no manguito rotador
  - Não recomendado para atividades prolongadas ou repetitivas

### Cotovelos/Antebraços

**Método de cálculo**: O ângulo do cotovelo/antebraço é calculado entre o ombro, cotovelo e pulso.

**Landmarks utilizados**:
- Ombro (ID: 12 para direito, 11 para esquerdo)
- Cotovelo (ID: 14 para direito, 13 para esquerdo)
- Pulso (ID: 16 para direito, 15 para esquerdo)

**Critérios de avaliação**:
- **Verde** (Nível 1): 60° ≤ Ângulo ≤ 100°
  - Posição funcional do cotovelo
  - Distribuição equilibrada da tensão entre bíceps e tríceps
  - Baixo estresse nas articulações do cotovelo
  - Posição ideal para a maioria das atividades

- **Amarelo** (Nível 2): Ângulo < 60° ou Ângulo > 100°
  - Flexão extrema ou extensão do cotovelo
  - Aumento da tensão nos tendões e ligamentos
  - Potencial para epicondilite (cotovelo de tenista/golfista)
  - Não recomendado para atividades prolongadas ou com carga

### Pulsos

**Método de cálculo**: O ângulo do pulso é calculado entre o cotovelo, pulso e dedo médio.

**Landmarks utilizados**:
- Cotovelo (ID: 14 para direito, 13 para esquerdo)
- Pulso (ID: 16 para direito, 15 para esquerdo)
- Dedo médio (ID: 18 para direito, 17 para esquerdo)

**Critérios de avaliação**:
- **Verde** (Nível 1): -15° ≤ Ângulo ≤ 15° (em relação à linha neutra do antebraço)
  - Posição neutra do pulso
  - Mínima pressão no túnel do carpo
  - Baixo risco de tendinites e síndrome do túnel do carpo

- **Amarelo** (Nível 2): -30° ≤ Ângulo < -15° ou 15° < Ângulo ≤ 30°
  - Desvio moderado do pulso
  - Aumento da pressão nas estruturas do pulso
  - Potencial para desconforto em uso prolongado

- **Vermelho** (Nível 3): Ângulo < -30° ou Ângulo > 30°
  - Desvio extremo do pulso
  - Alta pressão no túnel do carpo e tendões
  - Alto risco de síndrome do túnel do carpo e tendinites
  - Não recomendado mesmo para períodos curtos

### Joelhos

**Método de cálculo**: O ângulo do joelho é calculado entre o quadril, joelho e tornozelo.

**Landmarks utilizados**:
- Quadril (ID: 24 para direito, 23 para esquerdo)
- Joelho (ID: 26 para direito, 25 para esquerdo)
- Tornozelo (ID: 28 para direito, 27 para esquerdo)

**Critérios de avaliação (Suzanne Rodgers)**:
- **Verde** (Baixo Esforço - Nível 1): 160° ≤ Ângulo ≤ 180°
  - Posição quase reta (de pé ou sentado com pernas esticadas)
  - Distribuição equilibrada do peso corporal
  - Mínima tensão nos ligamentos e tendões do joelho
  - Baixa pressão patelar

- **Amarelo** (Moderado Esforço - Nível 2): 45° ≤ Ângulo ≤ 80° ou 80° < Ângulo < 160°
  - Flexão moderada do joelho (agachamento leve ou sentado com joelhos dobrados)
  - Aumento da pressão patelar
  - Maior ativação dos músculos da coxa
  - Aceitável para períodos curtos ou alternados com outras posturas

- **Vermelho** (Alto/Muito Alto Esforço - Nível 3+): Ângulo < 45°
  - Flexão extrema do joelho (agachamento profundo)
  - Máxima pressão patelar e nos meniscos
  - Alta tensão nos ligamentos cruzados
  - Não recomendado para períodos prolongados ou com carga

### Tornozelos

**Método de cálculo**: O ângulo do tornozelo é calculado em relação à horizontal.

**Landmarks utilizados**:
- Joelho (ID: 26 para direito, 25 para esquerdo)
- Tornozelo (ID: 28 para direito, 27 para esquerdo)

**Critérios de avaliação**:
- **Verde** (Nível 1): 80° ≤ Ângulo ≤ 110°
  - Posição neutra ou próxima do neutro
  - Distribuição equilibrada da pressão no pé
  - Baixa tensão nos tendões e ligamentos do tornozelo

- **Amarelo** (Nível 2): 70° ≤ Ângulo < 80° ou 110° < Ângulo ≤ 120°
  - Leve dorsiflexão ou flexão plantar
  - Aumento moderado da tensão nos tendões
  - Aceitável para períodos curtos

- **Vermelho** (Nível 3): Ângulo < 70° ou Ângulo > 120°
  - Dorsiflexão ou flexão plantar extrema
  - Alta tensão no tendão de Aquiles e outros tendões/ligamentos
  - Risco aumentado de entorses e tendinites
  - Não recomendado para períodos prolongados ou com carga

## Sistema de Pontuação

O sistema utiliza uma pontuação baseada nos níveis de risco de cada articulação:

- Nível 1 (Verde): 1 ponto
- Nível 2 (Amarelo): 2 pontos
- Nível 3 (Laranja): 3 pontos
- Nível 4 (Vermelho): 4 pontos

A pontuação total é calculada somando os pontos de todas as articulações avaliadas. A interpretação da pontuação total depende do número de articulações avaliadas, mas geralmente:

- **Baixo Risco**: Pontuação total ≤ 1.5 × (número de articulações)
- **Risco Moderado**: 1.5 × (número de articulações) < Pontuação total ≤ 2.5 × (número de articulações)
- **Alto Risco**: Pontuação total > 2.5 × (número de articulações)

## Interpretação dos Resultados

A interpretação dos resultados deve considerar:

1. **Pontuação total**: Indica o nível geral de risco ergonômico.
2. **Articulações críticas**: Articulações com pontuação 3 ou 4 requerem atenção imediata.
3. **Duração da postura**: Mesmo posturas de baixo risco podem se tornar problemáticas se mantidas por longos períodos.
4. **Frequência**: Movimentos repetitivos aumentam o risco, mesmo com ângulos favoráveis.
5. **Força aplicada**: A aplicação de força aumenta o risco em qualquer postura.

## Recomendações Ergonômicas

Com base nos resultados da avaliação, o sistema pode fornecer recomendações ergonômicas, como:

### Coluna Vertebral
- Manter a coluna alinhada com a vertical
- Utilizar apoio lombar ao sentar
- Alternar entre posições sentada e em pé
- Realizar pausas para alongamento

### Ombros
- Manter os braços próximos ao corpo
- Ajustar a altura da superfície de trabalho
- Evitar elevação prolongada dos braços
- Utilizar suportes para os braços quando apropriado

### Cotovelos/Antebraços
- Manter os cotovelos em ângulo próximo a 90°
- Posicionar objetos frequentemente utilizados ao alcance dos braços
- Evitar torção extrema dos antebraços

### Pulsos
- Manter os pulsos em posição neutra
- Utilizar apoios para os pulsos em tarefas de digitação
- Evitar desvios laterais extremos

### Joelhos
- Evitar agachamentos profundos por períodos prolongados
- Utilizar apoios para os joelhos em tarefas que exigem agachamento
- Manter os joelhos levemente flexionados ao ficar em pé por longos períodos

### Tornozelos
- Utilizar calçados adequados com bom suporte
- Evitar posições extremas dos pés
- Realizar movimentos de rotação dos tornozelos durante pausas

## Referências

### Critérios de Suzanne Rodgers para Joelhos

Os critérios de Suzanne Rodgers para avaliação do ângulo do joelho são baseados em estudos ergonômicos e biomecânicos. Os critérios classificam o ângulo do joelho em três níveis de esforço:

- **Baixo Esforço (Verde)**: 160° ≤ Ângulo ≤ 180° (quase reto, de pé ou sentado com pernas esticadas)
- **Moderado Esforço (Amarelo)**: 45° ≤ Ângulo ≤ 80° (agachamento leve ou joelhos muito dobrados ao sentar) ou 80° < Ângulo < 160° (outros ângulos)
- **Alto/Muito Alto Esforço (Vermelho)**: Ângulo < 45° (agachamento profundo)

### Métodos de Avaliação Ergonômica

1. **RULA (Rapid Upper Limb Assessment)**
   - Método para avaliar a exposição dos trabalhadores a fatores de risco associados a distúrbios dos membros superiores
   - Considera ângulos de braço, antebraço, pulso, pescoço, tronco e pernas
   - Pontuação final indica o nível de intervenção necessário

2. **REBA (Rapid Entire Body Assessment)**
   - Extensão do RULA que inclui avaliação do corpo inteiro
   - Considera fatores adicionais como carga/força e tipo de pega
   - Útil para avaliar tarefas que envolvem todo o corpo

3. **OWAS (Ovako Working Posture Analysing System)**
   - Sistema para identificar e avaliar posturas de trabalho inadequadas
   - Classifica posturas de costas, braços e pernas, além do peso da carga
   - Categoriza as posturas em quatro classes de ação

4. **Método de Suzanne Rodgers**
   - Avalia o esforço, duração e frequência de atividades musculares
   - Foca na fadiga muscular como indicador de risco
   - Utilizado para priorizar intervenções ergonômicas

### Referências Bibliográficas

1. Rodgers, S. H. (1992). A functional job analysis technique. Occupational Medicine: State of the Art Reviews, 7(4), 679-711.

2. McAtamney, L., & Corlett, E. N. (1993). RULA: a survey method for the investigation of work-related upper limb disorders. Applied Ergonomics, 24(2), 91-99.

3. Hignett, S., & McAtamney, L. (2000). Rapid Entire Body Assessment (REBA). Applied Ergonomics, 31(2), 201-205.

4. Karhu, O., Kansi, P., & Kuorinka, I. (1977). Correcting working postures in industry: A practical method for analysis. Applied Ergonomics, 8(4), 199-201.

5. Mediapipe Pose Landmarks: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker