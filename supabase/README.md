# Phase 0 — Supabase setup (do this once to turn on accounts)

This turns on real per-user accounts ("Sign in with Google") for **Alfred**. Sign-in lives on the
**`alfred-analyst`** front door (alfred-analyst.com); it gates and proxies `/atlas/*` to this Atlas
deployment, so one login covers everything. The code is already built; it stays open until these
env vars are set. None of this needs code — it's the Supabase + Google dashboards plus the one SQL
file here.

> **Two Vercel projects share the env.** `alfred-analyst` (the front door) needs `SUPABASE_URL` +
> `SUPABASE_ANON_KEY` (its login client) **and** `SUPABASE_JWT_SECRET` (its `/atlas` gate). This
> `atlas-private` project needs `SUPABASE_JWT_SECRET` (its verify-only gate), plus `SUPABASE_URL` +
> `SUPABASE_ANON_KEY` for the coverage page's session, and optional `LOGIN_URL`
> (default `https://alfred-analyst.com`). Use the **same** values in both.

## Steps

1. **Create a Supabase project** (free tier). From Settings → API, copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY` (public — it ships in the site)
   - **JWT secret** (Settings → API → JWT Keys, legacy HS256 shared secret) → `SUPABASE_JWT_SECRET` (**sensitive** — server-only)

2. **Enable Google auth.** Supabase → Authentication → Providers → Google. Create an OAuth
   client in Google Cloud (Authorized redirect URI = the `…/auth/v1/callback` URL Supabase
   shows you), then paste the Google client ID + secret into Supabase. (Apple is deferred —
   it needs the paid Apple Developer program.)

3. **Add redirect URLs.** Supabase → Authentication → URL Configuration → Redirect URLs, add the
   **front-door** origin (where login runs):
   - `https://alfred-analyst.com/**`  (the wildcard lets us return to any deep link, incl. `/atlas`)
   - `http://localhost:3000/**`  (local `vercel dev` of alfred-analyst)

4. **Run the schema.** Open `schema.sql` (next to this file) in the Supabase SQL editor and
   run it. It creates `profiles` (+ an auto-insert trigger on signup), `watchlist`,
   `coverage_requests`, `audit_log`, and the RLS policies. **Edit the `ADMIN_EMAIL` line** in
   that file to your account email before (or after) running, so you can see the request queue.

5. **Set the env vars** on **both** Vercel projects (Settings → Environment Variables), same values:
   ```
   SUPABASE_URL=https://<ref>.supabase.co
   SUPABASE_ANON_KEY=<anon public key>
   SUPABASE_JWT_SECRET=<JWT secret>
   ```
   (`alfred-analyst` also serves a committed `config.js` with the public URL + anon key for its login
   client.) The moment `SUPABASE_JWT_SECRET` is present, the gates switch from open to
   per-user accounts.

## How to confirm it works
- Redeploy both. Visit `alfred-analyst.com/atlas` while signed out → you're redirected to
  `alfred-analyst.com/login`. Click **Continue with Google** → you land back on `/atlas` signed in,
  seeing the full coverage library. A direct `atlas-private.vercel.app/...` URL while signed out is
  redirected to the front-door login too.
- Decode your real access token once (jwt.io) and confirm it carries `role: "authenticated"`
  and `aud: "authenticated"` — that's what the gate checks. (Supabase always stamps these; this
  is just a belt-and-suspenders confirmation against a live token.)

The gate's verification logic is covered by `tests/middleware_gate.test.mjs`
(`node tests/middleware_gate.test.mjs`).
