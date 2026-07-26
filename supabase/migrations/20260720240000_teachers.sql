-- Teachers, class assignments, and teaching-hour tracking (2026-07-20).
--
-- Model: a teacher is assigned to a recurring class slot (class_value, e.g.
-- "Tue 19:30 Beginner 2"). A class "happened" on a given date if attendance
-- rows exist for (class_value, class_date) — logging the presences is what
-- marks the session as taught, so hours are derived, never entered by hand.
--
-- Teacher logins do not exist yet (owner-only for now), but the schema and
-- the is_teacher() helper are in place so a teacher portal can be added
-- without a migration to the data model.

create table public.teachers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  email text not null unique
    check (char_length(email) <= 255 and position('@' in email) > 1),
  first_name text check (char_length(first_name) <= 80),
  last_name text check (char_length(last_name) <= 80),
  active boolean not null default true
);

create index teachers_email_idx on public.teachers (lower(email));

-- Recurring assignment. Several teachers may share one class (co-teaching),
-- and one teacher may hold several classes.
create table public.class_teachers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  class_value text not null,
  teacher_id uuid not null references public.teachers(id) on delete cascade,
  unique (class_value, teacher_id)
);

create index class_teachers_class_idx on public.class_teachers (class_value);

-- Audit trail: who logged a presence. Existing rows stay null; the teacher
-- portal will fill this from the JWT once teachers log in themselves.
alter table public.attendance
  add column marked_by_email text
    check (marked_by_email is null or char_length(marked_by_email) <= 255);

-- One row per reminder actually sent, so the daily job never emails twice
-- about the same unlogged session.
create table public.teaching_reminders (
  id uuid primary key default gen_random_uuid(),
  sent_at timestamptz not null default now(),
  class_value text not null,
  class_date date not null,
  teacher_id uuid not null references public.teachers(id) on delete cascade,
  unique (class_value, class_date, teacher_id)
);

create or replace function public.is_teacher()
returns boolean
language sql
stable
as $$
  select exists (
    select 1 from public.teachers
    where lower(email) = lower(coalesce(auth.jwt() ->> 'email', ''))
      and active
  )
$$;

alter table public.teachers enable row level security;
alter table public.class_teachers enable row level security;
alter table public.teaching_reminders enable row level security;

-- Owner manages everything; a teacher may read the roster and their own
-- assignments (harmless, and needed by a future teacher portal).
create policy "owner manages teachers"
  on public.teachers for all
  to authenticated
  using (public.is_owner())
  with check (public.is_owner());

create policy "teachers read teachers"
  on public.teachers for select
  to authenticated
  using (public.is_owner() or public.is_teacher());

create policy "owner manages class assignments"
  on public.class_teachers for all
  to authenticated
  using (public.is_owner())
  with check (public.is_owner());

create policy "teachers read class assignments"
  on public.class_teachers for select
  to authenticated
  using (public.is_owner() or public.is_teacher());

create policy "owner reads reminders"
  on public.teaching_reminders for select
  to authenticated
  using (public.is_owner());

-- Teaching hours, derived: a session counts once presences exist for it.
-- Every class on the schedule is a one-hour slot, hence count = hours.
create or replace function public.teaching_hours(from_date date default null, to_date date default null)
returns table (teacher_id uuid, email text, sessions bigint)
language sql
stable
security definer
set search_path = public
as $$
  select t.id, t.email, count(distinct (a.class_value, a.class_date))
  from public.teachers t
  join public.class_teachers ct on ct.teacher_id = t.id
  join public.attendance a on a.class_value = ct.class_value
  where (from_date is null or a.class_date >= from_date)
    and (to_date is null or a.class_date <= to_date)
  group by t.id, t.email
$$;

grant execute on function public.teaching_hours(date, date) to authenticated;
