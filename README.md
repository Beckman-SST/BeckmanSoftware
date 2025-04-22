# Sistema de Processamento de Imagens - Interface Web

Este projeto implementa uma interface web com Flask para o sistema de processamento de imagens e vídeos, substituindo a interface desktop anterior enquanto mantém toda a funcionalidade de processamento original.

## Funcionalidades

- Upload de múltiplas imagens e vídeos através de uma interface web intuitiva
- Processamento de arquivos utilizando o algoritmo de detecção existente (MediaPipe, OpenCV e YOLOv8)
- Visualização dos resultados processados em uma galeria
- Monitoramento do status de processamento em tempo real
- Possibilidade de cancelar processamentos em andamento
- Compatibilidade com os formatos: JPG, JPEG, PNG, MP4 e AVI

## Requisitos

- Python 3.6 ou superior
- Flask
- OpenCV
- MediaPipe
- YOLOv8 (Ultralytics)
- Outras dependências conforme o arquivo processamento.py original

## Como usar

1. Inicie o servidor Flask executando:
   ```
   python app.py
   ```

2. Acesse a interface web através do navegador em:
   ```
   http://127.0.0.1:5000
   ```

3. Faça o upload de imagens ou vídeos usando o botão "Escolher arquivos"

4. Clique em "Enviar para Processamento" para iniciar o processamento

5. Acompanhe o status do processamento e visualize os resultados na galeria

## Estrutura do Projeto

- `app.py`: Aplicação Flask principal
- `processamento.py`: Código de processamento original (mantido intacto)
- `templates/`: Pasta contendo os templates HTML
  - `index.html`: Interface web principal
- `uploads/`: Pasta para armazenamento temporário dos arquivos enviados
- `Output/`: Pasta onde os arquivos processados são salvos

## Observações

Esta interface web mantém toda a lógica de processamento do código original, incluindo:
- Detecção de landmarks do corpo usando MediaPipe
- Identificação de dispositivos eletrônicos usando YOLOv8
- Cálculo de ângulos e posicionamento
- Ocultação do rosto para privacidade
- Todas as outras funcionalidades específicas do processamento original