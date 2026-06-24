# Phase 0 — Supabase setup (do this once to turn on accounts)

This turns on real per-user accounts ("Sign in with Google") for the **Alfred** platform — the
whole app (the launcher at `/` and Atlas at `/atlas`) sits behind one login. The app code is
already built; it stays open (or on the legacy `SITE_PASSWORD`) until these env vars are set. None
of this needs code — it's all in the Supabase + Google dashboards plus the one SQL file here.

## Steps

1. **Create a Supabase project** (free tier). From Settings → API, copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_ANON_KEY` (public — it ships in the site)
   - **JWT secret** (Settings → API → JWT Keys, legacy HS256 shared secret) → `SUPABASE_JWT_SECRET` (**sensitive** — server-only)

2. **Enable Google auth.** Supabase → Authentication → Providers → Google. Create an OAuth
   client in Google Cloud (Authorized redirect URI = the `…/auth/v1/callback` URL Supabase
   shows you), then paste the Google client ID + secret into Supabase. (Apple is deferred —
   it needs the paid Apple Developer program.)

3. **Add redirect URLs.** Supabase → Authentication → URL Configuration → Redirect URLs, add:
   - `https://<your-site>/**`  (the wildcard lets us return to any deep link / `/login`)
   - `http://localhost:4173/**`  (local preview)

4. **Run the schema.** Open `schema.sql` (next to this file) in the Supabase SQL editor and
   run it. It creates `profiles` (+ an auto-insert trigger on signup), `watchlist`,
   `coverage_requests`, `audit_log`, and the RLS policies. **Edit the `ADMIN_EMAIL` line** in
   that file to your account email before (or after) running, so you can see the request queue.

5. **Set the env vars** in Vercel (Project → Settings → Environment Variables) and in a local
   `.env` for preview:
   ```
   SUPABASE_URL=https://<ref>.supabase.co
   SUPABASE_ANON_KEY=<anon public key>
   SUPABASE_JWT_SECRET=<JWT secret>
   ```
   The moment `SUPABASE_JWT_SECRET` is present, the edge middleware switches from the shared
   password to per-user accounts automatically. You can then remove `SITE_PASSWORD`.

## How to confirm it works
- Redeploy (or `node site/build.mjs` + `vercel dev` locally). Visit `/` or `/atlas` while signed
  out → you're redirected to `/login`. Click **Continue with Google** → you land on the launcher
  signed in. A direct `/atlas/briefs/<id>/<date>.html` URL is gated the same way.
- Decode your real access token once (jwt.io) and confirm it carries `role: "authenticated"`
  and `aud: "authenticated"` — that's what the gate checks. (Supabase always stamps these; this
  is just a belt-and-suspenders confirmation against a live token.)

The gate's verification logic is covered by `tests/middleware_gate.test.mjs`
(`node tests/middleware_gate.test.mjs`).
