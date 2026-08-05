# Arquitetura e personalização

## Fluxo da aplicação

```text
Navegador
  → rotas FastAPI (`app/routes`)
  → regras de negócio (`app/services` e funções das rotas)
  → modelos SQLAlchemy (`app/models`)
  → SQLite (`data/finansys.db`)
  → templates Jinja2 (`app/templates`) + CSS/JS (`app/static`)
```

## Arquivos principais

- `main.py`: cria a aplicação, inicializa o banco, registra rotas e inicia o servidor.
- `app/settings.py`: caminhos, nome da aplicação e URL do banco.
- `app/database.py`: engine SQLAlchemy, sessões, criação de tabelas e migrações aditivas.
- `app/models/core.py`: categorias, bancos, cartões, pagamentos, metas e assinaturas.
- `app/models/planning.py`: pessoas, fontes de renda e gastos previstos.
- `app/models/transaction.py`: lançamentos, parcelas, tags e vínculo opcional com uma compra.
- `app/models/purchase.py`: produto comprado, cartão, garantia, totais e período do parcelamento.
- `app/services/dashboard.py`: totais, gráficos, métricas individuais e alertas.
- `app/utils.py`: valores monetários, datas, parcelas e ciclo de cartão.
- `app/routes/*.py`: endpoints GET/POST de cada módulo.
- `app/templates/base.html`: menu, cabeçalho e estrutura compartilhada.
- `app/templates/*.html`: conteúdo de cada tela.
- `app/static/css/app.css`: sistema visual completo, responsividade e modo escuro.
- `app/static/js/theme.js`: persistência do tema no `localStorage`.

## Como alterar textos e telas

Edite o HTML correspondente em `app/templates/`. O arquivo herda `base.html` e preenche `{% block content %}`. Reinicie o programa ou, no modo atual com `reload=True`, salve e atualize o navegador.

O Jinja usa:

- `{{ valor }}` para imprimir dados;
- `{% if ... %}` para condições;
- `{% for item in itens %}` para listas.

Não renomeie campos `name="..."` de formulários sem atualizar o parâmetro de mesmo nome na rota Python.

## Como alterar cores e aparência

Edite as variáveis no início de `app/static/css/app.css`:

```css
:root { --primary: #2563eb; --bg: #f4f7fb; }
html[data-theme=dark] { --primary: #60a5fa; --bg: #0b1120; }
```

Classes reutilizáveis:

- `.card`, `.card-header`, `.card-body`;
- `.grid`, `.grid-2`, `.grid-3`, `.grid-4`;
- `.btn`, `.btn-primary`, `.btn-danger`;
- `.form-grid`, `.field`, `.control`;
- `.table`, `.table-wrap`;
- `.positive`, `.negative`, `.warning`.

## Como adicionar uma página

1. Crie `app/routes/nova_pagina.py` com um `APIRouter`.
2. Crie `app/templates/nova_pagina.html` estendendo `base.html`.
3. Importe o router em `main.py` e adicione-o à tupla de routers.
4. Adicione o link no menu de `base.html`.
5. Adicione teste HTTP em `tests/test_navigation.py`.

## Como adicionar um campo ao banco

1. Acrescente a coluna tipada no modelo SQLAlchemy.
2. Em `initialize_database()` de `app/database.py`, adicione `_add_column(...)` com SQL SQLite compatível.
3. Ajuste formulários, rota de gravação e template de leitura.
4. Faça backup e teste numa cópia antes de abrir o banco principal.

As migrações existentes são aditivas e não apagam dados. Evite renomear/remover colunas diretamente.

## Regras financeiras importantes

- Valores são `Decimal` e armazenados como `NUMERIC(12,2)`; não use `float` para cálculos monetários.
- `parse_money()` aceita `1.234,56` e `1234.56`.
- Parcelas usam `add_months()` e `split_installments()`; a diferença de centavos fica na última parcela.
- Compras de produtos criam uma linha em `purchases` e lançamentos mensais ligados por `transactions.purchase_id`.
- O ciclo de cartão vem de `invoice_cycle()` e usa intervalo inclusivo.
- Filtros individuais dependem de `person_id`; `NULL` significa Família/não atribuído.
- Geração de assinatura verifica ocorrência/data/cartão antes de inserir.

## Bibliotecas

- FastAPI: servidor e rotas.
- SQLAlchemy: banco e consultas.
- Jinja2: HTML dinâmico.
- HTMX: disponível para futuras atualizações parciais.
- Chart.js: gráficos do dashboard.
- openpyxl: exportação Excel.
- ReportLab: exportação PDF.
