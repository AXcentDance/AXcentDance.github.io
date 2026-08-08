-- Owner video library: private teaching archive (2026-08-05).
-- Class clips live on YouTube as unlisted uploads (uploaded through an
-- official YouTube client; API uploads stay locked-private until the Google
-- compliance audit passes, see _videos.html). These tables hold metadata
-- only. Each entry is a teaching occurrence: which class it was filmed in,
-- on what date, which technique tags it demonstrates, and which level the
-- move is fit for — so the owner can ask "when did I last teach X at level
-- Y" and "what is undercovered". The same YouTube video may appear on
-- several dates (taught again), so youtube_id is deliberately not unique.
-- Owner-only: is_owner() (info@axcentdance.com) gates every RLS path, same
-- pattern as the requests inbox. The anon key exposes nothing.

create table public.library_techniques (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 1 and 80),
  -- Optional manual ordering; ties break alphabetically in the UI.
  sort_order integer not null default 0
);

create unique index library_techniques_name_key
  on public.library_techniques (lower(name));

create table public.library_courses (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 1 and 120),
  starts_on date
);

create unique index library_courses_name_key
  on public.library_courses (lower(name));

create table public.library_videos (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  youtube_id text not null check (youtube_id ~ '^[A-Za-z0-9_-]{5,20}$'),
  title text not null check (char_length(title) between 1 and 200),
  taught_on date not null,
  course_id bigint not null references public.library_courses (id) on delete restrict,
  -- The level this move is fit for. Free text on purpose: levels follow the
  -- course pages (Foundation, Improver, Inter/Adv, ...) but the archive must
  -- not block on renames.
  level text not null check (char_length(level) between 1 and 40),
  notes text check (char_length(notes) <= 2000)
);

create index library_videos_youtube_id_idx
  on public.library_videos (youtube_id);
create index library_videos_taught_on_idx
  on public.library_videos (taught_on desc);
create index library_videos_course_idx
  on public.library_videos (course_id);

-- A clip usually demonstrates several techniques (combos), hence a junction
-- table rather than a column.
create table public.library_video_techniques (
  video_id bigint not null references public.library_videos (id) on delete cascade,
  technique_id bigint not null references public.library_techniques (id) on delete restrict,
  primary key (video_id, technique_id)
);

alter table public.library_techniques enable row level security;
alter table public.library_courses enable row level security;
alter table public.library_videos enable row level security;
alter table public.library_video_techniques enable row level security;

create policy "owner full access" on public.library_techniques
  for all to authenticated
  using (public.is_owner()) with check (public.is_owner());

create policy "owner full access" on public.library_courses
  for all to authenticated
  using (public.is_owner()) with check (public.is_owner());

create policy "owner full access" on public.library_videos
  for all to authenticated
  using (public.is_owner()) with check (public.is_owner());

create policy "owner full access" on public.library_video_techniques
  for all to authenticated
  using (public.is_owner()) with check (public.is_owner());

-- Dashboard convenience: clip count and last-taught date per technique and
-- level. Techniques never filmed appear with a null level. The admin page
-- computes the full technique x level matrix client-side; this view exists
-- for ad-hoc SQL in the Supabase dashboard. security_invoker keeps RLS in
-- force for whoever queries it.
create view public.library_coverage
  with (security_invoker = on) as
  select
    t.id as technique_id,
    t.name as technique,
    v.level,
    count(v.id) as clips,
    max(v.taught_on) as last_taught_on
  from public.library_techniques t
  left join public.library_video_techniques vt on vt.technique_id = t.id
  left join public.library_videos v on v.id = vt.video_id
  group by t.id, t.name, v.level;
