import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'

# If a local .env file is mounted (common in development/docker), load it into
# the process environment so settings that read os.environ[...] pick them up.
env_path = BASE_DIR / '.env'
if env_path.exists():
    try:
        for raw in env_path.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            # don't overwrite an already-set environment variable
            if key and key not in os.environ:
                os.environ[key] = val
    except Exception:
        # Best-effort loader; failing to parse the .env should not stop Django
        pass

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'mozilla_django_oidc',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Enforce login for all pages by default. Exempt the OIDC endpoints, static and health checks.
LOGIN_URL = '/auth/authenticate/'
LOGIN_EXEMPT_URLS = [
    r'^/auth/',
    r'^/logout',
    r'^/loggedout',  # Add exempt page for post-logout landing
    r'^/static/',
    r'^/healthz',
    r'^/admin',
]

# Insert our LoginRequiredMiddleware after authentication middleware
MIDDLEWARE.insert(MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware') + 1, 'config.middleware.LoginRequiredMiddleware')

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database: default to sqlite for easy local runs. Compose file can override to Postgres via env.
if os.environ.get('POSTGRES_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'django'),
            'USER': os.environ.get('POSTGRES_USER', 'django'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Authentication / OIDC settings (read from environment variables)
OIDC_RP_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET')
# OIDC_OP_DISCOVERY_ENDPOINT should point to the issuer base (or full discovery URL)
OIDC_OP_DISCOVERY_ENDPOINT = os.environ.get('OAUTH_ISSUER')
# Redirect URI used in the OIDC flow (should match Keycloak client's Valid redirect URIs)
OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI')

# If a discovery endpoint is provided, attempt to fetch the OpenID Connect configuration
# and populate the specific endpoint settings required by mozilla-django-oidc.
if OIDC_OP_DISCOVERY_ENDPOINT:
    try:
        import requests
        disc_url = OIDC_OP_DISCOVERY_ENDPOINT.rstrip('/')
        # If the value looks like the issuer (no /.well-known), try well-known first
        if not disc_url.endswith('/.well-known/openid-configuration'):
            try_urls = [disc_url + '/.well-known/openid-configuration', disc_url]
        else:
            try_urls = [disc_url]

        discovery = None
        for u in try_urls:
            try:
                r = requests.get(u, timeout=5)
                if r.ok:
                    discovery = r.json()
                    break
            except Exception:
                continue

        if discovery:
            OIDC_OP_AUTHORIZATION_ENDPOINT = discovery.get('authorization_endpoint')
            OIDC_OP_TOKEN_ENDPOINT = discovery.get('token_endpoint')
            OIDC_OP_USER_ENDPOINT = discovery.get('userinfo_endpoint')
            OIDC_OP_JWKS_ENDPOINT = discovery.get('jwks_uri')
            OIDC_OP_ISSUER = discovery.get('issuer')
    except Exception as e:
        # Best-effort only — failure will be surfaced by mozilla-django-oidc later
        print('Warning: failed to fetch OIDC discovery document:', str(e))

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
