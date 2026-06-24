# Deploy your own Alfred

Alfred is an analyst-tools platform; **Atlas** — company name → banker-grade research brief — is its
first tool. You sign in once, pick a tool from the launcher, and Atlas opens your coverage library.
This takes you from clone to a live, login-gated site in ~15 minutes. **Fastest path: open this repo
in Claude Code and run `/setup`** — it does all of the below interactively. Here's the manual version.

## What you'll end up with
- A private coverage database (`data-dumps/`) that grows as you research companies.
- A self-contained **HTML + PDF brief** per company.
- A walled **Alfred** site: a tool **launcher** at `/`, the **Atlas** library at `/atlas`, and
  sign-in at `/login` — the whole app behind your login (Google accounts, or a simple shared
  password).

## Prerequisites
- **[Claude Code](https://claude.com/claude-code)** - the research agents run inside it.
- **Node.js 18+** and **Python 3.9+** - for the site build and brief/PDF generation.
- **Google Chrome / Chromium** - used to render the PDF (no extra setup).
- *(optional)* a free **FMP API key** ([financialmodelingprep.com](https://financialmodelingprep.com)) for live comps. yfinance works with no key.

## 1. Clone
```bash
git clone https://github.com/Agrimd15/alfred-tools.git
cd alfred-tools
pip3 install yfinance requests
```
Pushing this to a **private repo of your own** is recommended — your coverage database stays yours.

## 2. Configure (optional)
```bash
cp .env.example .env      # add FMP_API_KEY if you have one
```

## 3. Make the coverage yours
This repo ships a handful of sample companies under `data-dumps/`. To start clean:
```bash
rm -rf data-dumps/*/      # removes sample companies, keeps the folder
```
Companies you research are gitignored by default, so your private coverage never lands in a public fork.

## 4. Research a company - the core loop
In Claude Code, from the repo root:
```
/atlas SNOW
```
(or just type a company name). Four parallel agents run, write `data-dumps/SNOW/profile.json`, and
generate an HTML + PDF brief in the run folder. Every number is pulled live and dated.

## 5. Build & preview locally
```bash
node site/build.mjs
npx -y serve site/dist -l 4321        # → http://localhost:4321  (or: python3 -m http.server 4321 --directory site/dist)
```
You'll get the Alfred launcher at `/` and Atlas at `/atlas`. Locally the static server doesn't run
the edge gate, so the app is open for preview — that's expected; the gate applies once deployed
(below).

## 6. Choose who can get in (the gate)
The whole Alfred app is walled by `middleware.js`. Pick one:
- **Simplest — a shared password.** Set the env var **`SITE_PASSWORD`**; the site asks for it once
  and remembers you. Good for a private instance you don't want to wire up accounts for.
- **Real accounts — Sign in with Google (recommended).** Follow **[`supabase/README.md`](supabase/README.md)**:
  create a free Supabase project, enable Google, run `supabase/schema.sql`, and set `SUPABASE_URL`,
  `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`. When the JWT secret is set it takes over from the
  password, giving each user their own login.
- **Set neither** and the site is fully open (handy for a public, ungated demo deployment).

## 7. Deploy to Vercel
1. Push your repo to GitHub.
2. Vercel → **Add New → Project** → import it.
3. **Leave Root Directory at the repo root**; Framework = **Other** (build command + output dir come
   from `vercel.json` automatically).
4. Add your gate env vars from step 6 (`SITE_PASSWORD`, **or** the three `SUPABASE_*` vars).
5. **Deploy.** Vercel auto-issues HTTPS.

Every push to `main` redeploys. To add a company later: `/atlas TICKER` → `git push` → live in ~1 minute.

## 8. Staying up to date (automatic)
The repo ships `.github/workflows/pull-upstream.yml`: once a day your clone checks the public
[alfred-tools](https://github.com/Agrimd15/alfred-tools) for new code and opens a PR in **your**
repo with the update — your `data-dumps/`, `.gitignore`, and workflows are never touched. Review
and merge (check `CLAUDE.md` for instance-specific state first). Manual alternative anytime:
```bash
git remote add upstream https://github.com/Agrimd15/alfred-tools.git   # once
git fetch upstream && git merge upstream/main
```
> GitHub pauses scheduled workflows after ~60 days without repo activity — re-enable from the
> Actions tab if your repo went quiet.

## 9. Custom domain (optional)
Vercel → Project → **Settings → Domains** → add your domain, then add the DNS record Vercel shows at
your registrar. SSL is automatic.

## (Optional) Publishing a public mirror — `DEMO_IDS`
If you also maintain a **public, ungated** copy (the way upstream `alfred-tools` ships a sample set),
`DEMO_IDS` at the top of [`site/build.mjs`](site/build.mjs) lists which companies are allowed into
that public mirror — everything else stays private. For a normal private instance you can ignore it.
```js
const DEMO_IDS = ['NTSK', 'CRWV', 'AVGO'];   // folder ids: ticker for public cos, kebab-slug for private
```

## Security & rules
- `vercel.json` ships with HSTS, a Content-Security-Policy, and other hardening headers (A/A+ on securityheaders.com).
- The whole app is gated **server-side at the edge** (`middleware.js`) — by your Google login
  (Supabase session) or `SITE_PASSWORD` — so brief files are protected before they're served, not
  just hidden in the browser.
- **Public information only** - no MNPI, client names, or deal data. Every output is **DRAFT** until you review it.
