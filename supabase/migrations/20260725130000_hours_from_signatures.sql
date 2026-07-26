-- Teaching hours come only from the teacher's own signature (2026-07-25).
--
-- The owner no longer assigns who taught a date: the teacher signs their own
-- hour in the presences page (sign_teaching). Hours therefore count exactly
-- the class_sessions rows a teacher signed — no more crediting "whoever
-- logged the presences" or the recurring assignment. The all-teacher report
-- is also gated to the owner; a teacher reads their own total through
-- my_teaching_hours() instead.

create or replace function public.teaching_hours(from_date date default null, to_date date default null)
returns table (teacher_id uuid, email text, first_name text, last_name text, sessions bigint)
language sql
stable
security definer
set search_path = public
as $$
  select t.id, t.email, t.first_name, t.last_name, count(cs.id)
  from public.teachers t
  join public.class_sessions cs on cs.teacher_id = t.id
  where public.is_owner()
    and (from_date is null or cs.class_date >= from_date)
    and (to_date is null or cs.class_date <= to_date)
  group by t.id, t.email, t.first_name, t.last_name
$$;

grant execute on function public.teaching_hours(date, date) to authenticated;
