# Atlas weekly improvement review — 2026-07-07

Propose-only audit (first in the series — no prior report to follow up on). Nothing changed except
this file and a memory note. Audited against `origin/main` (local checkout was 183 commits behind).

## 🔴 Urgent

1. **Both public-sync workflows are silently OFF.** `gh workflow list --all` shows *Sync to Public
   alfred-tools* and *Pull updates from public alfred-tools* as `disabled_manually`. No sync run
   since 2026-07-01 — the public mirror (Agrimd15/alfred-tools) has been frozen ~6 days while ~40+
   companies were published/refreshed. Almost certainly disabled to silence the 2026-06-30 billing
   failures and never re-enabled (CI + auto-merge are green now, so the outage is over).
   → **Re-enable both**: `gh workflow enable "Sync to Public alfred-tools"` and `… "Pull updates from
   public alfred-tools"`, then confirm the next scheduled run pushes clean.

2. **HEAD of `main` is an unreviewed brief with a BLOCKING mobile overflow — and it's on the public
   demo.** Commit `3edf378` `[NEEDS HUMAN REVIEW] databricks + standard-intelligence` sits on main;
   both briefs overflow at 390px (databricks 406px, standard-intelligence 620px). `databricks` is in
   `DEMO_IDS`, so this ships to the public face. The commit prescribes the fix: wrap the
   private-company comps table in `<div class="table-scroll">` in `deliverable_agent.py` — one
   selector clears both briefs. → Apply the wrapper, re-render both, drop the `NEEDS HUMAN REVIEW` tag.

## 🟡 Soon

3. **5 stale open PRs (22–33 days), all safe to close.** `#66` & `#59` (CRM/BE/NTSK refreshes,
   06-14/15) are superseded by newer main coverage (CRM 07-06, BE 07-05, NTSK 06-24) → close.
   `#58` (DRAFT, "Routine scheduling") is superseded — the routine is live (Group 3/4 refreshes
   running daily); auto-merge skips drafts so it can never land anyway → close. `#60` ("two-col prose
   layout") is `DIRTY` (merge conflict), a code PR → rebase-or-close decision. `#11` ("Reframe repo as
   alfred-tools", 33d) → decide/close.

4. **Recurring metric-audit warning cluster: "prose doesn't tie."** SOFI (2), WIX (3), databricks (1)
   flag prose $ figures that differ from the metrics grid *because the basis differs* — segment vs
   total revenue (SOFI $642M/$3B vs $1.10B net rev), run-rate YoY vs GAAP annual (databricks 65% vs
   84.6%). **No BLOCKING contradictions** — the trust layer holds — but the same false-positive shape
   recurs every run and a human has to re-verify it. → Tooling fix: teach `metric_audit.py` to
   recognize segment/FY/run-rate bases, or require inline period labels on prose figures so these
   stop reading as defects.

## 🟢 Nice-to-have

5. **No failure alerting on the sync/pull workflows.** They failed 3 days (06-28→30) then sat disabled
   a week with nothing surfacing it — this review is what caught it. Add a lightweight alert (file an
   issue / push notification when Sync/Pull fails *or is disabled*), mirroring the stale-PR sentinel.

6. **`notify-landing-page` failed every run in the 06-28/29 billing window;** hasn't triggered since
   (only fires on `plugins/**` changes). Likely self-resolved — just verify the next plugin-surface
   change turns it green.

7. **Local checkout is 183 commits behind `origin/main`.** Not a repo defect, but `git pull` before
   any local Atlas work so you don't branch off a stale base (per the atlas-publish-flow memory).

## ✅ Healthy

CI smoke tests, auto-merge, and stale-PR sentinel all green. Action versions current (checkout@v4,
setup-python@v5, github-script@v7 — no deprecations). **127 companies** covered and fresh — only
`maximor` (2026-06-21) is >14 days stale; the 06-24 cohort (AFRM/CRWD/FROG/KLAC/LRCX/NTSK/OKTA/PLTR/
TOST) ages out in ~2 days. No orphaned reverse-sync branches. **No BLOCKING metric contradictions** on
any sampled brief. DEMO set fresh (all ≤13d).
