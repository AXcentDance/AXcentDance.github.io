-- Private-class session tracking (2026-07-20): a purchased package is worth
-- 1 / 3 / 5 private hours (sessions_total, set by the portal at purchase
-- time); the owner ticks off delivered hours (+1) from the admin page.
-- Room bookings and other request types leave both columns untouched.

alter table public.requests
  add column sessions_total integer
    check (sessions_total is null or sessions_total > 0),
  add column sessions_done integer not null default 0
    check (sessions_done >= 0);
