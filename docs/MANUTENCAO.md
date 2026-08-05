# Manutenção, testes e solução de problemas

## Atualização segura

1. Pare o servidor com `Ctrl+C`.
2. Copie `data/finansys.db` ou crie backup pela interface.
3. Atualize o código.
4. Ative `.venv` e execute `pip install -r requirements.txt`.
5. Execute os testes.
6. Inicie `python main.py`.

## Comandos úteis

```powershell
# Instalar/atualizar dependências
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# Verificar sintaxe
.\.venv\Scripts\python.exe -m compileall -q app main.py

# Executar testes
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider

# Iniciar
.\.venv\Scripts\python.exe main.py
```

## O que os testes cobrem

- saúde do servidor e carregamento de todas as páginas;
- ausência de caractere de substituição (`�`);
- geração válida de CSV, XLSX e PDF;
- conversão de valores brasileiros e datas de fim do mês;
- ciclos de cartão antes/depois do fechamento;
- projeções de metas;
- dashboard familiar e individual;
- alerta de utilização do cartão;
- fluxo completo com pessoa, parcelamento, edição, meta e assinatura sem duplicação;
- compra de produto em parcelas, fechamento real, centavos exatos, conversão de planejamento e exclusão íntegra do conjunto.

Os testes de fluxo usam SQLite em memória e não alteram `data/finansys.db`.

## Problemas comuns

### A página mostra versão antiga

Pare todos os terminais com o FinanSys, inicie novamente dentro de `outputs\FinanSys` e force atualização no navegador com `Ctrl+F5`.

### Porta 8000 ocupada

Feche outra instância. Para usar outra porta temporariamente:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

### Módulo não encontrado

Confirme que está na pasta correta e reinstale:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Banco bloqueado

Feche todas as instâncias do FinanSys. Não abra `finansys.db` em outro editor enquanto grava dados.

### Restaurou backup e não mudou

Recarregue a página. Se necessário, reinicie o servidor para descartar conexões antigas.

### Gráficos não aparecem sem internet

Os dados, cadastros e cálculos continuam funcionando; Chart.js e HTMX são carregados por CDN. Para operação totalmente sem internet, baixe versões compatíveis para `app/static/vendor/` e troque os `<script src>` em `base.html` e `dashboard.html` por URLs locais.

## Checkpoints e recuperação

- `data/backups/pre_consolidacao_*.zip`: banco antes da consolidação.
- `checkpoints/codigo_pre_limpeza_*.zip`: código antes da remoção das pastas duplicadas.
- `data/backups/antes_restauracao_*.db`: cópia automática antes de restaurar um ZIP.

## Checklist antes de publicar uma alteração

- [ ] Banco copiado/backup criado.
- [ ] `compileall` sem erro.
- [ ] todos os testes verdes.
- [ ] dashboard claro e escuro revisados.
- [ ] formulários testados em largura desktop e móvel.
- [ ] exportações abrem corretamente.
- [ ] nenhuma senha, dado pessoal ou banco foi incluído em compartilhamento de código.

## Backup automático na Área de Trabalho

A rotina está em `app/services/automatic_backup.py` e é chamada no ciclo de vida de `main.py`.

- Pasta padrão: `%USERPROFILE%\Desktop\Backups FinanSys` ou o caminho de Área de Trabalho configurado no Registro do Windows.
- `FinanSys_backup_1.zip`: cópia mais recente.
- `FinanSys_backup_2.zip`: cópia anterior.
- Cada ZIP contém `finansys.db` e `backup_info.json`.
- Antes de publicar o arquivo, a rotina usa o backup nativo do SQLite e executa `PRAGMA quick_check`.
- A variável de ambiente `FINANSYS_BACKUP_DIR` pode redirecionar a raiz em testes ou instalações especiais.
