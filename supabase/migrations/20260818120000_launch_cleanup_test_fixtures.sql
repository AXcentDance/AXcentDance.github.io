-- Launch cleanup (merge-to-main checklist): remove the portal test account
-- and every row it created, before real students use the portal.
-- Scoped to the one test email; absences and attendance cascade from the
-- registration delete (registration_id ... on delete cascade). Idempotent.

delete from public.requests
where lower(email) = 'slamitza+portaltest@gmail.com';

delete from public.registrations
where lower(email) = 'slamitza+portaltest@gmail.com';

delete from auth.users
where lower(email) = 'slamitza+portaltest@gmail.com';
