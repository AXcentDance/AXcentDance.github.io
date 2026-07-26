-- Public trial-class requests for the owner WhatsApp confirmation inbox.
-- The public form writes through a tightly scoped RPC. The underlying table
-- stays private: only the authenticated studio owner may read or update rows.

create table public.trial_requests (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null check (char_length(name) between 1 and 120),
  phone text not null check (char_length(phone) between 8 and 30),
  selected_class text not null check (char_length(selected_class) between 1 and 180),
  locale text not null default 'en' check (locale in ('en', 'de')),
  status text not null default 'new' check (status in ('new', 'sent', 'dismissed')),
  whatsapp_opened_at timestamptz,
  sent_at timestamptz
);

create index trial_requests_status_idx
  on public.trial_requests (status, created_at desc);

alter table public.trial_requests enable row level security;

revoke all on public.trial_requests from anon;
grant select, update on public.trial_requests to authenticated;

create policy "owner reads trial requests"
  on public.trial_requests for select
  to authenticated
  using (public.is_owner());

create policy "owner updates trial requests"
  on public.trial_requests for update
  to authenticated
  using (public.is_owner())
  with check (public.is_owner());

create or replace function public.submit_trial_request(
  p_name text,
  p_phone text,
  p_selected_class text,
  p_locale text default 'en'
)
returns uuid
language plpgsql
security definer
set search_path = public
as $$
declare
  clean_name text := btrim(coalesce(p_name, ''));
  clean_phone text := btrim(coalesce(p_phone, ''));
  clean_class text := btrim(coalesce(p_selected_class, ''));
  clean_locale text := case when lower(coalesce(p_locale, '')) = 'de' then 'de' else 'en' end;
  phone_digits text;
  recent_count integer;
  new_id uuid;
begin
  phone_digits := regexp_replace(clean_phone, '[^0-9]', '', 'g');

  if char_length(clean_name) not between 1 and 120 then
    raise exception 'Please provide a valid name';
  end if;
  if char_length(clean_phone) not between 8 and 30 or char_length(phone_digits) < 8 then
    raise exception 'Please provide a valid WhatsApp number';
  end if;
  if char_length(clean_class) not between 1 and 180 then
    raise exception 'Please choose a trial class';
  end if;

  -- Limit repeated submissions for the same phone number while allowing a
  -- person to correct or repeat a genuine request when needed.
  select count(*) into recent_count
  from public.trial_requests
  where regexp_replace(phone, '[^0-9]', '', 'g') = phone_digits
    and created_at > now() - interval '24 hours';

  if recent_count >= 5 then
    raise exception 'Too many recent trial requests for this phone number';
  end if;

  insert into public.trial_requests (name, phone, selected_class, locale)
  values (clean_name, clean_phone, clean_class, clean_locale)
  returning id into new_id;

  return new_id;
end;
$$;

revoke all on function public.submit_trial_request(text, text, text, text) from public;
grant execute on function public.submit_trial_request(text, text, text, text) to anon, authenticated;

