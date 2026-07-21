-- Renewal reminder (2026-07-20): on the Monday of a pass's final week the
-- renewal-reminder edge function emails the student. pg_cron invokes the
-- function DAILY (the function itself only acts on passes whose end date
-- falls inside the current Mon-Sun week and that have not been reminded),
-- so a failed Monday run heals itself on Tuesday.
--
-- NOTE: the cron job carries an x-cron-secret header. The real secret is
-- scheduled directly against the live database and stored as the
-- CRON_SECRET function secret — the placeholder below is never used.

alter table public.registrations
  add column renewal_reminder_sent_at timestamptz;

-- A pass that gets extended (freeze, sick day) earns a fresh reminder for
-- its new final week.
create or replace function public.reset_renewal_reminder()
returns trigger
language plpgsql
as $$
begin
  if new.pass_end_date is distinct from old.pass_end_date
     and new.pass_end_date > old.pass_end_date then
    new.renewal_reminder_sent_at := null;
  end if;
  return new;
end;
$$;

create trigger registrations_reset_reminder
  before update on public.registrations
  for each row execute function public.reset_renewal_reminder();

create extension if not exists pg_cron;
create extension if not exists pg_net;

-- Daily at 07:30 UTC (08:30/09:30 in Zurich depending on DST).
select cron.schedule(
  'renewal-reminder-daily',
  '30 7 * * *',
  $CRON$
  select net.http_post(
    url := 'https://jwravnvytkmsvqoqkmwb.supabase.co/functions/v1/renewal-reminder',
    headers := jsonb_build_object('Content-Type', 'application/json', 'x-cron-secret', 'SET_AT_DEPLOY_TIME'),
    body := '{}'::jsonb
  );
  $CRON$
);
