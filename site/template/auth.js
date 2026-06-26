// Alfred auth — client-side Supabase session + cookie mirror for edge gating.
//
// supabase-js keeps the session in localStorage (so refresh + PKCE just work). The edge
// middleware that walls the app can only read COOKIES, so we additionally mirror just the
// access-token JWT into a small `sb_at` cookie on every auth state change. Middleware
// verifies that JWT's signature + expiry. The refresh token never leaves localStorage.
//
// Config (project URL + anon key) is injected at build time into window.ALFRED_SUPABASE by
// config.js. If it's absent (no env at build, or Supabase not set up yet) this module is a
// no-op and the page renders unauthenticated — with no JWT secret set, middleware stays open.
(function () {
  const cfg = window.ALFRED_SUPABASE || {};
  const COOKIE = 'sb_at';

  if (!cfg.url || !cfg.anonKey || !window.supabase) {
    document.documentElement.classList.add('auth-unconfigured');
    return; // auth not configured — leave the page as-is
  }

  const client = window.supabase.createClient(cfg.url, cfg.anonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true, // exchanges the ?code=… on the OAuth return
      flowType: 'pkce',
    },
  });
  window.alfredAuth = client;

  const secure = location.protocol === 'https:' ? '; Secure' : '';

  function setCookie(token, maxAgeSec) {
    document.cookie = `${COOKIE}=${token}; Path=/; SameSite=Lax; Max-Age=${maxAgeSec}${secure}`;
  }
  function clearCookie() {
    document.cookie = `${COOKIE}=; Path=/; SameSite=Lax; Max-Age=0${secure}`;
  }

  // Mirror the current session's access token into the cookie (or clear it). The cookie
  // outlives the ~1h token TTL; middleware enforces the real `exp`, and an active browser
  // refreshes the token (TOKEN_REFRESHED) which re-stamps the cookie.
  function mirror(session) {
    if (session && session.access_token) setCookie(session.access_token, 60 * 60 * 24 * 7);
    else clearCookie();
  }
  window.alfredMirror = mirror; // login.html sets the cookie before forwarding to the target

  function renderHeader(user) {
    const slot = document.getElementById('auth-slot');
    if (!slot) return;
    if (user) {
      const label = user.email || 'Signed in';
      slot.innerHTML =
        `<span class="auth-user" title="${label}">${label}</span>` +
        `<button type="button" class="auth-btn" id="auth-signout">Sign out</button>`;
      const b = document.getElementById('auth-signout');
      if (b) b.addEventListener('click', async () => {
        await client.auth.signOut();
        clearCookie();
        location.href = '/'; // back to the Alfred home (same origin via the proxy)
      });
    } else {
      slot.innerHTML = `<a class="auth-btn" href="/login">Sign in</a>`;
    }
  }

  client.auth.onAuthStateChange((event, session) => {
    mirror(session);
    renderHeader(session ? session.user : null);
  });

  // On load, reflect the current (possibly just-refreshed) session into the cookie + header.
  client.auth.getSession().then(({ data }) => {
    mirror(data.session);
    renderHeader(data.session ? data.session.user : null);
  });

  // Note: sign-IN happens on the Alfred front door (alfred-analyst). This module only keeps the
  // session/cookie fresh and renders the header + sign-out on the coverage page.
})();
