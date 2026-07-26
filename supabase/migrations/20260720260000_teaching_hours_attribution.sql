-- Sharpen teaching-hour attribution (2026-07-20).
--
-- A session is one (class_value, class_date) that has attendance rows; every
-- class on the schedule is a one-hour slot, so sessions == hours.
--
-- Credit goes to whoever actually logged the presences when that is known
-- (attendance.marked_by_email, which the teacher portal will fill once
-- teachers log in), and otherwise falls back to the teacher currently
-- assigned to the class. Known limitation of the fallback: it follows the
-- CURRENT assignment, so re-assigning a class also moves its unattributed
-- historical hours. Rows logged by a teacher are immune to that.

-- Return columns change (names added), so the old signature must go first.
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
      -- the teacher who logged it, if any of the rows names one
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
    -- explicit: the teacher who logged the presences
    select s.class_value, s.class_date, s.logged_by as teacher_id
    from sessions s
    where s.logged_by is not null
    union
    -- fallback: nobody named, so the assigned teacher(s) get the credit
    select s.class_value, s.class_date, ct.teacher_id
    from sessions s
    join public.class_teachers ct on ct.class_value = s.class_value
    where s.logged_by is null
  )
  select t.id, t.email, t.first_name, t.last_name, count(*)
  from public.teachers t
  join credited c on c.teacher_id = t.id
  group by t.id, t.email, t.first_name, t.last_name
$$;

grant execute on function public.teaching_hours(date, date) to authenticated;
