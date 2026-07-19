-- Requests v2 (2026-07-19): bootcamp type, paid request flow, room times.
--   * 'bootcamp' joins the request types (portal form -> Stripe -> inbox).
--   * 'pending_payment' status: private class and bootcamp requests are
--     created before Stripe checkout and only become visible ('new') when
--     the stripe-webhook confirms the payment by amount.
--   * Room bookings carry a same-day time range (practice hours).

alter table public.requests
  drop constraint requests_type_check;
alter table public.requests
  add constraint requests_type_check
  check (type in ('freeze', 'room_booking', 'private_class', 'bootcamp'));

alter table public.requests
  drop constraint requests_status_check;
alter table public.requests
  add constraint requests_status_check
  check (status in ('new', 'pending_payment', 'confirmed', 'declined', 'done'));

alter table public.requests
  add column time_from text check (time_from is null or time_from ~ '^\d{2}:\d{2}$'),
  add column time_until text check (time_until is null or time_until ~ '^\d{2}:\d{2}$');

-- Students may now also create rows that wait for payment.
drop policy "customers create own requests" on public.requests;
create policy "customers create own requests"
  on public.requests for insert
  to authenticated
  with check (
    lower(email) = lower(auth.jwt() ->> 'email')
    and status in ('new', 'pending_payment')
  );

-- Cap open rows including unpaid ones.
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
