
import express from 'express';
import session from 'express-session';
import crypto from 'crypto';

// Manual OIDC helpers (discovery, PKCE, token exchange) using global fetch
let oidcMetadata = null;
async function discoverMetadata() {
  if (oidcMetadata) return oidcMetadata;
  if (!issuerUrl) throw new Error('OAUTH_ISSUER not configured');
  const base = issuerUrl.replace(/\/$/, '');
  const candidates = [
    base + '/.well-known/openid-configuration',
    base + '/realms/master/.well-known/openid-configuration',
    base + '/auth/realms/master/.well-known/openid-configuration',
  ];
  let lastErr = null;
  for (const url of candidates) {
    try {
      console.log('Trying OIDC discovery URL:', url);
      const res = await fetch(url);
      if (!res.ok) {
        lastErr = new Error(`Not OK (${res.status}) ${res.statusText}`);
        console.warn('Discovery failed for', url, res.status, res.statusText);
        continue;
      }
      oidcMetadata = await res.json();
      console.log('Discovered OIDC metadata at', url);
      return oidcMetadata;
    } catch (err) {
      lastErr = err;
      console.warn('Error fetching discovery URL', url, err && err.message ? err.message : err);
    }
  }
  throw new Error('Failed to fetch OIDC metadata: ' + (lastErr && lastErr.message ? lastErr.message : 'unknown'));
}

function base64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
}

function generateCodeVerifier() {
  return base64url(crypto.randomBytes(32));
}

function generateCodeChallenge(verifier) {
  return base64url(crypto.createHash('sha256').update(verifier).digest());
}

function decodeJwt(token) {
  try {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    const payload = parts[1];
    const padded = payload.padEnd(Math.ceil(payload.length / 4) * 4, '=');
    const json = Buffer.from(padded.replace(/-/g, '+').replace(/_/g, '/'), 'base64').toString('utf8');
    return JSON.parse(json);
  } catch (e) {
    return null;
  }
}
import dotenv from 'dotenv';
import sirv from 'sirv';
import path from 'path';

// Load .env
dotenv.config({ path: path.resolve(process.cwd(), '.env') });


const app = express();
const port = process.env.PORT || 3000;

// Session middleware
app.use(session({
  secret: 'svelte-portal-secret',
  resave: false,
  saveUninitialized: false,
  cookie: { secure: false, httpOnly: true, maxAge: 24 * 60 * 60 * 1000 }
}));

const clientId = process.env.OAUTH_CLIENT_ID;
const clientSecret = process.env.OAUTH_CLIENT_SECRET;
const issuerUrl = process.env.OAUTH_ISSUER;
const redirectUri = process.env.OAUTH_REDIRECT_URI || `http://localhost:${port}/auth/callback`;

let client; // kept for compatibility but not used when using manual discovery

// Serve static files
app.use(sirv('public', { dev: false }));

// OAuth2 login endpoint

app.get('/auth/login', async (req, res) => {
  try {
    const meta = await discoverMetadata();
    const code_verifier = generateCodeVerifier();
    const code_challenge = generateCodeChallenge(code_verifier);
    req.session.code_verifier = code_verifier;
    const params = new URLSearchParams({
      client_id: clientId,
      response_type: 'code',
      scope: 'openid profile email',
      redirect_uri: redirectUri,
      code_challenge: code_challenge,
      code_challenge_method: 'S256',
    });
    const authUrl = meta.authorization_endpoint + '?' + params.toString();
    return res.redirect(authUrl);
  } catch (err) {
    console.error('Login error:', err && err.message ? err.message : err);
    return res.status(500).send('Login error: ' + (err.message || 'unknown'));
  }
});

// Health route
app.get('/healthz', (req, res) => {
  res.json({ ok: true, oidc: !!client });
});

// OAuth2 callback endpoint

app.get('/auth/callback', async (req, res) => {
  try {
    const meta = await discoverMetadata();
    const code = req.query.code;
    const code_verifier = req.session?.code_verifier;
    if (!code) return res.status(400).send('Missing code');
    if (!code_verifier) return res.status(400).send('Missing code_verifier in session');

    const tokenRes = await fetch(meta.token_endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        code: code,
        redirect_uri: redirectUri,
        client_id: clientId,
        client_secret: clientSecret || '',
        code_verifier: code_verifier,
      }),
    });
    if (!tokenRes.ok) {
      const t = await tokenRes.text();
      console.error('Token endpoint error:', t);
      return res.status(500).send('Token exchange failed');
    }
    const tokenJson = await tokenRes.json();
    req.session.tokenSet = tokenJson;
    const claims = tokenJson.id_token ? decodeJwt(tokenJson.id_token) : tokenJson;
    req.session.claims = claims;
    return res.redirect('/');
  } catch (err) {
    console.error('Callback error:', err && err.message ? err.message : err);
    return res.status(500).send('OAuth callback error: ' + (err.message || 'unknown'));
  }
});

// Logout endpoint
app.get('/auth/logout', (req, res) => {
  req.session.destroy(() => {
    res.redirect('/');
  });
});

// API endpoint to get user claims
app.get('/api/user', (req, res) => {
  if (req.session && req.session.claims) {
    // include access token when present so the portal can display it (for debugging/dev)
    const tokenSet = req.session.tokenSet || {};
    res.json({ authenticated: true, claims: req.session.claims, access_token: tokenSet.access_token || null });
  } else {
    res.json({ authenticated: false });
  }
});

// API endpoint to return configured app URLs
app.get('/api/apps', (req, res) => {
  const apps = [
    { id: 'django', name: 'Django App', url: process.env.APP_DJANGO_URL || 'http://localhost:8000' },
    { id: 'dotnet', name: '.NET 8', url: process.env.APP_DOTNET_URL || 'http://localhost:5000' },
    { id: 'php', name: 'PHP', url: process.env.APP_PHP_URL || 'http://localhost:8080' },
  ];
  res.json({ apps });
});

// Start server
app.listen(port, () => {
  console.log(`Svelte portal running on http://localhost:${port}`);
});
