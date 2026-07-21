-- Sick-day extension is AUTOMATIC again (owner decision 2026-07-20,
-- reverting 20260719170000): a declared sick day immediately pushes
-- pass_end_date to the next weekday on which the student has an enrolled
-- class — their own classes, not any class, so a Sunday end with Tue+Wed
-- classes extends to Tuesday. Flexible-package passes (no fixed weekly
-- classes) are left unchanged for manual handling.
-- Side effect by design: extending the pass fires registrations_reset_reminder,
-- so a fresh renewal reminder goes out in the new final week.

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
