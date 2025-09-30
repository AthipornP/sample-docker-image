from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from .oidc_views import login_view, callback_view, logout_view, private_view
import markdown
import html
import os
import dotenv

dotenv.load_dotenv()


def index(request):
    logged_in = bool(request.session.get('oidc_tokens'))
    userinfo = request.session.get('oidc_userinfo', {}) if logged_in else {}
    style = """
    <style>
    :root { --bg:#f6f8fa; --card:#ffffff; --accent:#1976d2; --orange:#ff7a18; --muted:#6b7280 }
    body { margin:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial;background:var(--bg);color:#0f1724 }
    .hero { display:flex;align-items:center;justify-content:center;min-height:60vh;padding:3rem 1rem }
    .card { background:var(--card);padding:2rem;border-radius:12px;box-shadow:0 12px 40px rgba(15,23,42,0.08);max-width:900px;width:100%;text-align:center }
    h1 { margin:0;font-size:2.25rem;color:var(--accent) }
    p.lead { color:#334155;margin:0.5rem 0 1.25rem }
    .actions { display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;margin-top:1rem }
    .btn { display:inline-flex;align-items:center;justify-content:center;padding:10px 16px;border-radius:8px;text-decoration:none;color:#fff;font-weight:700;min-width:160px }
    .btn-primary { background:linear-gradient(90deg,var(--accent),#42a5f5) }
    .btn-accent { background:linear-gradient(90deg,#ff8a00,var(--orange)) }
    .btn-ghost { background:#e2e8f0;color:#0f1724;font-weight:600;border-radius:8px;padding:10px 16px }
    .footer { text-align:center;margin-top:1.25rem;color:var(--muted) }
    </style>
    """

    # Markdown content for home page (kept from previous content)
    md = """
    This is a simple demo app that uses SSO (OpenID Connect) to protect pages.

    - Click Login to authenticate via Keycloak.
    - After login, visit the Protected page to view your user claims.
    """

    html_content = markdown.markdown(md)

    # action buttons (use the same classes as dotnet)
    if logged_in:
        actions = f"<a class=\"btn btn-primary\" href=\"/private\">Private</a> <a class=\"btn btn-accent\" href=\"/logout\">Logout</a>"
    else:
        login_url = reverse('login')
        actions = f"<a class=\"btn btn-accent\" href=\"{login_url}\">Login with SSO</a>"

    portal_button = f'<a class="btn btn-ghost" href="http://{os.getenv("PORTAL_HOST", "localhost")}:{os.getenv("PORTAL_PORT", "3000")}" target="_top">Back to Portal</a>'

    body = f"{style}<main class='hero'><div class='card'><h1>Customer Portal — Django Sample</h1><p class='lead'>This is a Django sample demonstrating OIDC login and access token display.</p>{html_content}<div class='actions'>{actions}{portal_button}</div><div class='footer'><small>Running in container — use this for development & testing only.</small></div></div></main>"
    return HttpResponse(body)


def loggedout_view(request):
    style = """
    <style>
    :root { --bg:#f6f8fa; --card:#ffffff; --accent:#1976d2; --orange:#ff7a18; --muted:#6b7280 }
    body { margin:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial;background:var(--bg);color:#0f1724 }
    .hero { display:flex;align-items:center;justify-content:center;min-height:60vh;padding:3rem 1rem }
    .card { background:var(--card);padding:2rem;border-radius:12px;box-shadow:0 12px 40px rgba(15,23,42,0.08);max-width:900px;width:100%;text-align:center }
    h1 { margin:0;font-size:2.25rem;color:var(--accent) }
    p.lead { color:#334155;margin:0.5rem 0 1.25rem }
    .actions { display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;margin-top:1rem }
    .btn { display:inline-flex;align-items:center;justify-content:center;padding:10px 16px;border-radius:8px;text-decoration:none;color:#fff;font-weight:700;min-width:160px }
    .btn-primary { background:linear-gradient(90deg,var(--accent),#42a5f5) }
    .btn-accent { background:linear-gradient(90deg,#ff8a00,var(--orange)) }
    .btn-ghost { background:#e2e8f0;color:#0f1724;font-weight:600;border-radius:8px;padding:10px 16px }
    .footer { text-align:center;margin-top:1.25rem;color:var(--muted) }
    </style>
    """

    login_url = reverse('login')
    body = f"{style}<main class='hero'><div class='card'><h1>Logged out</h1><p class='lead'>You have been successfully logged out.</p><div class='actions'><a class=\"btn btn-accent\" href=\"{login_url}\">Login again</a><a class=\"btn btn-ghost\" href=\"http://{os.getenv('PORTAL_HOST', 'localhost')}:{os.getenv('PORTAL_PORT', '3000')}\" target=\"_top\">Back to Portal</a></div><div class='footer'><small>Running in container — use this for development & testing only.</small></div></div></main>"
    return HttpResponse(body)


urlpatterns = [
    path('auth/authenticate/', login_view, name='login'),
    path('auth/callback/', callback_view, name='oidc_callback'),
    path('logout', logout_view, name='logout'),
    path('loggedout', loggedout_view, name='loggedout'),
    path('private', private_view, name='private'),
    path('', index),
]
