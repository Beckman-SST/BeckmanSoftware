# Guia de Contribuição

## Bem-vindo!

Obrigado por considerar contribuir para o Sistema de Processamento de Vídeos! Este documento fornece diretrizes e instruções para contribuir com o projeto.

## Índice

1. [Código de Conduta](#código-de-conduta)
2. [Como Posso Contribuir?](#como-posso-contribuir)
   - [Reportando Bugs](#reportando-bugs)
   - [Sugerindo Melhorias](#sugerindo-melhorias)
   - [Contribuindo com Código](#contribuindo-com-código)
3. [Estilo de Código](#estilo-de-código)
4. [Processo de Desenvolvimento](#processo-de-desenvolvimento)
   - [Branches](#branches)
   - [Commits](#commits)
   - [Pull Requests](#pull-requests)
5. [Testes](#testes)
6. [Documentação](#documentação)

## Código de Conduta

Este projeto e todos os participantes estão sujeitos a um Código de Conduta. Ao participar, espera-se que você mantenha este código. Por favor, reporte comportamentos inaceitáveis.

## Como Posso Contribuir?

### Reportando Bugs

Antes de criar um relatório de bug, verifique se o problema já foi reportado. Se não, crie um novo relatório incluindo:

- Um título claro e descritivo
- Passos detalhados para reproduzir o problema
- Comportamento esperado e comportamento observado
- Capturas de tela, se aplicável
- Ambiente (sistema operacional, versão do Python, etc.)

### Sugerindo Melhorias

Antes de criar uma sugestão de melhoria, verifique se a melhoria já foi sugerida. Se não, crie uma nova sugestão incluindo:

- Um título claro e descritivo
- Descrição detalhada da melhoria proposta
- Justificativa para a melhoria
- Possíveis implementações, se aplicável

### Contribuindo com Código

1. Escolha uma issue para trabalhar ou crie uma nova
2. Faça fork do repositório
3. Crie uma branch para sua contribuição
4. Implemente suas mudanças
5. Adicione ou atualize testes, se aplicável
6. Atualize a documentação, se aplicável
7. Certifique-se de que os testes passam
8. Crie um Pull Request

## Estilo de Código

O projeto segue o estilo de código PEP 8. Recomendamos o uso de ferramentas como `flake8` e `black` para verificar e formatar o código:

```bash
# Verificar estilo de código
flake8 .

# Formatar código
black .
```

Além disso, siga estas diretrizes:

- Use docstrings no estilo Google para documentar classes, métodos e funções
- Use nomes descritivos para variáveis, funções, classes, etc.
- Mantenha funções e métodos pequenos e focados em uma única responsabilidade
- Adicione comentários para explicar código complexo ou não óbvio

## Processo de Desenvolvimento

### Branches

- `main`: Branch principal, contém código estável e pronto para produção
- `develop`: Branch de desenvolvimento, contém código em desenvolvimento para a próxima versão
- `feature/<nome-da-feature>`: Branches para desenvolvimento de novas funcionalidades
- `bugfix/<nome-do-bug>`: Branches para correção de bugs
- `release/<versão>`: Branches para preparação de releases

### Commits

- Faça commits pequenos e frequentes
- Use mensagens de commit claras e descritivas
- Use o tempo presente ("Adiciona feature" em vez de "Adicionada feature")
- Referencie issues e pull requests, se aplicável

Exemplo de mensagem de commit:

```
Adiciona cálculo de ângulo do tornozelo

- Implementa função para calcular ângulo do tornozelo
- Adiciona critérios de avaliação para ângulo do tornozelo
- Atualiza visualização para mostrar ângulo do tornozelo

Resolve #123
```

### Pull Requests

- Use um título claro e descritivo
- Inclua uma descrição detalhada das mudanças
- Referencie issues relacionadas
- Certifique-se de que os testes passam
- Solicite revisão de pelo menos um membro da equipe

## Testes

O projeto utiliza o framework de testes `unittest` do Python. Para executar os testes:

```bash
python -m unittest discover tests
```

Ao contribuir com código, certifique-se de:

- Adicionar ou atualizar testes para suas mudanças
- Verificar se todos os testes passam antes de criar um Pull Request
- Manter a cobertura de testes alta

## Documentação

A documentação é uma parte crucial do projeto. Ao contribuir, certifique-se de:

- Atualizar a documentação para refletir suas mudanças
- Adicionar docstrings para novas classes, métodos e funções
- Atualizar o README.md, se aplicável
- Atualizar o CHANGELOG.md para novas funcionalidades ou correções de bugs

A documentação do projeto está organizada da seguinte forma:

- `docs/api/`: Documentação da API
- `docs/arquitetura/`: Documentação de arquitetura
- `docs/criterios/`: Documentação de critérios
- `docs/guias/`: Guias de uso e manutenção
- `docs/tecnico/`: Documentação técnica

Para mais informações sobre como documentar o código, consulte o [guia de manutenção](./guias/manutencao.md).

---

Obrigado por contribuir para o Sistema de Processamento de Vídeos!