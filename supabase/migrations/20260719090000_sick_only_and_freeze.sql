-- Absence policy change (owner-confirmed 2026-07-19):
--   * Students can no longer declare planned absences from the portal.
--     Longer breaks are handled as a PASS FREEZE request (email to the
--     studio, staff adjust pass_end_date manually). The 'excused' type
--     stays in the schema for staff-entered corrections only.
--   * Sick days are same-day-only and must be declared before 12:00
--     Europe/Zurich. Quota stays at 1 per pass.
--   * A sick day automatically extends the pass to the next date on which
--     the student has an enrolled class (one more day with an active pass).

create or replace function public.enforce_absence_rules()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  reg public.registrations%rowtype;
  used_count integer;
  zurich_now timestamp;
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
    -- Staff-only (dashboard / service role has no JWT). Students request a
    -- pass freeze by email instead.
    if auth.jwt() is not null then
      raise exception 'Planned absences are handled as pass freeze requests — please use the freeze form';
    end if;
  else -- sick
    zurich_now := now() at time zone 'Europe/Zurich';
    if new.absence_date <> zurich_now::date then
      raise exception 'Sick days can only be declared for today';
    end if;
    -- The midday cutoff applies to students; staff corrections are exempt.
    if auth.jwt() is not null and zurich_now::time >= time '12:00' then
      raise exception 'Sick days must be declared before 12:00 on the day itself';
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

-- A sick day gives the student one more day with an active pass: push
-- pass_end_date forward to the next weekday on which they have a class.
-- Flexible-package passes (no fixed weekly classes) are left unchanged.
create or replace function public.extend_pass_after_sick()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  reg public.registrations%rowtype;
  class_days text[];
  candidate date;
  i integer;
begin
  if new.type <> 'sick' then
    return new;
  end if;

  select * into reg from public.registrations where id = new.registration_id;

  if reg.pass_end_date is null or reg.selected_classes is null or reg.selected_classes = '' then
    return new;
  end if;

  select array_agg(distinct m[1]) into class_days
    from regexp_matches(reg.selected_classes, '(Mon|Tue|Wed|Thu|Fri|Sat|Sun) \d', 'g') m;

  if class_days is null then
    return new;
  end if;

  for i in 1..7 loop
    candidate := reg.pass_end_date + i;
    if trim(to_char(candidate, 'Dy')) = any(class_days) then
      update public.registrations set pass_end_date = candidate where id = reg.id;
      exit;
    end if;
  end loop;

  return new;
end;
$$;

drop trigger if exists absences_extend_pass on public.absences;
create trigger absences_extend_pass
  after insert on public.absences
  for each row execute function public.extend_pass_after_sick();
