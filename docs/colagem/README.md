# Documentação - Sistema de Colagem

## Visão Geral

O Sistema de Colagem é uma funcionalidade completa que permite aos usuários selecionar, organizar e criar colagens personalizadas de imagens processadas. O sistema oferece interface intuitiva para seleção de imagens, nomeação personalizada de grupos e geração automática de colagens com texto flutuante.

## Arquitetura

### Frontend
- **Template**: `colagem.html`
- **JavaScript**: `colagem.js`
- **Estilos**: CSS integrado no template

### Backend
- **Servidor**: Flask (Python)
- **Arquivo principal**: `app.py`
- **Processamento de imagens**: PIL (Python Imaging Library)

## Funcionalidades Principais

### 1. Visualização de Imagens
- Categorização automática (Executivo/Operacional)
- Exibição em grid responsivo
- Indicadores visuais para imagens já utilizadas
- Modal para visualização ampliada

### 2. Seleção de Grupos
- Seleção múltipla de até 3 imagens por grupo
- Indicadores numerados coloridos
- Nomeação personalizada de grupos
- Criação manual via botão "Próximo Grupo"

### 3. Geração de Colagens
- Redimensionamento automático mantendo proporções
- Texto flutuante com nome do grupo
- Formato PNG para qualidade superior
- Processamento em lote de múltiplos grupos

## Estrutura de Arquivos

```
frontend/public/
├── colagem.html          # Template principal
└── js/
    └── colagem.js        # Lógica de interface

backend/
└── app.py               # APIs e processamento
```

## Próximas Seções

- [Template Frontend](./template.md)
- [Backend APIs](./backend.md)
- [Guia de Uso](./guia-uso.md)
- [Troubleshooting](./troubleshooting.md)