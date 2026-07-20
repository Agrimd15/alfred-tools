// Gate for the private /full coverage view (Vercel Edge Middleware).
//
// One gating mode: ACCOUNTS. When SUPABASE_JWT_SECRET is set, /full requires a
// signed-in user: the browser mirrors its Supabase access token into an `sb_at` cookie
// (see site/template/auth.js), and this middleware verifies that JWT's HMAC-SHA256
// signature + expiry here at the edge. No valid token → redirect to the front-door login.
// This is the real protection: brief files are static on the CDN, so the check must run
// server-side BEFORE the file is served, not in browser JS.
//
// If SUPABASE_JWT_SECRET is not set, the site is fully open (the public demo at / is never
// gated either way). The legacy shared-password gate (SITE_PASSWORD) was removed 2026-07-20.
// Everything travels over HTTPS only.

export const config = {
  // This is the Atlas tool deployment. Gate the coverage browser (/) + every brief, EXCEPT the
  // auth assets the coverage page loads (config.js, auth.js, vendor/supabase.js) and Vercel's
  // /_vercel/*. Normal traffic arrives pre-authed via alfred-analyst's front-door gate + proxy;
  // this gate is defense-in-depth for direct atlas-private.vercel.app access. Sign-in is NOT here
  // — misses redirect to the front-door login (alfred-analyst).
  matcher: ['/((?!_vercel|config\\.js|auth\\.js|vendor).*)'],
};

// Where sign-in lives (the Alfred front door). Misses redirect here, never to a local /login —
// that would loop through the proxy (see alfred-analyst/README). Overridable per deployment.
const LOGIN_ORIGIN = process.env.LOGIN_URL || 'https://alfred-analyst.com';

// Open paths — never gated, even on a direct middleware call (keeps the matcher and the unit
// test in agreement). Matches /config.js, /auth.js, /vendor/*, /_vercel/*.
const OPEN_PATH = /^\/(config\.js$|auth\.js$|vendor\/|_vercel\/)/;

const SB_COOKIE = 'sb_at';

const enc = new TextEncoder();

function parseCookies(header) {
  const out = {};
  (header || '').split(/;\s*/).forEach((p) => {
    const i = p.indexOf('=');
    if (i > 0) out[p.slice(0, i)] = p.slice(i + 1);
  });
  return out;
}

// base64url → bytes (atob is available in the edge runtime).
function b64urlToBytes(s) {
  s = s.replace(/-/g, '+').replace(/_/g, '/');
  const pad = s.length % 4;
  if (pad) s += '='.repeat(4 - pad);
  const bin = atob(s);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

// Verify a Supabase HS256 JWT and confirm it represents a genuine signed-in END USER.
//
// CRITICAL: a valid signature is NOT sufficient. Supabase's anon key and service_role key
// are themselves JWTs signed with this same SUPABASE_JWT_SECRET (role "anon" / "service_role"),
// and the anon key is PUBLIC — it's baked into the site's config.js and shipped to every
// browser. If we accepted any validly-signed token, anyone could paste the public anon key
// into the sb_at cookie and walk straight past the gate. So we additionally require
// role === "authenticated" (the role Supabase stamps on a real user session) and a sane
// aud, on top of signature + exp.
//
// Returns the decoded payload when valid AND it's an authenticated user, otherwise null.
async function verifyJWT(token, secret) {
  const parts = token.split('.');
  if (parts.length !== 3) return null;
  const [h, p, sig] = parts;
  let header;
  try { header = JSON.parse(new TextDecoder().decode(b64urlToBytes(h))); } catch { return null; }
  if (header.alg !== 'HS256') return null; // only the shared-secret algo is verified here
  try {
    const key = await crypto.subtle.importKey(
      'raw', enc.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify']);
    const ok = await crypto.subtle.verify('HMAC', key, b64urlToBytes(sig), enc.encode(`${h}.${p}`));
    if (!ok) return null;
    const payload = JSON.parse(new TextDecoder().decode(b64urlToBytes(p)));

    // Must be a genuine authenticated user — NOT the public anon key or the service_role key.
    if (payload.role !== 'authenticated') return null;
    // Supabase user tokens carry aud "authenticated" (a single string, or an array that
    // includes it). Reject anything else.
    const aud = payload.aud;
    const audOk = aud === 'authenticated' || (Array.isArray(aud) && aud.includes('authenticated'));
    if (!audOk) return null;
    // A user session must identify the user.
    if (!payload.sub) return null;
    // Expiry is required and must be in the future.
    const nowSec = Math.floor(Date.now() / 1000);
    if (typeof payload.exp !== 'number' || nowSec >= payload.exp) return null; // expired/missing

    return payload;
  } catch {
    return null;
  }
}

// ── Entry ─────────────────────────────────────────────────────────────────────
export default async function middleware(request) {
  const jwtSecret = process.env.SUPABASE_JWT_SECRET;

  // Never gate the sign-in page or the assets it loads (defensive — the matcher already
  // excludes them, but a direct call / the unit test relies on this too).
  const { pathname, search } = new URL(request.url);
  if (OPEN_PATH.test(pathname)) return;

  // Accounts gate. Verify the Supabase session cookie.
  if (jwtSecret) {
    const token = parseCookies(request.headers.get('cookie'))[SB_COOKIE];
    if (token && (await verifyJWT(token, jwtSecret))) return; // authorized
    // Send unauthed (direct-access) visitors to the front-door login. `next` is the proxied
    // path so they land back in the tool: e.g. /briefs/x → /atlas/briefs/x on the front door.
    const next = '/atlas' + pathname + search;
    return Response.redirect(`${LOGIN_ORIGIN}/login?next=` + encodeURIComponent(next), 302);
  }

  // Not configured — site is open.
  return;
}
