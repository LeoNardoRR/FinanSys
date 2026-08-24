create table public.categories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(trim(name)) between 1 and 80),
  kind text not null check (kind in ('income', 'expense')),
  color text not null default '#2563eb' check (color ~ '^#[0-9A-Fa-f]{6}$'),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (user_id, name),
  unique (user_id, id)
);

create table public.cards (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(trim(name)) between 1 and 80),
  brand text check (brand is null or char_length(brand) <= 40),
  credit_limit numeric(12,2) not null default 0 check (credit_limit >= 0),
  closing_day smallint check (closing_day between 1 and 31),
  due_day smallint check (due_day between 1 and 31),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (user_id, name),
  unique (user_id, id)
);

create table public.goals (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(trim(name)) between 1 and 100),
  target_amount numeric(12,2) not null check (target_amount > 0),
  current_amount numeric(12,2) not null default 0 check (current_amount >= 0),
  monthly_contribution numeric(12,2) not null default 0 check (monthly_contribution >= 0),
  target_date date,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (user_id, name)
);

create table public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null check (char_length(trim(name)) between 1 and 100),
  amount numeric(12,2) not null check (amount > 0),
  billing_day smallint not null check (billing_day between 1 and 31),
  card_id uuid,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (user_id, name),
  foreign key (user_id, card_id) references public.cards(user_id, id) on delete restrict
);

create table public.transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  occurred_on date not null default current_date,
  description text not null check (char_length(trim(description)) between 1 and 160),
  amount numeric(12,2) not null check (amount > 0),
  kind text not null check (kind in ('income', 'expense')),
  category_id uuid,
  card_id uuid,
  notes text check (notes is null or char_length(notes) <= 2000),
  installment_group uuid,
  installment_number smallint check (installment_number is null or installment_number between 1 and 120),
  installments_total smallint check (installments_total is null or installments_total between 1 and 120),
  created_at timestamptz not null default now(),
  foreign key (user_id, category_id) references public.categories(user_id, id) on delete restrict,
  foreign key (user_id, card_id) references public.cards(user_id, id) on delete restrict,
  check (
    (installment_group is null and installment_number is null and installments_total is null)
    or (installment_group is not null and installment_number is not null and installments_total is not null and installment_number <= installments_total)
  )
);

create index transactions_user_date_idx on public.transactions (user_id, occurred_on desc, created_at desc);
create index transactions_user_kind_idx on public.transactions (user_id, kind, occurred_on desc);
create index subscriptions_user_active_idx on public.subscriptions (user_id, active, billing_day);
create index goals_user_active_idx on public.goals (user_id, active);

alter table public.categories enable row level security;
alter table public.cards enable row level security;
alter table public.goals enable row level security;
alter table public.subscriptions enable row level security;
alter table public.transactions enable row level security;

create policy categories_select_own on public.categories for select to authenticated using ((select auth.uid()) = user_id);
create policy categories_insert_own on public.categories for insert to authenticated with check ((select auth.uid()) = user_id);
create policy categories_update_own on public.categories for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy categories_delete_own on public.categories for delete to authenticated using ((select auth.uid()) = user_id);

create policy cards_select_own on public.cards for select to authenticated using ((select auth.uid()) = user_id);
create policy cards_insert_own on public.cards for insert to authenticated with check ((select auth.uid()) = user_id);
create policy cards_update_own on public.cards for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy cards_delete_own on public.cards for delete to authenticated using ((select auth.uid()) = user_id);

create policy goals_select_own on public.goals for select to authenticated using ((select auth.uid()) = user_id);
create policy goals_insert_own on public.goals for insert to authenticated with check ((select auth.uid()) = user_id);
create policy goals_update_own on public.goals for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy goals_delete_own on public.goals for delete to authenticated using ((select auth.uid()) = user_id);

create policy subscriptions_select_own on public.subscriptions for select to authenticated using ((select auth.uid()) = user_id);
create policy subscriptions_insert_own on public.subscriptions for insert to authenticated with check ((select auth.uid()) = user_id);
create policy subscriptions_update_own on public.subscriptions for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy subscriptions_delete_own on public.subscriptions for delete to authenticated using ((select auth.uid()) = user_id);

create policy transactions_select_own on public.transactions for select to authenticated using ((select auth.uid()) = user_id);
create policy transactions_insert_own on public.transactions for insert to authenticated with check ((select auth.uid()) = user_id);
create policy transactions_update_own on public.transactions for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy transactions_delete_own on public.transactions for delete to authenticated using ((select auth.uid()) = user_id);

revoke all on public.categories, public.cards, public.goals, public.subscriptions, public.transactions from anon;
grant usage on schema public to authenticated;
grant select, insert, update, delete on public.categories, public.cards, public.goals, public.subscriptions, public.transactions to authenticated;
