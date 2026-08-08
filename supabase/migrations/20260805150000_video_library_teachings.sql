-- Teaching occurrences split out of library_videos (2026-08-05, same-day
-- refinement requested by the owner): a clip is cataloged once (title, the
-- level it is fit for, technique tags); every time it is taught becomes a
-- row in library_teachings. This enables "timeline of moves taught in
-- class X" and "taught again" logging without duplicating clip rows, and
-- youtube_id becomes unique again.

create table public.library_teachings (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  video_id bigint not null references public.library_videos (id) on delete cascade,
  course_id bigint not null references public.library_courses (id) on delete restrict,
  taught_on date not null
);

create index library_teachings_video_idx
  on public.library_teachings (video_id);
create index library_teachings_course_idx
  on public.library_teachings (course_id);
create index library_teachings_taught_on_idx
  on public.library_teachings (taught_on desc);

alter table public.library_teachings enable row level security;

create policy "owner full access" on public.library_teachings
  for all to authenticated
  using (public.is_owner()) with check (public.is_owner());

-- Preserve anything already cataloged under the old one-row-per-teaching
-- shape before the columns disappear.
insert into public.library_teachings (video_id, course_id, taught_on)
select id, course_id, taught_on from public.library_videos;

drop view public.library_coverage;

alter table public.library_videos
  drop column taught_on,
  drop column course_id;

-- One row per video again: re-teaching is a teachings row, not a duplicate
-- clip. The old non-unique lookup index is superseded.
drop index public.library_videos_youtube_id_idx;
create unique index library_videos_youtube_id_key
  on public.library_videos (youtube_id);

create view public.library_coverage
  with (security_invoker = on) as
  select
    t.id as technique_id,
    t.name as technique,
    v.level,
    count(distinct v.id) as clips,
    max(tg.taught_on) as last_taught_on
  from public.library_techniques t
  left join public.library_video_techniques vt on vt.technique_id = t.id
  left join public.library_videos v on v.id = vt.video_id
  left join public.library_teachings tg on tg.video_id = v.id
  group by t.id, t.name, v.level;
