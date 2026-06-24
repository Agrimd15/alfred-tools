# Atlas v2 — Accounts & Coverage Platform (Layer 2)

Branch: `feat/v2-accounts`

## Goal

Turn Atlas from "a static coverage site behind one shared password" into "a coverage
platform with real personal accounts." Target user for v2: **individuals** (analysts,
operators, curious finance people) — not yet funds/SSO. Sign in with Google (Apple later),
get a watchlist and the ability to request coverage of a name.

Non-goals for this layer: teams/orgs, SSO/SAML, billing, BYOK (that's Layer 3).

## Decisions

- **Auth + DB: Supabase.** One free project gives Google/Apple OAuth + Postgres + Row-Level
  Security. We need a DB anyway (watchlists, request queue, audit log), so a unified free tier
  beats stitching Clerk (auth) + a separate Postgres together. Swappable later if needed.
- **Keep the static-site architecture.** The site is built by `site/build.mjs` and served on
  Vercel. We add the Supabase **browser JS client** to the existing pages instead of rewriting
  into a framework. No Next.js migration required for v1 of this layer.
- **Git stays the brief database.** Supabase stores *only* user/account data (profiles,
  watchlists, requests). The brief artifacts remain version-controlled in `data-dumps/`.
- **Google first, Apple later.** Google OAuth is free. Apple Sign In needs the paid Apple
  Developer Program ($99/yr) for the Service ID — defer until we're ready to pay it.
- **The `/full` gate becomes login-based.** Public demo at `/` stays open. `/full` flips from
  the shared `SITE_PASSWORD` cookie to a verified Supabase session.

## Data model (Supabase Postgres)

```
profiles          (id = auth.users.id, email, display_name, created_at)
watchlist         (id, user_id → profiles, folder_id, company_name, created_at)
coverage_requests (id, user_id → profiles, query, status[queued|running|published|declined],
                   folder_id nullable, note, created_at, updated_at)
audit_log         (id, user_id nullable, action, meta jsonb, created_at)
```

All tables get **RLS policies**: a user can read/write only rows where `user_id = auth.uid()`.
`coverage_requests` is additionally readable by an admin role (you) to work the queue.

## Phases

**Phase 0 — Supabase setup (no code)**
- Create project; copy `SUPABASE_URL` + `SUPABASE_ANON_KEY`.
- Enable Google provider (OAuth consent screen + client ID). Apple deferred.
- Create the tables above + RLS policies via SQL editor.

**Phase 1 — Auth on the site**
- Add Supabase JS client to the site template. Add a minimal sign-in page (Google button).
- Session handling: store session, show signed-in state in the header, sign-out.
- Replace the `/full` password gate in `middleware.js` with a Supabase JWT check
  (verify the access token with the project JWT secret in edge middleware).
- Public demo `/` unchanged.

**Phase 2 — Watchlist**
- "Star" control on each company card and at the top of a brief.
- A "My coverage" view that lists the user's starred names (reads `watchlist` via RLS).

**Phase 3 — Request coverage queue**
- "Request a name" input writes a row to `coverage_requests` (status `queued`).
- Admin view (you) lists the queue. Fulfilling a request = run Atlas, publish the brief,
  set status `published` + link the `folder_id`. (Run stays manual/triggered for now —
  no auto-spend.)

**Phase 4 — Alerts (optional, later)**
- Email on "your requested name is published" and "a watchlisted name has earnings this week"
  (Supabase scheduled function + a free email sender like Resend).

## Open questions to resolve before Phase 1

1. Confirm Supabase as the provider (vs Clerk + separate DB).
2. Where does the sign-in UI live — a new `/login` page in the static build, or a modal on
   the existing index? (Lean: dedicated `/login`, simplest to reason about.)
3. Admin identity for the request queue — a hard-coded allowlist of your email(s) in an RLS
   policy is enough for v1.

## What this does NOT touch

The research pipeline (`agents/`), the brief renderer, the QA passes, and the
git-as-database convention are all unchanged. This layer wraps the existing site; it does
not alter how a brief is produced.
