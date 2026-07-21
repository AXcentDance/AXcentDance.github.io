-- Outside room requests (2026-07-20): the public "Rental Inquiry" form on
-- room-rental.html (no login, business/event bookings) now also lands in
-- the owner's requests inbox, alongside the existing FormSubmit email and
-- Sheets webhook — nothing about that existing flow changes, this just adds
-- visibility on the admin page. Distinct from 'room_booking', which is the
-- logged-in student practice-room feature in the portal.

alter table public.requests
  add column phone text check (phone is null or char_length(phone) <= 30);

alter table public.requests
  drop constraint requests_type_check;
alter table public.requests
  add constraint requests_type_check
  check (type in ('freeze', 'room_booking', 'private_class', 'bootcamp', 'sick_day', 'room_rental'));

-- The public form has no logged-in user, so it inserts as the anonymous
-- role. Scoped tightly: only this one type, only fresh ('new') rows, and
-- the existing enforce_request_limits trigger still caps open rows per email.
create policy "public can create room rental inquiries"
  on public.requests for insert
  to anon
  with check (type = 'room_rental' and status = 'new');
