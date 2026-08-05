# Manual de uso

## Dashboard

O Dashboard usa o mês atual. O seletor no topo alterna entre a família inteira e cada perfil ativo.

- **Receitas**: soma dos lançamentos do tipo Receita no mês.
- **Despesas**: soma das despesas no mês.
- **Saldo**: receitas menos despesas.
- **Meta mensal de aportes**: soma dos aportes mensais configurados nas metas ativas.
- **Gastos por categoria**: até oito categorias com maior gasto.
- **Métricas por pessoa**: receitas, despesas e saldo individual.
- **Alertas**: cartão acima de 85% do limite no ciclo e assinaturas cobradas hoje/amanhã.

## Lançamentos

Abra **Novo lançamento**, preencha descrição, valor total e data. Categoria, conta, pagamento, cartão e pessoa são opcionais, mas preenchê-los melhora as métricas.

### Parcelas

Informe o valor total e o número de parcelas. O sistema cria uma linha por mês. Exemplo: R$ 100 em 3 vezes vira R$ 33,33, R$ 33,33 e R$ 33,34. A diferença de centavos fica na última parcela, portanto a soma permanece exata.

Editar uma parcela altera somente aquela linha. Excluir também remove somente a parcela escolhida.


## Compras parceladas

Use este módulo para produtos de maior valor, como geladeira, móveis, computador ou eletrodomésticos.

1. Abra **Compras parceladas**.
2. Clique em **Nova compra**.
3. Informe produto, valor total, parcelas, cartão e data.
4. Opcionalmente informe loja, responsável, categoria, garantia e observações.
5. Confira a prévia e salve.

O sistema cria a compra e todos os lançamentos mensais. O primeiro e o último vencimento usam os dias de fechamento e vencimento do cartão. Diferenças de centavos ficam na última parcela.

A tela mostra total comprado, saldo das parcelas futuras, próxima fatura, término, garantia e cronograma completo. “Vencimento passado” significa apenas que a data já passou; não é uma conciliação com o banco.

Para preservar o cronograma, parcelas vinculadas devem ser gerenciadas pela página da compra. **Excluir compra completa** remove a compra e todas as parcelas relacionadas.

Em Planejamento, o botão **Parcelar no cartão** carrega uma compra prevista neste formulário e a marca como convertida depois de salvar.

## Cartões e faturas

Cadastre o cartão em Configurações com limite, dia de fechamento e vencimento. Uma compra no crédito precisa estar associada ao cartão para aparecer na fatura.

O ciclo começa no dia seguinte ao fechamento anterior e termina no fechamento atual. Exemplo: fechamento dia 10, referência 3 de agosto: ciclo de 11 de julho a 10 de agosto. Compras após 10 de agosto entram no ciclo seguinte.

## Metas

Para cada meta informe:

- valor objetivo;
- quanto já foi guardado;
- aporte mensal pretendido;
- data desejada, se houver.

O sistema calcula o percentual, quanto falta, quantos meses serão necessários com o aporte atual, saldo após 12 meses e aporte mínimo para cumprir o prazo. Atualize o valor guardado quando fizer novos aportes.

## Assinaturas

Cadastre o serviço, valor, dia, pagamento, cartão e pessoa. No início do mês use **Gerar lançamentos**. O comando é seguro para repetir: uma assinatura já gerada na mesma data/cartão não é duplicada.

## Planejamento

### Perfis

Cadastre cada integrante. Perfis ativos aparecem nos formulários e filtros.

### Fontes de renda

Cadastre salário, freelance, aluguel ou outra renda mensal prevista e associe a uma pessoa. Esse valor é planejamento; ele não vira receita realizada automaticamente.

### Gastos previstos

Cadastre compras que pretende fazer. Quando acontecerem, clique **Virou compra**. O sistema cria a despesa real e marca a previsão como convertida.

A seção de parcelas futuras lê os lançamentos já existentes nos próximos quatro meses, incluindo parcelas automáticas.

## Fluxo de caixa

Filtre por pessoa e horizonte. A linha do tempo mostra cada entrada/saída e o saldo acumulado. Assinaturas ativas aparecem como compromissos recorrentes.

## Backup, restauração e exportações

Em Configurações:

- **Criar backup** gera um ZIP em `data/backups/` e oferece download.
- **Restaurar ZIP** substitui o banco atual e salva automaticamente uma cópia anterior em `data/backups/`.
- **CSV** é ideal para importação simples.
- **Excel** gera `.xlsx` formatado.
- **PDF** gera resumo financeiro e lançamentos recentes.

Faça backup antes de editar código, atualizar dependências ou mover o sistema.
