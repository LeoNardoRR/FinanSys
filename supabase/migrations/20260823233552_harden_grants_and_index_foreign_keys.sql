revoke all privileges on public.categories, public.cards, public.goals, public.subscriptions, public.transactions from authenticated;
grant select, insert, update, delete on public.categories, public.cards, public.goals, public.subscriptions, public.transactions to authenticated;

create index subscriptions_user_card_idx on public.subscriptions (user_id, card_id);
create index transactions_user_category_idx on public.transactions (user_id, category_id);
create index transactions_user_card_idx on public.transactions (user_id, card_id);
