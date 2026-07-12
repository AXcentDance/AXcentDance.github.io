-- Input hardening for anonymous registration inserts.
-- The anon INSERT policy is intentionally open (checkout must never break),
-- so this trigger is the gate that keeps garbage and injection payloads out:
--   * pass_type must be one of the real packages (blocks stored-HTML payloads
--     and forged "free pass" strings in one stroke)
--   * email must look like an email; hard length caps on every text field
--   * max 5 outstanding pending registrations per email (spam brake)
create or replace function public.enforce_registration_rules()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  pending_count integer;
begin
  if new.email is null or new.email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' or length(new.email) > 254 then
    raise exception 'Invalid email address';
  end if;

  if new.pass_type is not null and new.pass_type not in (
    '1 Course (8 Weeks)',
    '2 Classes/Week (8 Weeks)',
    '3 Classes/Week (8 Weeks)',
    '4 Classes/Week (8 Weeks)',
    '10-Class Flexible Package'
  ) then
    raise exception 'Unknown package';
  end if;

  if length(coalesce(new.first_name, '')) > 100
     or length(coalesce(new.last_name, '')) > 100
     or length(coalesce(new.phone, '')) > 40
     or length(coalesce(new.selected_classes, '')) > 600
     or length(coalesce(new.dates_unavailable, '')) > 400 then
    raise exception 'Field too long';
  end if;

  if new.status = 'pending_payment' then
    select count(*) into pending_count from public.registrations
      where lower(email) = lower(new.email) and status = 'pending_payment';
    if pending_count >= 5 then
      raise exception 'Too many pending registrations for this email';
    end if;
  end if;

  return new;
end;
$$;

create trigger registrations_enforce_rules
  before insert on public.registrations
  for each row execute function public.enforce_registration_rules();

-- Cap the absence note as well (portal input already caps at 200 client-side).
alter table public.absences
  add constraint absences_note_length check (length(coalesce(note, '')) <= 300);
