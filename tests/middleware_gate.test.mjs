// Standalone Node test for the /full edge gate (middleware.js).
//
// The most security-critical, fully-testable piece of Layer 2 auth. There is no live
// Supabase project, so we forge HS256 JWTs with a known test secret and fire REAL
// Request objects at the REAL middleware export. This proves the JWT verification chain
// end to end WITHOUT any network — the only thing left for the live project is the actual
// Google/Supabase OAuth handshake.
//
// Run: node tests/middleware_gate.test.mjs   (exits non-zero on any failure)
//
// Covered:
//   • CRITICAL: anon-role and service_role tokens (both validly signed with the project
//     secret — the anon key is PUBLIC) must be REJECTED; only role:"authenticated" passes.
//   • Signature: forged signature (wrong secret), tampered payload → reject.
//   • Claims: expired (exp), not-yet-valid is allowed only if you choose (we test exp),
//     missing/garbage cookie, missing role, bad aud.
//   • Algorithm confusion: alg:"none" and alg:"HS512" → reject.
//   • base64url: padding handled, malformed base64url → reject (no throw).
//   • Cookie parsing: token byte-for-byte round-trips; other cookies alongside sb_at.
//   • Fallback: fully open when SUPABASE_JWT_SECRET is not set (legacy password gate removed).

import crypto from 'node:crypto';

const SECRET = 'test-jwt-secret-please-ignore-0123456789';
const MW_URL = new URL('../middleware.js', import.meta.url);

// ── tiny JWT forge (HS256 by default) ──────────────────────────────────────────
const b64url = (buf) =>
  Buffer.from(buf).toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');

function sign(headerBytes, payloadBytes, secret, alg = 'sha256') {
  return b64url(crypto.createHmac(alg, secret).update(`${headerBytes}.${payloadBytes}`).digest());
}

function forge(payload, { secret = SECRET, alg = 'HS256', hmac = 'sha256', sig } = {}) {
  const h = b64url(JSON.stringify({ alg, typ: 'JWT' }));
  const p = b64url(JSON.stringify(payload));
  const s = sig !== undefined ? sig : sign(h, p, secret, hmac);
  return `${h}.${p}.${s}`;
}

const now = () => Math.floor(Date.now() / 1000);
// A realistic Supabase user access token: role "authenticated", aud "authenticated".
const userPayload = (over = {}) => ({
  iss: 'https://demo-project.supabase.co/auth/v1',
  sub: '11111111-1111-1111-1111-111111111111',
  aud: 'authenticated',
  role: 'authenticated',
  email: 'user@example.com',
  exp: now() + 3600,
  iat: now(),
  ...over,
});
// The PUBLIC anon key shape (this is what's baked into config.js and shipped to browsers).
const anonPayload = (over = {}) => ({
  iss: 'supabase',
  ref: 'demo-project',
  role: 'anon',
  aud: 'authenticated',
  exp: now() + 10 * 365 * 24 * 3600,
  iat: now(),
  ...over,
});
const servicePayload = (over = {}) => ({ ...anonPayload(), role: 'service_role', ...over });

// ── test harness ────────────────────────────────────────────────────────────────
let pass = 0, fail = 0;
const fails = [];
function check(name, cond) {
  if (cond) { pass++; }
  else { fail++; fails.push(name); console.log(`  ✗ ${name}`); }
}

// Build a GET /briefs/x.html request carrying the given cookie header (or none). Atlas serves
// coverage at the ROOT now (alfred-analyst proxies /atlas/* here), so briefs live at /briefs/….
function req(cookie, { url = 'https://atlas-private.vercel.app/briefs/SNOW/2026-01-01.html', method = 'GET', body } = {}) {
  const headers = {};
  if (cookie) headers.cookie = cookie;
  const init = { method, headers };
  if (body !== undefined) { init.body = body; headers['content-type'] = 'application/x-www-form-urlencoded'; }
  return new Request(url, init);
}

// Was the response an "allow" (middleware returned undefined → request passes through)?
const isAllowed = (res) => res === undefined || res === null;
// Was it a redirect to the front-door login (alfred-analyst)? The Atlas gate sends misses to an
// ABSOLUTE LOGIN_URL/login, never a local /login (that would loop through the proxy).
function isLoginRedirect(res) {
  if (!res || typeof res.status !== 'number') return false;
  if (res.status !== 302 && res.status !== 307) return false;
  const loc = res.headers.get('location') || '';
  return /^https?:\/\/[^/]+\/login\b/.test(loc);
}

// Load middleware fresh with a given env (module is import-cached, but it reads process.env
// at call time, so we can flip env between calls without re-importing).
const { default: middleware } = await import(MW_URL);

async function withEnv(env, fn) {
  const saved = {};
  for (const k of ['SUPABASE_JWT_SECRET']) {
    saved[k] = process.env[k];
    if (env[k] === undefined) delete process.env[k];
    else process.env[k] = env[k];
  }
  try { return await fn(); }
  finally {
    for (const k of Object.keys(saved)) {
      if (saved[k] === undefined) delete process.env[k];
      else process.env[k] = saved[k];
    }
  }
}

console.log('▶ middleware Alfred app gate — JWT verification + walled paths');

await withEnv({ SUPABASE_JWT_SECRET: SECRET }, async () => {
  // ── 1. CRITICAL: privilege checks ──
  const authd = forge(userPayload());
  check('authenticated user token is ALLOWED', isAllowed(await middleware(req(`sb_at=${authd}`))));

  const anon = forge(anonPayload());
  check('PUBLIC anon-key token is REJECTED (no bypass)', isLoginRedirect(await middleware(req(`sb_at=${anon}`))));

  const service = forge(servicePayload());
  check('service_role token is REJECTED', isLoginRedirect(await middleware(req(`sb_at=${service}`))));

  check('token with NO role claim is REJECTED',
    isLoginRedirect(await middleware(req(`sb_at=${forge(userPayload({ role: undefined }))}`))));

  check('token with empty role is REJECTED',
    isLoginRedirect(await middleware(req(`sb_at=${forge(userPayload({ role: '' }))}`))));

  // ── 2. Signature / tamper ──
  check('forged signature (wrong secret) is REJECTED',
    isLoginRedirect(await middleware(req(`sb_at=${forge(userPayload(), { secret: 'wrong-secret' })}`))));

  // Tamper the payload but keep the original signature.
  const good = forge(userPayload());
  const [h, , sig] = good.split('.');
  const tamperedPayload = b64url(JSON.stringify(userPayload({ email: 'attacker@evil.com', sub: 'x' })));
  check('tampered payload (orig signature) is REJECTED',
    isLoginRedirect(await middleware(req(`sb_at=${h}.${tamperedPayload}.${sig}`))));

  // ── 3. Expiry ──
  check('expired token (exp in past) is REJECTED',
    isLoginRedirect(await middleware(req(`sb_at=${forge(userPayload({ exp: now() - 10 }))}`))));
  check('token expiring far in the future is ALLOWED',
    isAllowed(await middleware(req(`sb_at=${forge(userPayload({ exp: now() + 99999 }))}`))));

  // ── 4. Algorithm confusion ──
  check('alg:"none" is REJECTED',
    isLoginRedirect(await middleware(req(`sb_at=${forge(userPayload(), { alg: 'none', sig: '' })}`))));
  check('alg:"none" with payload-only (no sig) is REJECTED', await (async () => {
    const hn = b64url(JSON.stringify({ alg: 'none', typ: 'JWT' }));
    const pn = b64url(JSON.stringify(userPayload()));
    return isLoginRedirect(await middleware(req(`sb_at=${hn}.${pn}.`)));
  })());
  // HS512 forged with the same secret but declared HS512 — must be rejected (we only verify HS256).
  check('alg:"HS512" is REJECTED (algorithm confusion)',
    isLoginRedirect(await middleware(req(`sb_at=${forge(userPayload(), { alg: 'HS512', hmac: 'sha512' })}`))));

  // ── 5. aud sanity ──
  check('wrong aud is REJECTED',
    isLoginRedirect(await middleware(req(`sb_at=${forge(userPayload({ aud: 'some-other-audience' }))}`))));

  // ── 6. Malformed / missing cookie ──
  check('no cookie at all → redirect', isLoginRedirect(await middleware(req(null))));
  check('empty sb_at → redirect', isLoginRedirect(await middleware(req('sb_at='))));
  check('garbage (not a JWT) → redirect', isLoginRedirect(await middleware(req('sb_at=not.a.jwt'))));
  check('two-part token → redirect', isLoginRedirect(await middleware(req('sb_at=onlytwo.parts'))));
  check('malformed base64url payload does not throw → redirect',
    isLoginRedirect(await middleware(req(`sb_at=${b64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }))}.@@@not-b64@@@.sig`))));

  // ── 7. base64url padding correctness ──
  // Force a payload whose base64 needs 1 and 2 pad chars to confirm decoding handles both.
  for (const padCase of ['p', 'pp', 'ppp']) {
    const tok = forge(userPayload({ email: padCase + '@example.com' }));
    check(`base64url padding handled (${padCase}) → ALLOWED`, isAllowed(await middleware(req(`sb_at=${tok}`))));
  }

  // ── 8. Cookie parsing: token survives byte-for-byte alongside other cookies ──
  const tok = forge(userPayload());
  check('sb_at parsed correctly when other cookies present (before)',
    isAllowed(await middleware(req(`other=foo; sb_at=${tok}; another=bar`))));
  check('sb_at parsed correctly when listed last',
    isAllowed(await middleware(req(`a=1; b=2; sb_at=${tok}`))));
  // A cookie value containing '=' before sb_at must not corrupt parsing.
  check('cookie with "=" in another value does not break sb_at',
    isAllowed(await middleware(req(`weird=a=b=c; sb_at=${tok}`))));

  // ── 8b. Verify-only gate: auth assets are OPEN; coverage paths are gated → front-door login ──
  const U = (p) => 'https://atlas-private.vercel.app' + p;
  for (const open of ['/config.js', '/auth.js', '/vendor/supabase.js']) {
    check(`open asset ${open} is NOT gated (no cookie)`,
      isAllowed(await middleware(req(null, { url: U(open) }))));
  }
  for (const gated of ['/', '/briefs/SNOW/2026-01-01.html']) {
    check(`gated path ${gated} without cookie → front-door login`,
      isLoginRedirect(await middleware(req(null, { url: U(gated) }))));
    check(`gated path ${gated} WITH valid user token → ALLOWED`,
      isAllowed(await middleware(req(`sb_at=${tok}`, { url: U(gated) }))));
  }
  // The redirect carries the proxied next= so login returns the user into the tool.
  const r = await middleware(req(null, { url: U('/briefs/SNOW/2026-01-01.html') }));
  check('redirect next= points back through the /atlas proxy',
    /next=%2Fatlas%2Fbriefs/.test(r.headers.get('location') || ''));
});

// ── 9. Open: no JWT secret configured ──
await withEnv({}, async () => {
  check('no env configured → site is OPEN (allow)', isAllowed(await middleware(req(null))));
});

// ── summary ──
console.log(`\n${fail === 0 ? '✓ PASS' : '✗ FAIL'} — ${pass} passed, ${fail} failed`);
if (fail) { console.log('Failed:', fails.join(' | ')); process.exit(1); }
