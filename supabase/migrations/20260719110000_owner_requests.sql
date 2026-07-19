-- Owner master account + customer request inbox (2026-07-19).
-- The owner logs in with the normal Supabase auth flow using the studio
-- address; is_owner() gates the admin RLS paths server-side, so the admin
-- page is real security, not a hidden URL.

create or replace function public.is_owner()
returns boolean
language sql
stable
as $$
  select lower(coalesce(auth.jwt() ->> 'email', '')) = 'info@axcentdance.com'
$$;

-- One table for every portal request that staff handle by hand:
--   freeze         pass freeze for a longer break (from/until)
--   room_booking   studio hall rental enquiry
--   private_class  1-on-1 lesson enquiry
create table public.requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  email text not null check (char_length(email) <= 255 and position('@' in email) > 1),
  name text check (char_length(name) <= 120),
  type text not null check (type in ('freeze', 'room_booking', 'private_class')),
  date_from date,
  date_until date,
  details text check (char_length(details) <= 1000),
  status text not null default 'new' check (status in ('new', 'confirmed', 'declined', 'done')),
  handled_at timestamptz
);

create index requests_status_idx on public.requests (status, created_at desc);
create index requests_email_idx on public.requests (lower(email));

alter table public.requests enable row level security;

create policy "customers create own requests"
  on public.requests for insert
  to authenticated
  with check (lower(email) = lower(auth.jwt() ->> 'email') and status = 'new');

create policy "customers read own, owner reads all"
  on public.requests for select
  to authenticated
  using (lower(email) = lower(auth.jwt() ->> 'email') or public.is_owner());

create policy "owner updates requests"
  on public.requests for update
  to authenticated
  using (public.is_owner())
  with check (public.is_owner());

-- No delete policy: the inbox keeps its history.

create or replace function public.enforce_request_limits()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  open_count integer;
begin
  if new.date_from is not null and new.date_until is not null
     and new.date_until < new.date_from then
    raise exception 'The end date cannot be before the start date';
  end if;

  select count(*) into open_count from public.requests
    where lower(email) = lower(new.email) and status = 'new';
  if open_count >= 10 then
    raise exception 'Too many open requests for this email — please wait for a reply';
  end if;

  return new;
end;
$$;

create trigger requests_enforce_limits
  before insert on public.requests
  for each row execute function public.enforce_request_limits();
