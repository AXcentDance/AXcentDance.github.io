-- Fix infinite recursion in is_teacher() (2026-07-25).
--
-- is_teacher() reads public.teachers, and the RLS policy ON public.teachers
-- calls is_teacher() — so any teacher-authenticated query recursed until
-- Postgres aborted with "stack depth limit exceeded", making the whole
-- teacher portal unusable. SECURITY DEFINER lets the check read the table
-- without re-entering RLS. (is_owner() was never affected: it only reads
-- the JWT and touches no table.)

create or replace function public.is_teacher()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.teachers
    where lower(email) = lower(coalesce(auth.jwt() ->> 'email', ''))
      and active
  )
$$;
