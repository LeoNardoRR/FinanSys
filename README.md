# FinanSys

Controle financeiro pessoal e familiar que roda localmente no navegador. Desenvolvido com FastAPI, SQLAlchemy, SQLite e Jinja2, sem conta, assinatura ou servidor externo.

> Seus lançamentos ficam no arquivo `data/finansys.db` da sua própria instalação. Bancos, backups e exportações são ignorados pelo Git.

## Recursos

- Dashboard familiar e individual com receitas, despesas, saldo, categorias e alertas.
- Lançamentos com busca, filtros, edição, exclusão e parcelamento automático.
- Compras grandes parceladas por cartão, com loja, garantia, cronograma e saldo futuro.
- Faturas calculadas pelo fechamento e vencimento reais de cada cartão.
- Metas com aporte mensal, prazo estimado, projeção de 12 meses e valor necessário.
- Assinaturas recorrentes com geração idempotente, sem cobranças duplicadas.
- Perfis da família, fontes de renda e planejamento de compras futuras.
- Fluxo de caixa, exportação CSV/Excel/PDF e backups rotativos.
- Interface responsiva com temas claro e escuro.
- Central **Como usar** integrada ao aplicativo.

## Instalação rápida no Windows

1. Instale [Python 3.12 ou superior](https://www.python.org/downloads/).
2. Baixe o repositório em **Code > Download ZIP** e extraia a pasta.
3. Execute `INICIAR_FINANSYS.bat`.

Na primeira execução, o script cria o ambiente virtual e instala as dependências. Depois, o navegador abre em:

```text
http://127.0.0.1:8000
```

Para encerrar corretamente e gerar o backup automático, feche o servidor com `Ctrl+C` no terminal.

## Instalação pelo terminal

### Windows PowerShell

```powershell
git clone https://github.com/erickgalvao04/FinanSys.git
cd FinanSys
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

### Linux ou macOS

```bash
git clone https://github.com/erickgalvao04/FinanSys.git
cd FinanSys
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python main.py
```

## Onde ficam os dados

| Conteúdo | Local |
|---|---|
| Banco principal | `data/finansys.db` |
| Backups manuais | `data/backups/` |
| Backups automáticos no Windows | `Área de Trabalho/Backups FinanSys/` |
| Código da aplicação | `app/` |
| Testes | `tests/` |

Nunca envie `finansys.db`, backups ou exportações para um repositório público. O `.gitignore` deste projeto já bloqueia esses arquivos.

## Atualizar o projeto

Faça backup pelo aplicativo antes de atualizar. Em uma instalação clonada com Git:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

As migrações existentes são aditivas e executadas automaticamente na inicialização.

## Desenvolvimento e testes

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m compileall -q app main.py
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

O GitHub Actions executa a suíte em Python 3.12 e 3.13 a cada push e pull request.

## Arquitetura

```text
Navegador
  -> FastAPI / Jinja2
  -> rotas e regras de negócio
  -> SQLAlchemy
  -> SQLite local
```

A aplicação é deliberadamente simples: não usa React, Node.js, Docker ou servidor de banco externo.

## Documentação

- [Manual de uso](docs/MANUAL_USUARIO.md)
- [Arquitetura e personalização](docs/ARQUITETURA_E_PERSONALIZACAO.md)
- [Manutenção e solução de problemas](docs/MANUTENCAO.md)
- [Como contribuir](CONTRIBUTING.md)
- [Política de segurança](SECURITY.md)

## Segurança e escopo

O FinanSys não possui login porque foi projetado para uso pessoal em `127.0.0.1`. Não exponha a aplicação diretamente à internet. Uma versão hospedada para múltiplos usuários exigiria autenticação, isolamento dos dados, HTTPS, proteção CSRF e revisão de segurança.

Este projeto não substitui aconselhamento financeiro, contábil ou tributário.

## Licença

Distribuído sob a [Licença MIT](LICENSE).
