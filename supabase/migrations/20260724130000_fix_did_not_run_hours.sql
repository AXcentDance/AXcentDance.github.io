-- Fix: "class did not run" must credit nobody (2026-07-24).
--
-- A class_sessions row with teacher_id = NULL means the class explicitly did
-- not happen. The previous version read that as "no override", so the hour
-- still fell through to whoever logged the presences, or to the assigned
-- teacher. Distinguish the two by testing for the ROW's existence, not for a
-- non-null teacher_id.

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
      exists (
        select 1 from public.class_sessions cs
        where cs.class_value = a.class_value and cs.class_date = a.class_date
      ) as has_override,
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
    -- 1. explicit override naming a teacher
    select s.class_value, s.class_date, s.override_teacher as teacher_id
    from sessions s
    where s.has_override and s.override_teacher is not null
    union
    -- 2. no override row at all: whoever logged the presences
    select s.class_value, s.class_date, s.logged_by
    from sessions s
    where not s.has_override and s.logged_by is not null
    union
    -- 3. no override row and no logger: the recurring assignment
    select s.class_value, s.class_date, ct.teacher_id
    from sessions s
    join public.class_teachers ct on ct.class_value = s.class_value
    where not s.has_override and s.logged_by is null
    -- a row with teacher_id NULL ("did not run") matches none of the above
  )
  select t.id, t.email, t.first_name, t.last_name, count(*)
  from public.teachers t
  join credited c on c.teacher_id = t.id
  group by t.id, t.email, t.first_name, t.last_name
$$;

grant execute on function public.teaching_hours(date, date) to authenticated;
