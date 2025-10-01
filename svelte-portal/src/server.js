
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
const port = 3000;

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

const DJANGO_JWT_SNIPPET = `class KeycloakJWTAuthentication(authentication.BaseAuthentication):
  """
  JWT authentication using Keycloak public key
  """

  def __init__(self):
    self.keycloak_public_key = None
    self.key_cache_timeout = 3600  # Cache for 1 hour
    self.last_key_fetch = 0

  def get_keycloak_public_key(self):
    """
    Fetch and cache Keycloak public key
    """
    import time
    current_time = time.time()

    # Return cached key if still valid
    if (self.keycloak_public_key and
      current_time - self.last_key_fetch < self.key_cache_timeout):
      return self.keycloak_public_key

    try:
      # Fetch JWKS from Keycloak
      response = requests.get(settings.KEYCLOAK_CERT_URL, timeout=10)
      response.raise_for_status()
      jwks = response.json()

      # Get the first key (usually there's only one)
      if 'keys' in jwks and len(jwks['keys']) > 0:
        key_data = jwks['keys'][0]

        # Store the JWKS for use with python-jose
        self.keycloak_public_key = jwks
        self.last_key_fetch = current_time

        return self.keycloak_public_key
      else:
        raise exceptions.AuthenticationFailed('No keys found in JWKS')

    except requests.RequestException as e:
      raise exceptions.AuthenticationFailed(f'Failed to fetch Keycloak public key: {str(e)}')
    except Exception as e:
      raise exceptions.AuthenticationFailed(f'Error processing Keycloak public key: {str(e)}')

  def authenticate(self, request):
    """
    Authenticate the request and return a two-tuple of (user, token).
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION')

    if not auth_header:
      return None

    try:
      # Extract token from "Bearer <token>"
      prefix, token = auth_header.split(' ', 1)
      if prefix.lower() != 'bearer':
        return None
    except ValueError:
      return None

    try:
      # Get Keycloak JWKS
      jwks = self.get_keycloak_public_key()

      # Decode and verify JWT token using JWKS
      payload = jose_jwt.decode(
        token,
        jwks,  # Pass JWKS directly
        algorithms=['RS256'],
        audience=None,  # Skip audience validation for now
        options={
          'verify_aud': False,  # Skip audience verification
          'verify_exp': True,   # Verify expiration
          'verify_iat': True,   # Verify issued at
          'verify_nbf': True,   # Verify not before
        }
      )

      # Create user from token payload
      user = KeycloakUser(payload)

      return (user, token)

    except ExpiredSignatureError:
      raise exceptions.AuthenticationFailed('Token has expired')
    except JWTClaimsError as e:
      raise exceptions.AuthenticationFailed(f'Invalid token claims: {str(e)}')
    except JWTError as e:
      raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
    except Exception as e:
      raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')

  def authenticate_header(self, request):
    """
    Return a string to be used as the value of the 'WWW-Authenticate'
    header in a '401 Unauthenticated' response.
    """
    return 'Bearer realm="keycloak"'`;

const DOTNET_JWT_SNIPPET = `// Middleware นี้ทำหน้าที่ตรวจสอบ JWT จาก Keycloak ก่อนให้คำขอเข้าสู่ API หลัก
public sealed class KeycloakJwtMiddleware
{
  public const string TokenPayloadKey = "KeycloakTokenPayload";

  private readonly RequestDelegate _next;
  private readonly ILogger<KeycloakJwtMiddleware> _logger;
  private readonly KeycloakJwtValidator _validator;

  private static readonly string[] _anonymousPrefixes =
  {
    "/api/health",
    "/health",
    "/_health"
  };

  public KeycloakJwtMiddleware(RequestDelegate next, ILogger<KeycloakJwtMiddleware> logger, KeycloakJwtValidator validator)
  {
    _next = next;
    _logger = logger;
    _validator = validator;
  }

  public async Task InvokeAsync(HttpContext context)
  {
    // อนุญาตให้คำขอแบบ OPTIONS (preflight) ผ่านไปโดยไม่ตรวจ JWT เพื่อรองรับ CORS
    if (HttpMethods.IsOptions(context.Request.Method))
    {
      await _next(context);
      return;
    }

    // ตรวจสอบว่าเส้นทางนี้อยู่ในรายการยกเว้นที่ไม่ต้องตรวจสอบสิทธิ์หรือไม่
    if (ShouldBypass(context.Request.Path))
    {
      await _next(context);
      return;
    }

    // ดึงค่า Authorization header แล้วตรวจว่ามี Bearer token หรือไม่
    var authHeader = context.Request.Headers.Authorization.FirstOrDefault();
    if (string.IsNullOrWhiteSpace(authHeader) || !authHeader.StartsWith("Bearer ", StringComparison.OrdinalIgnoreCase))
    {
      await WriteUnauthorizedAsync(context, "Missing bearer token.");
      return;
    }

    // ตัดคำว่า "Bearer" ออกแล้วเก็บเฉพาะตัว token จริง ๆ
    var token = authHeader["Bearer ".Length..].Trim();
    if (string.IsNullOrEmpty(token))
    {
      await WriteUnauthorizedAsync(context, "Empty bearer token.");
      return;
    }

    try
    {
      // ส่ง token ไปให้ตัว Validator ตรวจสอบลายเซ็น วันหมดอายุ และข้อมูลอื่น ๆ
      var result = await _validator.ValidateAsync(token, context.RequestAborted).ConfigureAwait(false);
      // หากผ่านการตรวจสอบ ให้ผูก ClaimsPrincipal กับ HttpContext.User เพื่อใช้ต่อใน endpoint
      context.User = result.Principal;
      // เก็บ payload ดิบไว้ใน context.Items เผื่อ endpoint ภายหลังต้องใช้ข้อมูล claim เพิ่มเติม
      context.Items[TokenPayloadKey] = result.Payload;
      await _next(context);
    }
    catch (Exception ex)
    {
      // ถ้า JWT ตรวจไม่ผ่าน ให้คืน 401 พร้อมรายละเอียด และบันทึก log ไว้
      _logger.LogWarning(ex, "JWT validation failed.");
      await WriteUnauthorizedAsync(context, ex.Message);
    }
  }

  private static bool ShouldBypass(PathString path)
  {
    // ถ้าไม่มี path ให้ถือว่ายกเว้นไปเลย (เช่น คำขอวิ่งมาที่ root)
    if (!path.HasValue)
    {
      return true;
    }

    foreach (var prefix in _anonymousPrefixes)
    {
      // ถ้า path ขึ้นต้นด้วย prefix ที่อนุญาต ก็ผ่านโดยไม่ต้องตรวจ JWT
      if (path.StartsWithSegments(prefix, StringComparison.OrdinalIgnoreCase))
      {
        return true;
      }
    }

    return false;
  }

  private static Task WriteUnauthorizedAsync(HttpContext context, string message)
  {
    // สร้าง response แบบ JSON ตอบกลับให้ client ทราบว่าไม่ผ่านการตรวจสอบสิทธิ์
    context.Response.StatusCode = StatusCodes.Status401Unauthorized;
    context.Response.ContentType = "application/json";
    var payload = JsonSerializer.Serialize(new
    {
      error = "Unauthorized",
      detail = message
    });
    return context.Response.WriteAsync(payload);
  }
}

// ตัว Validator สำหรับตรวจสอบลายเซ็นและข้อมูลภายใน JWT ที่ออกโดย Keycloak
public sealed class KeycloakJwtValidator
{
  private readonly KeycloakJwksCache _jwksCache;
  private readonly KeycloakJwtOptions _options;

  public KeycloakJwtValidator(KeycloakJwksCache jwksCache, KeycloakJwtOptions options)
  {
    _jwksCache = jwksCache;
    _options = options;
  }

  public async Task<KeycloakValidationResult> ValidateAsync(string token, CancellationToken cancellationToken = default)
  {
    // ใช้ JwtSecurityTokenHandler ของ .NET ในการตรวจสอบความถูกต้องของ token
    var handler = new JwtSecurityTokenHandler();
    var validationParameters = await BuildValidationParametersAsync(cancellationToken).ConfigureAwait(false);

    // หากตรวจสอบผ่าน จะได้ ClaimsPrincipal และ security token กลับมา
    var principal = handler.ValidateToken(token, validationParameters, out var securityToken);
    if (securityToken is not JwtSecurityToken jwt)
    {
      throw new SecurityTokenException("Token is not a JWT.");
    }

    // เก็บ payload ของ JWT ที่ยังมีข้อมูลไว้เป็น dictionary เพื่อใช้งานต่อ
    var payload = jwt.Payload
      .Where(kvp => kvp.Value is not null)
      .ToDictionary(kvp => kvp.Key, kvp => kvp.Value);

    return new KeycloakValidationResult(principal, payload);
  }

  private async Task<TokenValidationParameters> BuildValidationParametersAsync(CancellationToken cancellationToken)
  {
    // ดึงชุดกุญแจสาธารณะ (JWKS) จาก cache เพื่อใช้ตรวจลายเซ็นของ token
    var keySet = await _jwksCache.GetKeySetAsync(cancellationToken).ConfigureAwait(false);

    // กำหนดกฎการตรวจสอบต่าง ๆ เช่น issuer, audience, วันหมดอายุ และลายเซ็น
    var parameters = new TokenValidationParameters
    {
      ValidateIssuer = !string.IsNullOrWhiteSpace(_options.Issuer),
      ValidIssuer = _options.Issuer,
      ValidateAudience = !string.IsNullOrWhiteSpace(_options.Audience),
      ValidAudience = _options.Audience,
      ValidateLifetime = true,
      RequireExpirationTime = true,
      RequireSignedTokens = true,
      ValidateIssuerSigningKey = true,
      IssuerSigningKeys = keySet.GetSigningKeys(),
      ClockSkew = TimeSpan.FromMinutes(2)
    };

    return parameters;
  }
}

public sealed record KeycloakValidationResult(ClaimsPrincipal Principal, IDictionary<string, object?> Payload);`;

const PHP_JWT_SNIPPET = `<?php
require __DIR__ . '/../vendor/autoload.php';

use Firebase\\JWT\\JWT;
use Firebase\\JWT\\JWK;

// ฟังก์ชันนี้ใช้ตรวจสอบ JWT ที่ Keycloak ออกให้
function verify_jwt(string $token): array
{
  static $cachedJwks = null;
  static $cachedAt = 0;

  $jwksUrl = $_ENV['KEYCLOAK_CERT_URL'] ?? '';
  if ($jwksUrl === '') {
    throw new RuntimeException('KEYCLOAK_CERT_URL environment variable is required.');
  }

  $cacheSeconds = (int) ($_ENV['KEYCLOAK_JWKS_CACHE_SECONDS'] ?? 3600);

  // ดึง JWKS จาก Keycloak แล้ว cache ไว้เพื่อลดการเรียกซ้ำ
  if ($cachedJwks === null || (time() - $cachedAt) >= $cacheSeconds) {
    $client = curl_init($jwksUrl);
    curl_setopt_array($client, [
      CURLOPT_RETURNTRANSFER => true,
      CURLOPT_TIMEOUT => 10,
      CURLOPT_FOLLOWLOCATION => true,
      CURLOPT_SSL_VERIFYPEER => false,
      CURLOPT_SSL_VERIFYHOST => false,
    ]);

    $response = curl_exec($client);
    if ($response === false) {
      $error = curl_error($client);
      curl_close($client);
      throw new RuntimeException('Failed to fetch JWKS: ' . $error);
    }

    $status = curl_getinfo($client, CURLINFO_RESPONSE_CODE);
    curl_close($client);

    if ($status < 200 || $status >= 300) {
      throw new RuntimeException('Failed to fetch JWKS: HTTP ' . $status);
    }

    $jwks = json_decode($response, true);
    if (!is_array($jwks) || !isset($jwks['keys'])) {
      throw new RuntimeException('Invalid JWKS payload.');
    }

    $cachedJwks = $jwks;
    $cachedAt = time();
  }

  // แปลง JWKS เป็น key สำหรับ firebase/php-jwt (รองรับ RS256)
  $keys = JWK::parseKeySet($cachedJwks, true);

  // เผื่อเวลา clock skew เพื่อไม่ให้ token ที่เพิ่งออกใหม่ถูกปฏิเสธ
  JWT::$leeway = 60;

  $decoded = JWT::decode($token, $keys);
  $payload = json_decode(json_encode($decoded, JSON_THROW_ON_ERROR), true, 512, JSON_THROW_ON_ERROR);

  // ตรวจสอบ issuer / audience ให้ตรงตาม .env
  $expectedIssuer = $_ENV['KEYCLOAK_ISSUER'] ?? '';
  if ($expectedIssuer !== '' && ($payload['iss'] ?? null) !== $expectedIssuer) {
    throw new UnexpectedValueException('Invalid token issuer.');
  }

  $expectedAudience = $_ENV['KEYCLOAK_AUDIENCE'] ?? '';
  if ($expectedAudience !== '') {
    $aud = $payload['aud'] ?? null;
    if (is_array($aud)) {
      if (!in_array($expectedAudience, $aud, true)) {
        throw new UnexpectedValueException('Invalid token audience.');
      }
    } elseif ($aud !== $expectedAudience) {
      throw new UnexpectedValueException('Invalid token audience.');
    }
  }

  return $payload;
}`;

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
  // expose API URLs configured in .env so the frontend can call them without user input
  const phpApiUrl = process.env.API_PHP_URL || 'http://localhost:8082/api/weather/london';
  const phpBaseUrl = phpApiUrl.replace(/\/api\/weather\/london$/i, '').replace(/\/$/, '');
  const api = [
    {
      id: 'django',
      name: 'Django API',
      method: 'GET',
      url: process.env.API_DJANGO_URL || ((process.env.APP_DJANGO_URL || 'http://localhost:8000').replace(/\/$/, '') + '/api/weather/bangkok'),
      description: 'Django REST Framework weather endpoint (Bangkok)'
    },
    {
      id: 'dotnet',
      name: '.NET 8 API',
      method: 'GET',
      url: process.env.API_DOTNET_URL || ((process.env.APP_DOTNET_API_URL || 'http://localhost:5100').replace(/\/$/, '') + '/api/weather/tokyo'),
      description: 'ASP.NET Core weather endpoint (Tokyo)'
    },
    {
      id: 'php',
      name: 'PHP API',
      method: 'GET',
      url: phpApiUrl,
      description: 'PHP weather endpoint (London)',
      baseUrl: phpBaseUrl
    }
  ];

  res.json({ apps, api });
});

app.get('/api/code/jwt', (req, res) => {
  const service = (req.query.service || 'django').toString().toLowerCase();
  const isDotnet = service === 'dotnet' || service === 'dotnet-api' || service === '.net' || service === 'dotnet8';
  const isPhp = service === 'php' || service === 'php-api';

  if (isDotnet) {
    return res.json({
      code: DOTNET_JWT_SNIPPET,
      language: 'csharp',
      languageLabel: 'C#',
      filename: 'dotnet8-api/Auth/KeycloakJwtMiddleware.cs',
      service: 'dotnet',
      serviceLabel: '.NET 8 API (C#)'
    });
  }

  if (isPhp) {
    return res.json({
      code: PHP_JWT_SNIPPET,
      language: 'php',
      languageLabel: 'PHP',
      filename: 'php-api/public/index.php',
      service: 'php',
      serviceLabel: 'PHP API (PHP)'
    });
  }

  return res.json({
    code: DJANGO_JWT_SNIPPET,
    language: 'python',
    languageLabel: 'Python',
    filename: 'django-api/api/authentication.py',
    service: 'django',
    serviceLabel: 'Django API (Python)'
  });
});

app.get('/api/code/django-jwt', (req, res) => {
  res.json({ code: DJANGO_JWT_SNIPPET, language: 'python', service: 'django' });
});

// Start server
app.listen(port, () => {
  console.log(`Svelte portal running on http://localhost:${port}`);
});
