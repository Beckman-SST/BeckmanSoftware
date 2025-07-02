# Critérios de Avaliação do Sistema de Processamento de Vídeos

## Visão Geral

Esta seção documenta os critérios de avaliação utilizados pelo Sistema de Processamento de Vídeos para analisar a postura e ergonomia em vídeos. Os critérios são baseados em metodologias estabelecidas de ergonomia e biomecânica, adaptados para análise automatizada de vídeo.

## Conteúdo

### [Critérios de Angulação](./angulacao.md)

Documentação detalhada sobre os critérios de avaliação de ângulos entre articulações, incluindo:

- Metodologia de avaliação
- Critérios por articulação (coluna, ombros, cotovelos/antebraços, pulsos, joelhos, tornozelos)
- Sistema de pontuação
- Interpretação dos resultados
- Recomendações ergonômicas

## Metodologia Geral

O sistema utiliza uma abordagem baseada em evidências para avaliar a postura e ergonomia, combinando várias metodologias estabelecidas:

1. **Critérios de Suzanne Rodgers**: Utilizados principalmente para avaliação de joelhos e outras articulações de membros inferiores.

2. **RULA (Rapid Upper Limb Assessment)**: Adaptado para avaliação de membros superiores, incluindo ombros, cotovelos e pulsos.

3. **REBA (Rapid Entire Body Assessment)**: Utilizado para avaliação da postura corporal como um todo.

4. **OWAS (Ovako Working Posture Analyzing System)**: Considerado para classificação de posturas de trabalho.

## Sistema de Pontuação

O sistema utiliza um esquema de pontuação de 1 a 3 para classificar o risco ergonômico:

- **1 (Verde)**: Postura adequada, baixo risco ergonômico
- **2 (Amarelo)**: Postura moderadamente inadequada, risco ergonômico moderado
- **3 (Vermelho)**: Postura inadequada, alto risco ergonômico

Esta pontuação é aplicada a cada articulação analisada e pode ser visualizada no vídeo processado através de um código de cores.

## Landmarks Utilizados

O sistema utiliza os landmarks do MediaPipe Pose para detectar pontos-chave do corpo. Estes landmarks são utilizados para calcular ângulos entre articulações, que são então avaliados com base nos critérios estabelecidos.

Para detalhes sobre os landmarks específicos utilizados para cada articulação, consulte a [documentação de angulação](./angulacao.md).

## Extensibilidade

O sistema foi projetado para ser extensível, permitindo a adição de novos critérios de avaliação ou a modificação dos existentes. Para adicionar novos critérios, consulte o [guia de manutenção](../guias/manutencao.md).

## Referências

- Rodgers, S. H. (1992). A functional job analysis technique. Occupational Medicine: State of the Art Reviews, 7(4), 679-711.
- McAtamney, L., & Corlett, E. N. (1993). RULA: a survey method for the investigation of work-related upper limb disorders. Applied Ergonomics, 24(2), 91-99.
- Hignett, S., & McAtamney, L. (2000). Rapid Entire Body Assessment (REBA). Applied Ergonomics, 31(2), 201-205.
- Karhu, O., Kansi, P., & Kuorinka, I. (1977). Correcting working postures in industry: A practical method for analysis. Applied Ergonomics, 8(4), 199-201.
- [MediaPipe Pose Landmarks](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker)