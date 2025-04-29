# Treinamento DeepLabCut para Visão Top-Down

Este diretório contém os arquivos necessários para treinar um modelo DeepLabCut especializado em análise de cotovelo e pulso em visão top-down.

## Estrutura de Pastas

```
topdown_vision/
├── treinamento.py         # Script principal para criar e configurar o projeto
├── dlc_cotovelo_pulso/    # Diretório do projeto (criado automaticamente)
│   ├── imagens_exemplo/   # Pasta para armazenar imagens de exemplo
│   └── ...                # Outros arquivos gerados pelo DeepLabCut
└── README.md              # Este arquivo
```

## Requisitos

Antes de começar, você precisa instalar o DeepLabCut e suas dependências:

```bash
# Criar ambiente conda (recomendado)
conda create -n dlc python=3.8
conda activate dlc

# Instalar DeepLabCut
pip install deeplabcut

# Ou para a versão mais recente do GitHub
pip install git+https://github.com/DeepLabCut/DeepLabCut.git
```

## Como Usar

### 1. Preparação

Antes de executar o script, você precisa:

1. Adicionar imagens de exemplo na pasta `dlc_cotovelo_pulso/imagens_exemplo/`
   - Use imagens de alta qualidade da visão top-down
   - Recomenda-se pelo menos 5-10 imagens representativas
   - Formatos suportados: JPG, JPEG, PNG

### 2. Executar o Script de Treinamento

```bash
python treinamento.py
```

O script irá:
1. Verificar se já existe um projeto
2. Criar diretórios necessários
3. Criar um novo projeto DeepLabCut se necessário
4. Guiar você pelos próximos passos do processo

### 3. Fluxo de Trabalho Completo

Após a criação do projeto, siga estas etapas:

1. **Extrair frames para rotulagem**
   ```python
   import deeplabcut
   config_path = "caminho/para/config.yaml"
   deeplabcut.extract_frames(config_path, 'automatic', 'kmeans')
   ```

2. **Rotular frames** (interface gráfica)
   ```python
   deeplabcut.label_frames(config_path)
   ```

3. **Verificar rótulos**
   ```python
   deeplabcut.check_labels(config_path)
   ```

4. **Criar conjunto de treinamento**
   ```python
   deeplabcut.create_training_dataset(config_path)
   ```

5. **Treinar rede**
   ```python
   deeplabcut.train_network(config_path)
   ```

6. **Avaliar o modelo**
   ```python
   deeplabcut.evaluate_network(config_path)
   ```

7. **Analisar novos vídeos**
   ```python
   deeplabcut.analyze_videos(config_path, ["caminho/para/video.mp4"])
   ```

## Integração com o Sistema

Após o treinamento, o modelo pode ser integrado ao sistema principal para análise de cotovelo e pulso em tempo real. Consulte a documentação do sistema principal para detalhes sobre como integrar modelos DeepLabCut treinados.

## Referências

- [Documentação oficial do DeepLabCut](http://www.mackenziemathislab.org/deeplabcut)
- [GitHub do DeepLabCut](https://github.com/DeepLabCut/DeepLabCut)
- [Tutorial de DeepLabCut](https://github.com/DeepLabCut/DeepLabCut/blob/master/docs/UseOverviewGuide.md)