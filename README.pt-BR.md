# GhostBudget

[English](README.md) | [Português](README.pt-BR.md)

Um aplicativo desktop de finanças pessoais feito com Python e Flet.

> **Aviso:** Este é um projeto pessoal desenvolvido por um único desenvolvedor para uso próprio. Está sendo desenvolvido com o auxílio do [Claude Code](https://claude.ai/code).

## Funcionalidades

- Dashboard mensal com resumo de receitas, despesas e saldo
- Adicionar e editar transações (receitas e despesas)
- Categorias personalizáveis com cor e ícone
- Navegação entre meses
- Controle de investimentos com depósitos e retiradas
- Planejamento de mês ideal com comparação com os gastos reais
- Interface disponível em inglês e português (BR)
- Backup e restauração via Google Drive (opcional)

## Stack

- [Python 3.11+](https://www.python.org/)
- [Flet](https://flet.dev/) — framework de UI desktop para Python
- SQLite — banco de dados local
- Google Drive API — sincronização opcional

## Instalação

**1. Clone o repositório**

```bash
git clone https://github.com/your-username/GhostBudget.git
cd GhostBudget
```

**2. Crie e ative um ambiente virtual**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Execute o app**

```bash
python main.py
```

## Sincronização com Google Drive (opcional)

O Google Drive permite fazer backup e restaurar o banco de dados entre dispositivos. A configuração é feita uma única vez.

### Pré-requisitos

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a **Google Drive API** (APIs e Serviços → Biblioteca)
4. Crie credenciais OAuth 2.0 (APIs e Serviços → Credenciais → Criar Credenciais → ID do cliente OAuth → App de computador)
5. Baixe o arquivo JSON gerado e renomeie para `credentials.json`
6. Coloque o `credentials.json` na pasta raiz do GhostBudget

A estrutura esperada do arquivo está documentada em `credentials.example.json`.

### Vinculando sua conta

Com o `credentials.json` no lugar, abra o app, vá em **Configurações** e clique em **Vincular conta Google**. Uma janela do navegador abrirá para autorização — após confirmada, o app estará pronto para fazer upload e restaurar backups.

> O token de acesso é salvo em `data/gdrive_token.json` e atualizado automaticamente. O app acessa apenas os arquivos que ele mesmo criou no seu Drive.

## Estrutura do projeto

```
GhostBudget/
├── main.py                  # Ponto de entrada
├── state.py                 # Estado global do app
├── i18n.py                  # Internacionalização (EN / PT-BR)
├── requirements.txt
├── credentials.example.json # Modelo para configuração do Google Drive
├── models/                  # Acesso ao banco de dados
├── controllers/             # Lógica de negócio
├── views/                   # Telas do app
├── components/              # Componentes de UI reutilizáveis (navbar)
├── sync/                    # Integração com Google Drive
├── locales/                 # Arquivos de tradução (en.json, pt.json)
└── data/                    # Banco de dados e configuração (gerados automaticamente)
```

## Dados locais

O banco de dados SQLite é armazenado em `data/budget.db` e criado automaticamente na primeira execução. A pasta `data/` não é versionada.
