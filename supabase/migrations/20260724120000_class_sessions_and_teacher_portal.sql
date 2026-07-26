-- Per-date teacher overrides + teacher portal access (2026-07-24).
--
-- class_teachers holds the RECURRING assignment. When somebody covers a
-- single date (the usual teacher is sick), that one occurrence gets a row
-- here instead of touching the recurring assignment.

create table public.class_sessions (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  class_value text not null,
  class_date date not null,
  teacher_id uuid references public.teachers(id) on delete set null,
  note text check (note is null or char_length(note) <= 200),
  unique (class_value, class_date)
);

create index class_sessions_lookup_idx on public.class_sessions (class_value, class_date);

alter table public.class_sessions enable row level security;

-- Both the owner and any active teacher may record who actually taught a
-- session; teachers need this to mark themselves when they cover for a
-- colleague.
create policy "staff read class sessions"
  on public.class_sessions for select
  to authenticated
  using (public.is_owner() or public.is_teacher());

create policy "staff write class sessions"
  on public.class_sessions for insert
  to authenticated
  with check (public.is_owner() or public.is_teacher());

create policy "staff update class sessions"
  on public.class_sessions for update
  to authenticated
  using (public.is_owner() or public.is_teacher())
  with check (public.is_owner() or public.is_teacher());

create policy "owner deletes class sessions"
  on public.class_sessions for delete
  to authenticated
  using (public.is_owner());

-- Teachers need the roster to mark presences, and their own attendance
-- history to see their hours. Note: this exposes student contact details
-- to staff accounts — acceptable for studio teachers, but it is a real
-- widening of who can read the registrations table.
create policy "teachers read registrations"
  on public.registrations for select
  to authenticated
  using (public.is_teacher());

create policy "teachers read attendance"
  on public.attendance for select
  to authenticated
  using (public.is_teacher());

create policy "teachers write attendance"
  on public.attendance for insert
  to authenticated
  with check (public.is_teacher());

create policy "teachers update attendance"
  on public.attendance for update
  to authenticated
  using (public.is_teacher())
  with check (public.is_teacher());

create policy "teachers delete attendance"
  on public.attendance for delete
  to authenticated
  using (public.is_teacher());

-- Hours, now three-tier. Priority, highest first:
--   1. class_sessions.teacher_id  — an explicit "X taught this date"
--   2. attendance.marked_by_email — whoever logged the presences
--   3. class_teachers             — the recurring assignment
-- Tiers 1 and 2 are immutable history; only the tier-3 fallback moves if a
-- class is later reassigned.
drop function if exists public.teaching_hours(date, date);

create or replace function public.teaching_hours(from_date date default null, to_date date default null)
returns table (teacher_id uuid, email text, first_name text, last_name text, sessions bigint)
language sql
stable
security definer
set search_path = public
as $$
  with sessions as (
    select
      a.class_value,
      a.class_date,
      (
        select cs.teacher_id from public.class_sessions cs
        where cs.class_value = a.class_value and cs.class_date = a.class_date
      ) as override_teacher,
      (
        select t.id from public.attendance a2
        join public.teachers t on lower(t.email) = lower(a2.marked_by_email)
        where a2.class_value = a.class_value and a2.class_date = a.class_date
        limit 1
      ) as logged_by
    from public.attendance a
    where (from_date is null or a.class_date >= from_date)
      and (to_date is null or a.class_date <= to_date)
    group by a.class_value, a.class_date
  ),
  credited as (
    select s.class_value, s.class_date, s.override_teacher as teacher_id
    from sessions s where s.override_teacher is not null
    union
    select s.class_value, s.class_date, s.logged_by
    from sessions s where s.override_teacher is null and s.logged_by is not null
    union
    select s.class_value, s.class_date, ct.teacher_id
    from sessions s
    join public.class_teachers ct on ct.class_value = s.class_value
    where s.override_teacher is null and s.logged_by is null
  )
  select t.id, t.email, t.first_name, t.last_name, count(*)
  from public.teachers t
  join credited c on c.teacher_id = t.id
  group by t.id, t.email, t.first_name, t.last_name
$$;

grant execute on function public.teaching_hours(date, date) to authenticated;
