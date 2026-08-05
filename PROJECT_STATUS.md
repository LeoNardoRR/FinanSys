# Estado do projeto — 04/08/2026

Cópia executável canônica: `outputs/FinanSys`.

## Concluído

- Consolidação de modelos, rotas, templates, CSS e JavaScript.
- Interface nova responsiva, temas claro/escuro e remoção de caracteres corrompidos.
- Lançamentos, edição, exclusão, filtros e parcelas.
- Dashboard familiar/individual e alertas.
- Cartões por ciclo real de fechamento.
- Metas e projeções.
- Assinaturas idempotentes.
- Perfis, rendas, compras previstas e conversão.
- Fluxo de caixa.
- CSV, Excel, PDF, backup e restauração.
- Limpeza das pastas duplicadas internas após checkpoint.
- 12 testes automatizados aprovados.
- Revisão visual desktop claro/escuro e móvel, sem erro de console.

## Próximas evoluções opcionais

- Empacotar bibliotecas web localmente para gráficos 100% offline.
- Adicionar edição de cadastros (hoje é possível ativar/desativar).
- Importar extratos OFX/CSV.
- Adicionar orçamento mensal por categoria.

Último comando de validação:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
```

## Revisão visual e ajuda — 03/08/2026

- Ícones do menu substituídos por SVGs locais, maiores e com estados ativo/hover de alto contraste.
- Nova página `Como usar` com 11 seções, índice, pesquisa instantânea e instruções de todos os módulos.
- Validação visual em tema escuro e viewport móvel, sem overflow, caracteres corrompidos ou ícones quebrados.
- Nove testes automatizados continuam aprovados.

## Backup rotativo automático — 03/08/2026

- Dois backups automáticos na Área de Trabalho, atualizados na abertura e no encerramento normal.
- Snapshot consistente do SQLite e verificação de integridade antes da rotação.
- Estado e caminho exibidos em Configurações; funcionamento documentado em Como usar.
- Onze testes automatizados aprovados, incluindo rotação, conteúdo e ausência de banco.

## Compras parceladas de produtos — 04/08/2026

- Nova entidade Purchase vinculada aos lançamentos mensais.
- Cadastro rápido de produto, total, parcelas, cartão, loja, pessoa, garantia e observações.
- Primeiro/último vencimento calculados pelo fechamento real do cartão.
- Acompanhamento de saldo futuro, próxima parcela, término e cronograma.
- Conversão de gasto previsto e proteção contra exclusão de parcela isolada.
- Doze testes automatizados aprovados, incluindo o cenário Geladeira em 5x.
