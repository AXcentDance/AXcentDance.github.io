-- Teachers: self-signed hours + minimum-necessary student data (2026-07-25).
--
-- Previously a teacher could read every registration (emails, phones, pass
-- prices) and the owner assigned who taught. Now:
--   * a teacher only ever sees FIRST + LAST NAME, only for students enrolled
--     in a class they are assigned to;
--   * a teacher signs their own teaching hour — the owner does not assign it;
--   * attendance is written through a function, so the student's email is
--     filled server-side and never exposed to the teacher.
-- The broad "teachers read registrations" policy is dropped accordingly.

drop policy if exists "teachers read registrations" on public.registrations;
drop policy if exists "teachers read attendance" on public.attendance;
drop policy if exists "teachers write attendance" on public.attendance;
drop policy if exists "teachers update attendance" on public.attendance;
drop policy if exists "teachers delete attendance" on public.attendance;
drop policy if exists "staff write class sessions" on public.class_sessions;
drop policy if exists "staff update class sessions" on public.class_sessions;

-- Is the caller the teacher assigned to this class?
create or replace function public.is_class_teacher(cv text)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.class_teachers ct
    join public.teachers t on t.id = ct.teacher_id
    where ct.class_value = cv
      and t.active
      and lower(t.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
  )
$$;

grant execute on function public.is_class_teacher(text) to authenticated;

-- The roster a teacher is allowed to see: names only, no contact details,
-- no pass information — and only for their own class.
create or replace function public.class_roster(cv text, cd date)
returns table (
  registration_id uuid,
  first_name text,
  last_name text,
  role text,
  status text
)
language sql
stable
security definer
set search_path = public
as $$
  select
    r.id,
    r.first_name,
    r.last_name,
    (regexp_match(r.selected_classes, cv || ' \((Leader|Follower)\)'))[1],
    a.status
  from public.registrations r
  left join public.attendance a
    on a.registration_id = r.id and a.class_value = cv and a.class_date = cd
  where (public.is_owner() or public.is_class_teacher(cv))
    and r.status in ('active', 'expired')
    and (r.pass_start_date is null or r.pass_start_date <= cd)
    and (r.pass_end_date is null or r.pass_end_date >= cd)
    and position(cv in coalesce(r.selected_classes, '')) > 0
  order by r.first_name, r.last_name
$$;

grant execute on function public.class_roster(text, date) to authenticated;

-- Mark a presence. The email is looked up here so the caller never needs it.
-- status null removes the mark.
create or replace function public.mark_attendance(cv text, cd date, reg uuid, st text)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  student_email text;
begin
  if not (public.is_owner() or public.is_class_teacher(cv)) then
    raise exception 'Not allowed to mark attendance for this class';
  end if;
  if st is not null and st not in ('present', 'absent') then
    raise exception 'Invalid status';
  end if;

  if st is null then
    delete from public.attendance
    where class_value = cv and class_date = cd and registration_id = reg;
    return;
  end if;

  select email into student_email from public.registrations where id = reg;
  if student_email is null then
    raise exception 'Unknown registration';
  end if;

  insert into public.attendance
    (class_value, class_date, registration_id, email, status, marked_by_email)
  values (cv, cd, reg, student_email, st, auth.jwt() ->> 'email')
  on conflict (class_date, class_value, registration_id) do update
    set status = excluded.status,
        marked_by_email = excluded.marked_by_email;
end;
$$;

grant execute on function public.mark_attendance(text, date, uuid, text) to authenticated;

-- A teacher signs (or unsigns) their own teaching hour for one class date.
-- Always records the CALLER, so nobody can sign hours for someone else.
create or replace function public.sign_teaching(cv text, cd date, taught boolean)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  me uuid;
begin
  select id into me from public.teachers
  where lower(email) = lower(coalesce(auth.jwt() ->> 'email', '')) and active;

  if me is null then
    raise exception 'Only an active teacher can sign a teaching hour';
  end if;
  if not public.is_class_teacher(cv) then
    raise exception 'You are not assigned to this class';
  end if;

  if taught then
    insert into public.class_sessions (class_value, class_date, teacher_id)
    values (cv, cd, me)
    on conflict (class_value, class_date) do update set teacher_id = me;
  else
    -- withdraw only my own signature
    delete from public.class_sessions
    where class_value = cv and class_date = cd and teacher_id = me;
  end if;
end;
$$;

grant execute on function public.sign_teaching(text, date, boolean) to authenticated;

-- A teacher's own hours, so the portal never needs the all-teacher table.
create or replace function public.my_teaching_hours()
returns bigint
language sql
stable
security definer
set search_path = public
as $$
  select coalesce((
    select count(*) from public.class_sessions cs
    join public.teachers t on t.id = cs.teacher_id
    where lower(t.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
  ), 0)
$$;

grant execute on function public.my_teaching_hours() to authenticated;
