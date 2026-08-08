-- Seed the owner's current class slots (2026-08-05, owner-provided list).
-- Day names normalized to full words; the owner can rename rows freely.
-- on conflict do nothing keeps the seed idempotent against the
-- lower(name) unique index.

insert into public.library_courses (name) values
  ('19:30 Monday'),
  ('19:30 Tuesday'),
  ('19:30 Wednesday'),
  ('20:30 Wednesday'),
  ('19:30 Thursday'),
  ('20:30 Thursday')
on conflict do nothing;
