# Guia de Instalação do TensorFlow para DeepLabCut

## Situação Atual

- **TensorFlow instalado:** Versão 2.18.0
- **Versão recomendada para DeepLabCut:** 2.5.0
- **Suporte a GPU:** Não detectado
- **DeepLabCut:** Não instalado corretamente

## Problema Identificado

O DeepLabCut requer uma versão específica do TensorFlow (2.5.0) para funcionar corretamente. Atualmente, você tem a versão 2.18.0 instalada, que é mais recente, mas pode não ser compatível com o DeepLabCut.

## Solução Recomendada

1. **Criar um ambiente virtual** para isolar as dependências:

```bash
python -m venv dlc_env
```

2. **Ativar o ambiente virtual**:

- No Windows:
```bash
dlc_env\Scripts\activate
```

3. **Desinstalar a versão atual do TensorFlow**:

```bash
pip uninstall -y tensorflow tensorflow-gpu
```

4. **Instalar a versão compatível do TensorFlow**:

```bash
pip install tensorflow==2.5.0
```

Ou, se tiver GPU NVIDIA compatível:

```bash
pip install tensorflow-gpu==2.5.0
```

5. **Instalar o DeepLabCut**:

```bash
pip install deeplabcut
```

6. **Verificar a instalação**:

```bash
python -c "import deeplabcut; print('DeepLabCut versão:', deeplabcut.__version__)"
```

## Observações Importantes

- O arquivo `requirements.txt` foi atualizado para incluir `tensorflow==2.5.0`
- Para utilizar GPU com TensorFlow 2.5.0, você precisará de:
  - CUDA Toolkit 11.0-11.2
  - cuDNN 8.0.x
  - Drivers NVIDIA atualizados

## Solução de Problemas

Se encontrar o erro `AttributeError: _ARRAY_API not found` ao importar o OpenCV:

1. Reinstale o OpenCV com uma versão específica:

```bash
pip uninstall -y opencv-python
pip install opencv-python==4.5.3.56
```

2. Verifique se há conflitos entre pacotes:

```bash
pip check
```