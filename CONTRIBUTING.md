# Como contribuir

Obrigado por considerar uma contribuição ao FinanSys.

## Ambiente local

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe main.py
```

## Antes de enviar uma alteração

1. Não inclua `data/`, bancos SQLite, backups, exportações ou informações financeiras reais.
2. Mantenha os cálculos monetários em `Decimal`.
3. Acrescente ou atualize testes para regras financeiras e novos fluxos.
4. Execute `compileall` e toda a suíte de testes.
5. Descreva claramente o comportamento alterado no pull request.

## Relatos de erros

Inclua passos para reproduzir, resultado esperado, resultado observado, versão do Python e navegador. Nunca anexe seu banco real; crie dados fictícios mínimos.
