-- Class attendance (2026-07-19): one row per dancer per class per date,
-- marked by staff from _attendance.html. Unmarked = no row; flex-pass
-- consumption is the count of 'present' rows.

create table public.attendance (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  class_value text not null,
  class_date date not null,
  registration_id uuid not null references public.registrations(id) on delete cascade,
  email text not null,
  status text not null check (status in ('present', 'absent')),
  unique (class_date, class_value, registration_id)
);

create index attendance_class_idx on public.attendance (class_value, class_date);
create index attendance_email_idx on public.attendance (lower(email));

alter table public.attendance enable row level security;

-- Students may read their own marks (future portal feature); the owner
-- reads everything and is the only writer.
create policy "read own attendance, owner reads all"
  on public.attendance for select
  to authenticated
  using (lower(email) = lower(auth.jwt() ->> 'email') or public.is_owner());

create policy "owner writes attendance"
  on public.attendance for insert
  to authenticated
  with check (public.is_owner());

create policy "owner updates attendance"
  on public.attendance for update
  to authenticated
  using (public.is_owner())
  with check (public.is_owner());

create policy "owner deletes attendance"
  on public.attendance for delete
  to authenticated
  using (public.is_owner());
