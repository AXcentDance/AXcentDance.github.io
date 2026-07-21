-- Pass freezes are for multi-week breaks (owner policy 2026-07-20):
-- hard minimum of 14 days between freeze start and return date.
-- Shorter absences are covered by the sick day or handled by email.

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

  if new.type = 'freeze' then
    if new.date_from is null or new.date_until is null
       or new.date_until - new.date_from < 14 then
      raise exception 'A pass freeze must cover at least two weeks';
    end if;
  end if;

  if new.time_from is not null and new.time_until is not null
     and new.time_until <= new.time_from then
    raise exception 'The end time must be after the start time';
  end if;

  select count(*) into open_count from public.requests
    where lower(email) = lower(new.email)
      and status in ('new', 'pending_payment');
  if open_count >= 10 then
    raise exception 'Too many open requests for this email — please wait for a reply';
  end if;

  return new;
end;
$$;
