-- Purchase-gated signup (owner-requested 2026-07-20): an account can only
-- be created for an email that already has a real registration. Forged
-- pending_payment rows (the public form can insert those anonymously) do
-- NOT qualify — only statuses the webhook or staff can set.
--
-- The signup pages pre-check with the existing email_has_profile() RPC for
-- a friendly message; this trigger is the hard enforcement underneath.
-- Note: this also applies to users created via the admin API — the studio
-- owner address is exempt, other staff accounts would need a registration
-- row or a temporary exemption here.

create or replace function public.enforce_signup_requires_pass()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if lower(new.email) = 'info@axcentdance.com' then
    return new;
  end if;

  if not exists (
    select 1 from public.registrations
    where lower(email) = lower(new.email)
      and status <> 'pending_payment'
  ) then
    raise exception 'signup requires a registered pass for this email';
  end if;

  return new;
end;
$$;

drop trigger if exists users_require_pass on auth.users;
create trigger users_require_pass
  before insert on auth.users
  for each row execute function public.enforce_signup_requires_pass();
