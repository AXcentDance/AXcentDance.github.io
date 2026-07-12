-- Yes/no probe used by the registration form to greet returning customers.
-- SECURITY DEFINER so it can see rows the anonymous role cannot; it exposes
-- nothing but a boolean, and only for the exact email asked about.
create or replace function public.email_has_profile(check_email text)
returns boolean
language sql
security definer
set search_path = public
stable
as $$
  select exists (
    select 1 from public.registrations
    where lower(email) = lower(check_email)
      and status <> 'pending_payment'
  );
$$;

grant execute on function public.email_has_profile(text) to anon, authenticated;
