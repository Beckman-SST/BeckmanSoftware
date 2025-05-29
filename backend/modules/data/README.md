# Estrutura de Dados do Sistema

Este diretório contém os dados utilizados pelo sistema de análise de postura.

## Estrutura de Pastas

- `images/`: Contém as imagens de entrada para processamento
- `videos/`: Contém os vídeos de entrada para processamento
- `output/`: Contém os resultados do processamento (imagens e vídeos processados)
- `uploads/`: Diretório temporário para arquivos enviados pelo usuário
- `merge/`: Contém as imagens resultantes da união de múltiplas imagens

## Uso

Os arquivos de entrada (imagens e vídeos) devem ser colocados nas pastas correspondentes para processamento pelo sistema. Os resultados serão salvos na pasta `output/`.

## Observações

- As pastas são criadas automaticamente pelo sistema se não existirem
- Os formatos suportados para imagens são: jpg, jpeg, png
- Os formatos suportados para vídeos são: mp4, avi, mov