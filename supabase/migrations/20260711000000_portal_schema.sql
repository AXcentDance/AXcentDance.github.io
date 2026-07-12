-- Student portal schema: registrations (passes) + absences (excused/sick days)
-- Access model: customers are matched to their rows by the email in their
-- Supabase Auth JWT. No user_id linkage is required, so signup can happen
-- before or after purchase.

create table public.registrations (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  email text not null,
  first_name text,
  last_name text,
  phone text,
  pass_type text,
  is_student boolean default false,
  pass_start_date date,
  pass_end_date date,
  selected_classes text,
  dates_unavailable text,
  status text not null default 'pending_payment'
    check (status in ('pending_payment', 'active', 'expired', 'cancelled')),
  stripe_session_id text
);

create index registrations_email_idx on public.registrations (lower(email));

alter table public.registrations enable row level security;

-- Customers can read only their own rows (email from the verified JWT).
create policy "customers read own registrations"
  on public.registrations for select
  to authenticated
  using (lower(email) = lower(auth.jwt() ->> 'email'));

-- The registration form (anonymous visitor) may create pending rows only.
-- Only the stripe-webhook (service role, bypasses RLS) can activate them,
-- so a forged insert can never become a valid pass.
create policy "public can create a pending registration"
  on public.registrations for insert
  to anon, authenticated
  with check (status = 'pending_payment');

-- No update/delete policies for clients.


create table public.absences (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  registration_id uuid not null references public.registrations(id) on delete cascade,
  email text not null,
  type text not null check (type in ('excused', 'sick')),
  absence_date date not null,
  note text
);

create index absences_registration_idx on public.absences (registration_id);

alter table public.absences enable row level security;

create policy "customers read own absences"
  on public.absences for select
  to authenticated
  using (lower(email) = lower(auth.jwt() ->> 'email'));

create policy "customers declare own absences"
  on public.absences for insert
  to authenticated
  with check (lower(email) = lower(auth.jwt() ->> 'email'));

-- No update/delete policies: declarations are final from the customer side;
-- staff can correct rows via the Supabase dashboard (service role).


-- Business rules (confirmed 2026-07-11):
--   * quota per registration: max 2 excused days and max 1 sick day (independent)
--   * excused days must be declared for a future date
--   * sick days may be declared for today or a future date (not retroactively)
--   * absences can only be declared against the customer's own ACTIVE registration
--   * excused days do not apply to the 10-Class Flexible Package
-- Enforced in a trigger because RLS policies cannot count sibling rows.
create or replace function public.enforce_absence_rules()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  reg public.registrations%rowtype;
  used_count integer;
begin
  select * into reg from public.registrations where id = new.registration_id;

  if reg.id is null then
    raise exception 'Registration not found';
  end if;

  if lower(reg.email) <> lower(new.email) then
    raise exception 'Absence email does not match the registration';
  end if;

  if reg.status <> 'active' then
    raise exception 'Absences can only be declared on an active pass';
  end if;

  if new.type = 'excused' then
    if reg.pass_type = '10-Class Flexible Package' then
      raise exception 'Excused days do not apply to the 10-Class Flexible Package';
    end if;
    if new.absence_date <= current_date then
      raise exception 'Excused days must be declared in advance';
    end if;
    select count(*) into used_count from public.absences
      where registration_id = new.registration_id and type = 'excused';
    if used_count >= 2 then
      raise exception 'All 2 excused days have already been used for this pass';
    end if;
  else -- sick
    if new.absence_date < current_date then
      raise exception 'Sick days cannot be declared for a past date';
    end if;
    select count(*) into used_count from public.absences
      where registration_id = new.registration_id and type = 'sick';
    if used_count >= 1 then
      raise exception 'The sick day has already been used for this pass';
    end if;
  end if;

  return new;
end;
$$;

create trigger absences_enforce_rules
  before insert on public.absences
  for each row execute function public.enforce_absence_rules();
