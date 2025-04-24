# Plano de Reorganização do Projeto RePosture

## Problemas Identificados

1. Arquivos duplicados entre as pastas `frontend` e `static`
2. Templates HTML duplicados entre `backend/templates` e raiz do projeto
3. Arquivos estáticos (CSS, JS) espalhados em diferentes locais
4. Falta de uma estrutura clara entre frontend e backend

## Nova Estrutura de Pastas

```
BeckmanSoftware/
├── backend/
│   ├── app.py                  # Aplicação principal
│   ├── processamento.py        # Lógica de processamento
│   ├── config.json             # Configurações do backend
│   ├── logs/                   # Pasta de logs
│   ├── uploads/                # Uploads temporários
│   ├── Output/                 # Resultados processados
│   └── models/                 # Modelos de ML (yolov8n.pt, etc.)
├── frontend/
│   ├── static/                 # Arquivos estáticos
│   │   ├── css/                # Estilos CSS
│   │   ├── js/                 # Scripts JavaScript
│   │   └── images/             # Imagens da interface
│   └── templates/              # Templates HTML
│       ├── index.html          # Página principal
│       ├── config.html         # Configurações
│       └── logs.html           # Gerenciamento de logs
├── data/                       # Dados para testes
│   ├── images/                 # Imagens de teste
│   └── videos/                 # Vídeos de teste
├── README.md                   # Documentação do projeto
├── requirements.txt            # Dependências do projeto
└── render.yaml                 # Configuração de deploy
```

## Plano de Migração

1. Criar a nova estrutura de pastas
2. Mover os arquivos HTML para `frontend/templates`
3. Consolidar arquivos CSS e JS em `frontend/static`
4. Atualizar referências nos arquivos HTML
5. Mover modelos ML para `backend/models`
6. Atualizar caminhos no código Python
7. Testar a aplicação após a reorganização

## Benefícios da Nova Estrutura

- Separação clara entre frontend e backend
- Eliminação de arquivos duplicados
- Organização lógica dos recursos
- Facilidade de manutenção e desenvolvimento
- Melhor escalabilidade do projeto