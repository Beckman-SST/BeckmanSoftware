# Guia de Instalação do DeepLabCut

Este guia fornece instruções detalhadas para instalar o DeepLabCut e suas dependências no seu sistema.

## Requisitos do Sistema

- Windows 10/11, macOS ou Linux
- Python 3.7, 3.8 ou 3.9 (recomendado: 3.8)
- GPU NVIDIA com CUDA (recomendado para treinamento)

## Instalação Passo a Passo

### 1. Instalar Anaconda ou Miniconda

Recomendamos usar um ambiente virtual Conda para evitar conflitos com outros pacotes Python.

1. Baixe e instale [Anaconda](https://www.anaconda.com/products/distribution) ou [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

### 2. Criar e Ativar Ambiente Conda

Abra o Anaconda Prompt (Windows) ou Terminal (macOS/Linux) e execute:

```bash
# Criar novo ambiente com Python 3.8
conda create -n dlc python=3.8

# Ativar o ambiente
conda activate dlc
```

### 3. Instalar DeepLabCut

```bash
# Instalar versão estável do DeepLabCut
pip install deeplabcut

# OU instalar a versão mais recente do GitHub (opcional)
# pip install git+https://github.com/DeepLabCut/DeepLabCut.git
```

### 4. Instalar TensorFlow com Suporte a GPU (Opcional, mas Recomendado)

Para treinamento mais rápido, instale TensorFlow com suporte a GPU:

```bash
# Para GPU NVIDIA
pip install tensorflow-gpu==2.5.0
```

### 5. Verificar a Instalação

```bash
python -c "import deeplabcut; print('DeepLabCut versão:', deeplabcut.__version__)"
```

## Solução de Problemas Comuns

### Erro de DLL não encontrada (Windows)

Se você encontrar erros relacionados a DLLs ausentes ao usar GPU:

1. Instale o [Visual C++ Redistributable](https://aka.ms/vs/16/release/vc_redist.x64.exe)
2. Instale os drivers NVIDIA mais recentes
3. Instale o [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) compatível com sua versão do TensorFlow

### Erro de Importação do wxPython

Se encontrar erros ao importar wxPython (necessário para a interface gráfica):

```bash
pip uninstall wxPython
pip install wxPython
```

## Próximos Passos

Após a instalação bem-sucedida:

1. Adicione algumas imagens de exemplo na pasta `dlc_cotovelo_pulso/imagens_exemplo/`
2. Execute o script de treinamento: `python treinamento.py`
3. Siga as instruções no terminal para criar e configurar seu projeto

Consulte o arquivo README.md para mais detalhes sobre o fluxo de trabalho completo.