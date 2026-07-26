-- Let staff have accounts (2026-07-25).
--
-- enforce_signup_requires_pass() gates signup on owning a real pass, which is
-- right for students but blocks teachers, who never buy one. Allow any email
-- already listed in `teachers` as well, so the owner can create teacher
-- logins (and a future teacher self-signup would work) without weakening the
-- student rule.

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

  -- staff: listed as a teacher
  if exists (
    select 1 from public.teachers
    where lower(email) = lower(new.email)
  ) then
    return new;
  end if;

  -- students: must own a pass the webhook or staff actually activated
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
