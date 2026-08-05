# Segurança

## Dados locais

O FinanSys armazena dados financeiros em `data/finansys.db`. Esse arquivo, backups e exportações são ignorados pelo Git e nunca devem ser enviados para issues ou repositórios públicos.

## Como relatar uma vulnerabilidade

Não publique detalhes exploráveis em uma issue pública. Use o recurso **Security > Report a vulnerability** do repositório, quando disponível, ou contate o mantenedor de forma privada.

Inclua apenas dados fictícios, uma descrição do impacto e passos mínimos para reprodução.

## Escopo

O FinanSys é uma aplicação local de finanças pessoais, sem autenticação e destinada ao uso em `127.0.0.1`. Não a exponha diretamente à internet sem adicionar autenticação, HTTPS, proteção CSRF e uma revisão de segurança específica para hospedagem multiusuário.
