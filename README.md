# FinanSys

Controle financeiro pessoal e familiar que roda localmente no navegador. Desenvolvido com FastAPI, SQLAlchemy, SQLite e Jinja2, sem conta, assinatura ou servidor externo.

> Seus lanÃ§amentos ficam no arquivo `data/finansys.db` da sua prÃ³pria instalaÃ§Ã£o. Bancos, backups e exportaÃ§Ãµes sÃ£o ignorados pelo Git.

## Recursos

- Dashboard familiar e individual com receitas, despesas, saldo, categorias e alertas.
- LanÃ§amentos com busca, filtros, ediÃ§Ã£o, exclusÃ£o e parcelamento automÃ¡tico.
- Compras grandes parceladas por cartÃ£o, com loja, garantia, cronograma e saldo futuro.
- Faturas calculadas pelo fechamento e vencimento reais de cada cartÃ£o.
- Metas com aporte mensal, prazo estimado, projeÃ§Ã£o de 12 meses e valor necessÃ¡rio.
- Assinaturas recorrentes com geraÃ§Ã£o idempotente, sem cobranÃ§as duplicadas.
- Perfis da famÃ­lia, fontes de renda e planejamento de compras futuras.
- Fluxo de caixa, exportaÃ§Ã£o CSV/Excel/PDF e backups rotativos.
- Interface responsiva com temas claro e escuro.
- Central **Como usar** integrada ao aplicativo.

## InstalaÃ§Ã£o rÃ¡pida no Windows

1. Instale [Python 3.12 ou superior](https://www.python.org/downloads/).
2. Baixe o repositÃ³rio em **Code > Download ZIP** e extraia a pasta.
3. Execute `INICIAR_FINANSYS.bat`.

Na primeira execuÃ§Ã£o, o script cria o ambiente virtual e instala as dependÃªncias. Depois, o navegador abre em:

```text
http://127.0.0.1:8000
```

Para encerrar corretamente e gerar o backup automÃ¡tico, feche o servidor com `Ctrl+C` no terminal.

## InstalaÃ§Ã£o pelo terminal

### Windows PowerShell

```powershell
git clone https://github.com/erickgalvao04/FinanSys---Gest-o-de-Finan-as-pessoais.git
cd FinanSys
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

### Linux ou macOS

```bash
git clone https://github.com/erickgalvao04/FinanSys---Gest-o-de-Finan-as-pessoais.git
cd FinanSys
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python main.py
```

## Onde ficam os dados

| ConteÃºdo | Local |
|---|---|
| Banco principal | `data/finansys.db` |
| Backups manuais | `data/backups/` |
| Backups automÃ¡ticos no Windows | `Ãrea de Trabalho/Backups FinanSys/` |
| CÃ³digo da aplicaÃ§Ã£o | `app/` |
| Testes | `tests/` |

Nunca envie `finansys.db`, backups ou exportaÃ§Ãµes para um repositÃ³rio pÃºblico. O `.gitignore` deste projeto jÃ¡ bloqueia esses arquivos.

## Atualizar o projeto

FaÃ§a backup pelo aplicativo antes de atualizar. Em uma instalaÃ§Ã£o clonada com Git:

```powershell
git pull
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

As migraÃ§Ãµes existentes sÃ£o aditivas e executadas automaticamente na inicializaÃ§Ã£o.

## Desenvolvimento e testes

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m compileall -q app main.py
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

O GitHub Actions executa a suÃ­te em Python 3.12 e 3.13 a cada push e pull request.

## Arquitetura

```text
Navegador
  -> FastAPI / Jinja2
  -> rotas e regras de negÃ³cio
  -> SQLAlchemy
  -> SQLite local
```

A aplicaÃ§Ã£o Ã© deliberadamente simples: nÃ£o usa React, Node.js, Docker ou servidor de banco externo.

## DocumentaÃ§Ã£o

- [Manual de uso](docs/MANUAL_USUARIO.md)
- [Arquitetura e personalizaÃ§Ã£o](docs/ARQUITETURA_E_PERSONALIZACAO.md)
- [ManutenÃ§Ã£o e soluÃ§Ã£o de problemas](docs/MANUTENCAO.md)
- [Como contribuir](CONTRIBUTING.md)
- [PolÃ­tica de seguranÃ§a](SECURITY.md)

## SeguranÃ§a e escopo

O FinanSys nÃ£o possui login porque foi projetado para uso pessoal em `127.0.0.1`. NÃ£o exponha a aplicaÃ§Ã£o diretamente Ã  internet. Uma versÃ£o hospedada para mÃºltiplos usuÃ¡rios exigiria autenticaÃ§Ã£o, isolamento dos dados, HTTPS, proteÃ§Ã£o CSRF e revisÃ£o de seguranÃ§a.

Este projeto nÃ£o substitui aconselhamento financeiro, contÃ¡bil ou tributÃ¡rio.

## LicenÃ§a

DistribuÃ­do sob a [LicenÃ§a MIT](LICENSE).
