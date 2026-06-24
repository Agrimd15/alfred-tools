-- Atlas Layer 2 — Supabase schema (Phase 0)
-- ===========================================================================
-- Run this once in your Supabase project's SQL editor (Dashboard → SQL Editor → New query).
-- It creates the user-account tables and Row-Level Security so each signed-in user can read/
-- write ONLY their own rows. Git stays the brief database; Supabase holds only account data
-- (profiles, watchlists, coverage requests, an audit log).
--
-- Idempotent: safe to re-run. Phase 1 (login) strictly needs only `profiles` + its trigger;
-- the rest is for Phases 2–4 (watchlist, request queue, alerts) and is created now so the
-- schema is complete.
--
-- AFTER running this, set the admin email in the `coverage_requests` admin policy below
-- (search for ADMIN_EMAIL) to whoever should see the full request queue.
-- ===========================================================================

-- ── 1. profiles — one row per user, keyed to auth.users ────────────────────
create table if not exists public.profiles (
  id           uuid primary key references auth.users (id) on delete cascade,
  email        text,
  display_name text,
  created_at   timestamptz not null default now()
);

-- Auto-create a profile row the moment a new auth user signs up (Google, etc.).
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, display_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ── 2. watchlist — a user's starred companies (Phase 2) ────────────────────
create table if not exists public.watchlist (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references public.profiles (id) on delete cascade,
  folder_id    text not null,            -- the Atlas coverage folder id (e.g. "SNOW")
  company_name text,
  created_at   timestamptz not null default now(),
  unique (user_id, folder_id)            -- a name can be starred once per user
);

-- ── 3. coverage_requests — "request a name" queue (Phase 3) ────────────────
create table if not exists public.coverage_requests (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references public.profiles (id) on delete cascade,
  query      text not null,             -- what the user asked to be covered
  status     text not null default 'queued'
             check (status in ('queued', 'running', 'published', 'declined')),
  folder_id  text,                      -- set when fulfilled (links to the published brief)
  note       text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ── 4. audit_log — lightweight activity trail ──────────────────────────────
create table if not exists public.audit_log (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid references public.profiles (id) on delete set null,
  action     text not null,
  meta       jsonb,
  created_at timestamptz not null default now()
);

-- ── Row-Level Security ─────────────────────────────────────────────────────
alter table public.profiles          enable row level security;
alter table public.watchlist         enable row level security;
alter table public.coverage_requests enable row level security;
alter table public.audit_log         enable row level security;

-- profiles: a user sees/edits only their own row.
drop policy if exists "profiles_self_select" on public.profiles;
create policy "profiles_self_select" on public.profiles
  for select using (auth.uid() = id);
drop policy if exists "profiles_self_update" on public.profiles;
create policy "profiles_self_update" on public.profiles
  for update using (auth.uid() = id) with check (auth.uid() = id);

-- watchlist: full CRUD on own rows only.
drop policy if exists "watchlist_self_all" on public.watchlist;
create policy "watchlist_self_all" on public.watchlist
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- coverage_requests: a user manages their own rows…
drop policy if exists "requests_self_all" on public.coverage_requests;
create policy "requests_self_all" on public.coverage_requests
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
-- …and the admin (you) can read the whole queue. The email comes straight from the JWT,
-- so no table lookup is needed. >>> REPLACE ADMIN_EMAIL with your account email. <<<
drop policy if exists "requests_admin_select" on public.coverage_requests;
create policy "requests_admin_select" on public.coverage_requests
  for select using ((auth.jwt() ->> 'email') = 'agrimd3@gmail.com');  -- ADMIN_EMAIL

-- audit_log: a user can read their own entries; writes go through definer functions /
-- the service role (no user-facing insert policy on purpose).
drop policy if exists "audit_self_select" on public.audit_log;
create policy "audit_self_select" on public.audit_log
  for select using (auth.uid() = user_id);
