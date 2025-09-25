from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from .oidc_views import login_view, callback_view, logout_view, private_view
import markdown
import html


def index(request):
    logged_in = bool(request.session.get('oidc_tokens'))
    userinfo = request.session.get('oidc_userinfo', {}) if logged_in else {}

    style = """
    <style>
    body{font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:32px; background:#f6f8fa}
    .card{background:#fff;padding:24px;border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,0.06);max-width:900px;margin:12px auto}
    .btn{display:inline-block;padding:10px 16px;color:#fff;border-radius:8px;text-decoration:none;font-weight:700}
    .btn-orange{background:#ff7a18}
    .btn-blue{background:#1976d2}
    .muted{color:#4b5563}
    pre{background:#0f1724;color:#e6edf3;padding:12px;border-radius:8px;overflow:auto}
    </style>
    """

    # Markdown content for home page (could be moved to a file)
    md = """
    # Django Sample App

    This is a simple demo app that uses SSO (OpenID Connect) to protect pages.

    - Click Login to authenticate via Keycloak.
    - After login, visit the Protected page to view your user claims.
    """

    html_content = markdown.markdown(md)

    # action buttons (use buttons styled like links)
    if logged_in:
        actions = f"<a class=\"btn btn-blue\" href=\"/private\">Protected</a> <a class=\"btn btn-orange\" href=\"/logout\">Logout</a>"
    else:
        login_url = reverse('login')
        actions = f"<a class=\"btn btn-orange\" href=\"{login_url}\">Login</a>"

    portal_button = '<a class="btn btn-blue" href="http://localhost:3000" target="_top">Back to Portal</a>'

    body = f"{style}<div class=\"card\">{html_content}<p style=\"margin-top:18px;\">{actions} {portal_button}</p></div>"
    return HttpResponse(body)


def loggedout_view(request):
    style = """
    <style>
    body{font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:32px; background:#f6f8fa}
    .card{background:#fff;padding:24px;border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,0.06);max-width:900px;margin:12px auto}
    .btn{display:inline-block;padding:10px 16px;color:#fff;border-radius:8px;text-decoration:none;font-weight:700}
    .btn-orange{background:#ff7a18}
    .btn-blue{background:#1976d2}
    .muted{color:#4b5563}
    </style>
    """
    
    login_url = reverse('login')
    body = f"{style}<div class=\"card\"><h1>Logged out</h1><p class=\"muted\">You have been successfully logged out.</p><p><a class=\"btn btn-orange\" href=\"{login_url}\">Login again</a></p><p><a class=\"btn btn-blue\" href=\"http://localhost:3000\" target=\"_top\">Back to Portal</a></p></div>"
    return HttpResponse(body)


urlpatterns = [
    path('auth/authenticate/', login_view, name='login'),
    path('auth/callback/', callback_view, name='oidc_callback'),
    path('logout', logout_view, name='logout'),
    path('loggedout', loggedout_view, name='loggedout'),
    path('private', private_view, name='private'),
    path('', index),
]
