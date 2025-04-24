# Reorganização do Projeto RePosture

## Visão Geral

Este documento explica a reorganização proposta para o projeto RePosture, visando melhorar a estrutura de arquivos e pastas para facilitar a manutenção e o desenvolvimento futuro.

## Problemas Identificados

1. **Duplicação de arquivos**: Existem arquivos CSS e JavaScript duplicados entre as pastas `frontend` e `static`
2. **Templates espalhados**: Arquivos HTML estão em diferentes locais (`backend/templates` e raiz)
3. **Falta de estrutura clara**: Não há separação clara entre frontend e backend
4. **Recursos desorganizados**: Imagens, vídeos e modelos estão espalhados em diferentes pastas

## Nova Estrutura Proposta

A nova estrutura segue o padrão MVC (Model-View-Controller) e organiza os arquivos de forma mais lógica:

```
BeckmanSoftware/
├── backend/               # Código do servidor e processamento
│   ├── app.py            # Aplicação principal
│   ├── processamento.py  # Lógica de processamento
│   ├── config.json       # Configurações
│   ├── logs/             # Logs do sistema
│   ├── uploads/          # Uploads temporários
│   ├── Output/           # Resultados processados
│   └── models/           # Modelos ML (yolov8n.pt, etc.)
├── frontend/             # Interface do usuário
│   ├── static/           # Recursos estáticos
│   │   ├── css/          # Estilos CSS
│   │   ├── js/           # Scripts JavaScript
│   │   └── images/       # Imagens da interface
│   └── templates/        # Templates HTML
├── data/                 # Dados para testes
│   ├── images/           # Imagens de teste
│   └── videos/           # Vídeos de teste
└── docs/                 # Documentação
```

## Como Proceder com a Reorganização

Para implementar esta reorganização, siga os passos detalhados no arquivo `script_migracao.md` que foi criado para orientar o processo de migração passo a passo.

### Principais Etapas

1. Criar a nova estrutura de pastas
2. Mover os arquivos HTML para `frontend/templates`
3. Consolidar arquivos CSS e JS em `frontend/static`
4. Atualizar referências nos arquivos HTML
5. Mover modelos ML para `backend/models`
6. Atualizar caminhos no código Python

## Benefícios da Nova Estrutura

- **Organização lógica**: Separação clara entre frontend e backend
- **Eliminação de duplicações**: Arquivos únicos em locais apropriados
- **Manutenção simplificada**: Facilidade para encontrar e modificar arquivos
- **Escalabilidade**: Estrutura preparada para crescimento do projeto
- **Padrões de desenvolvimento**: Alinhamento com práticas modernas de desenvolvimento web

## Documentação Adicional

- `plano_reorganizacao.md`: Detalhes completos do plano de reorganização
- `script_migracao.md`: Comandos e passos para executar a migração

## Recomendações

1. Faça um backup completo do projeto antes de iniciar a reorganização
2. Execute os passos de migração em um ambiente de desenvolvimento
3. Teste a aplicação após cada etapa importante
4. Verifique se todas as funcionalidades continuam operando corretamente após a migração