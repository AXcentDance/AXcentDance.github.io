-- Daily teaching-reminder job (2026-07-20). Runs at 20:00 UTC (21:00/22:00
-- Zurich), by which point the previous evening's classes are comfortably
-- past the 24h grace period the function enforces per class start time.
--
-- As with the renewal reminder, the real x-cron-secret is scheduled directly
-- against the live database and kept as the CRON_SECRET function secret —
-- the placeholder below is never used.

select cron.schedule(
  'teaching-reminder-daily',
  '0 20 * * *',
  $CRON$
  select net.http_post(
    url := 'https://jwravnvytkmsvqoqkmwb.supabase.co/functions/v1/teaching-reminder',
    headers := jsonb_build_object('Content-Type', 'application/json', 'x-cron-secret', 'SET_AT_DEPLOY_TIME'),
    body := '{}'::jsonb
  );
  $CRON$
);
