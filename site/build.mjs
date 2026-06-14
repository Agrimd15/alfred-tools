#!/usr/bin/env node
// Atlas site build — assembles the static coverage viewer into site/dist.
//
// Emits TWO views from data-dumps:
//   • dist/        → PUBLIC demo: the DEMO_COUNT most-recent companies, no auth
//   • dist/full/   → FULL coverage: every company, gated by middleware.js (SITE_PASSWORD)
// Each view gets its own index.json + index.html + briefs/, so the shared template's
// relative fetches ("index.json", "briefs/…") just work in either directory. A company's
// brief is only published into a view that includes it, so private briefs never land in
// the public root.
//
// Zero dependencies. Run from repo root: `node site/build.mjs`. Vercel runs the same
// (project repo root (default), so the build command is just `node site/build.mjs`).

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');          // repo root (data-dumps lives here)
const DATA = path.join(ROOT, 'data-dumps');
const OUT = path.join(__dirname, 'dist');            // site/dist (published)
const TEMPLATE = path.join(__dirname, 'template', 'index.html');

// Companies shown on the PUBLIC demo at the site root. Everything else is reachable
// only via the gated /full view. Add more demo ids over time. (Folder ids: Broadcom = "AVGO".)
// Refreshed 2026-06-11: the public demo now features Netskope plus the latest coverage
// (CoreWeave, Broadcom, AppLovin, Figma, Databricks). The prior demo names (CRM, EGAN,
// forgepoint-ai, standard-intelligence) are archived off the live demo but remain in /full.
// Public demo shows the N most recently updated companies from the full coverage set.
const DEMO_COUNT = 5;

// Vercel Web Analytics tag, injected into each published brief page at build time.
const ANALYTICS_TAG = '<script defer src="/_vercel/insights/script.js"></script>';

// ── Sector buckets for the filter bar. Profile `verticals` are free-form (80+ unique
// tags), so the site maps them into this canonical set and renders one chip per bucket.
// Matching is keyword-based against each vertical string, so newly researched companies
// bucket themselves with no manual tagging. A company can land in several buckets.
// Kept deliberately BROAD for now — a handful of top-level tech sectors rather than
// fine-grained sub-categories. Matching is keyword-based against each free-form vertical
// string, so a company can land in several buckets and new names self-classify.
const SECTORS = [
  ['Software',            /software|\bsaas\b|\bcrm\b|\berp\b|productivity|design software|creative tools|knowledge management|customer (engagement|service)|sales automation|database|data (platform|cloud|warehouse|engineering)|analytics|lakehouse|nosql|vector search|log management|restaurant|point of sale|\bsmb\b|vertical saas/i],
  ['AI',                  /artificial intelligence|foundation model|agentic|ai agents?|enterprise ai|generative ai|genai|machine learning|ai research|\bllm\b|\bai\b/i],
  ['Semiconductors',      /semiconductor|\bsemis?\b|\bdram\b|\bnand\b|\bhbm\b|silicon|\basic\b|\bxpu\b|\bgpus?\b|\bcpus?\b|accelerator|chiplet|foundry|\beuv\b|optical|interconnect/i],
  ['Cloud & Infra',       /cloud|infra|data ?center|(?<!quantum )networking|\bcdn\b|\bedge\b|serverless|observability|monitoring|\bapm\b|hyperscaler|ethernet|security|cyber|\bsase\b|\bsse\b|zero trust|\bsiem\b|endpoint|devops/i],
  ['Internet & Consumer', /internet|e-?commerce|\bcommerce\b|adtech|advertis|\bctv\b|consumer|marketplace|payments|fintech|gaming|\bmedia\b/i],
  ['Frontier Tech',       /quantum|deep tech|robotics|defense|gov tech|national security|\bspace\b|autonomous|biotech/i],
];
const sectorsFor = (verticals) =>
  SECTORS.filter(([, re]) => verticals.some((v) => re.test(v))).map(([name]) => name);

const readJSON = (p) => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return null; } };
const ensureDir = (p) => fs.mkdirSync(p, { recursive: true });

// Choose the right brief when a run folder has more than one HTML file.
function pickBrief(files, id) {
  if (!files.length) return null;
  const lid = id.toLowerCase();
  return files.find((f) => f.toLowerCase().includes(lid))      // matches the folder id
      || files.find((f) => /brief/i.test(f))                   // any *brief*.html
      || files.slice().sort()[0];                              // fallback: first
}

// Bare domain (no protocol, no www, no path) — the client builds logo URLs from this.
function cleanDomain(profile) {
  const host = (profile.website || '')
    .replace(/^https?:\/\//, '').replace(/\/.*$/, '').replace(/^www\./, '').trim();
  return host || null;
}

// Honor an explicit faviconUrl from the profile, but drop the deprecated Clearbit
// logo API — it no longer serves reliably, so we let the client resolve from domain.
function explicitFavicon(profile) {
  const u = profile.faviconUrl;
  return u && !/clearbit\.com/i.test(u) ? u : null;
}

const cap = (s, n = 220) => (s.length > n ? s.slice(0, n - 1).trimEnd() + '…' : s);
function firstSentence(s) {
  s = String(s || '').replace(/\s+/g, ' ').trim();
  const m = s.match(/^.*?[.!?](\s|$)/);
  return (m ? m[0] : s).trim();
}

// Card blurb: prefer the curated one-liner, else the lead sentence of the brief's
// business overview, else the business model / market context — all real data,
// never invented. Keeps cards from reading "No description yet".
function blurbFor(profile) {
  const sd = (profile.shortDescription || '').trim();
  if (sd) return cap(sd);
  const bo = profile.brief && profile.brief.businessOverview;
  const lead = Array.isArray(bo) ? (bo[0] || '') : (bo || '');
  if (lead) return cap(firstSentence(lead));
  const bm = (profile.businessModel || '').trim();
  if (bm) return cap(firstSentence(bm));
  return cap((profile.marketContext || '').trim());
}

console.log('▶ Atlas site build');
fs.rmSync(OUT, { recursive: true, force: true });

// ── Scan every company once. Record brief SOURCE paths; copy per-view later. ──
const companies = [];
const ids = fs.existsSync(DATA)
  ? fs.readdirSync(DATA, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name)
  : [];

for (const id of ids.sort()) {
  const profile = readJSON(path.join(DATA, id, 'profile.json'));
  if (!profile) continue;

  const runsDir = path.join(DATA, id, 'runs');
  const runs = [];
  if (fs.existsSync(runsDir)) {
    const dates = fs.readdirSync(runsDir, { withFileTypes: true })
      .filter((d) => d.isDirectory()).map((d) => d.name).sort().reverse(); // newest first
    for (const date of dates) {
      const rdir = path.join(runsDir, date);
      const files = fs.readdirSync(rdir);
      const chosen = pickBrief(files.filter((f) => /\.html$/i.test(f)), id);
      if (!chosen) continue;
      const pdfs = files.filter((f) => /\.pdf$/i.test(f));
      const pdf = pdfs.find((f) => f.toLowerCase().includes(id.toLowerCase())) || pdfs[0];
      runs.push({
        date,
        srcHtml: path.join(rdir, chosen),
        srcPdf: pdf ? path.join(rdir, pdf) : null,
        href: `briefs/${id}/${date}.html`,
        pdf: pdf ? `briefs/${id}/${date}.pdf` : null,
      });
    }
  }

  companies.push({
    id,
    name: profile.name || id,
    ticker: profile.ticker || null,
    isPublic: !!(profile.ticker && /^[A-Z.]{1,6}$/.test(profile.ticker)),
    shortDescription: blurbFor(profile),
    verticals: Array.isArray(profile.verticals) ? profile.verticals : [],
    sectors: sectorsFor(Array.isArray(profile.verticals) ? profile.verticals : []),
    website: profile.website || null,
    domain: cleanDomain(profile),
    faviconUrl: explicitFavicon(profile),
    isStarred: !!profile.isStarred,
    latestRunDate: runs.length ? runs[0].date : (profile.lastRunDate || null),
    runs,
  });
}

// Starred first, then most-recent run first.
companies.sort((a, b) =>
  (Number(b.isStarred) - Number(a.isStarred)) ||
  String(b.latestRunDate || '').localeCompare(String(a.latestRunDate || '')));

// ── Emit one view: copy its briefs, write its manifest + the shared template. ──
function emitView(outDir, list, opts = {}) {
  ensureDir(path.join(outDir, 'briefs'));
  for (const c of list) {
    for (const r of c.runs) {
      ensureDir(path.join(outDir, 'briefs', c.id));
      // The brief's version-history links are written relative to the runs/<date>/ database
      // layout (../<date>/<id>_brief_<date>.html). On the site every version sits flat in
      // briefs/<id>/, so a sibling version is just <date>.html — rewrite the links to match.
      const html = fs.readFileSync(r.srcHtml, 'utf8')
        .replace(/href="\.\.\/(\d{4}-\d{2}-\d{2})\/[^"]*\.html"/g, 'href="$1.html"')
        // Inject Vercel Web Analytics into the published copy only — the raw brief in
        // data-dumps/ stays self-contained (its PDF source makes no external calls).
        .replace('</head>', `${ANALYTICS_TAG}</head>`);
      fs.writeFileSync(path.join(outDir, 'briefs', c.id, `${r.date}.html`), html);
      if (r.srcPdf) fs.copyFileSync(r.srcPdf, path.join(outDir, 'briefs', c.id, `${r.date}.pdf`));
    }
  }
  // Published manifest carries only the web-facing run fields (no source paths).
  const clean = list.map((c) => ({
    ...c,
    runs: c.runs.map(({ date, href, pdf }) => ({ date, href, pdf })),
  }));
  const manifest = {
    generatedAt: new Date().toISOString(),
    demo: !!opts.demo,
    count: clean.length,
    latestRunDate: clean.reduce((m, c) => (c.latestRunDate && c.latestRunDate > m ? c.latestRunDate : m), ''),
    companies: clean,
  };
  fs.writeFileSync(path.join(outDir, 'index.json'), JSON.stringify(manifest, null, 2));
  fs.copyFileSync(TEMPLATE, path.join(outDir, 'index.html'));
  return clean.reduce((n, c) => n + c.runs.length, 0);
}

// Public demo = the most recently updated companies on the full site (no curated list).
const demo = [...companies]
  .sort((a, b) => String(b.latestRunDate || '').localeCompare(String(a.latestRunDate || '')))
  .slice(0, DEMO_COUNT);

ensureDir(OUT);
const fullBriefs = emitView(path.join(OUT, 'full'), companies);              // /full → gated, everything
const demoBriefs = emitView(OUT, demo, { demo: true });                      // /     → public demo

console.log(`✓ demo: ${demo.length} companies, ${demoBriefs} briefs → site/dist  (public)`);
console.log(`✓ full: ${companies.length} companies, ${fullBriefs} briefs → site/dist/full  (gated)`);
