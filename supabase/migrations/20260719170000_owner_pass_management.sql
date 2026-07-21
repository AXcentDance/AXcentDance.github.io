-- Owner pass management (2026-07-19, owner-requested):
--   * Sick days no longer extend the pass automatically. The portal files a
--     'sick_day' request instead; the admin page computes the proposed new
--     end date and the owner applies it with one click.
--   * The owner can read every registration and edit pass dates from the
--     admin page (previously dashboard-only).

drop trigger if exists absences_extend_pass on public.absences;
drop function if exists public.extend_pass_after_sick();

alter table public.requests
  drop constraint requests_type_check;
alter table public.requests
  add constraint requests_type_check
  check (type in ('freeze', 'room_booking', 'private_class', 'bootcamp', 'sick_day'));

create policy "owner reads all registrations"
  on public.registrations for select
  to authenticated
  using (public.is_owner());

create policy "owner updates registrations"
  on public.registrations for update
  to authenticated
  using (public.is_owner())
  with check (public.is_owner());

create policy "owner reads all absences"
  on public.absences for select
  to authenticated
  using (public.is_owner());
