from django.urls import path
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse
from .oidc_views import login_view, callback_view, logout_view, private_view


def index(request):
    logged_in = bool(request.session.get('oidc_tokens'))
    userinfo = request.session.get('oidc_userinfo', {}) if logged_in else {}

    style = """
    <style>
    body{font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:32px; background:#f6f8fa}
    .card{background:#fff;padding:24px;border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,0.06);max-width:900px;margin:12px auto}
    .btn{display:inline-block;padding:10px 16px;background:#ff7a18;color:#fff;border-radius:8px;text-decoration:none;font-weight:700}
    .muted{color:#4b5563}
    pre{background:#0f1724;color:#e6edf3;padding:12px;border-radius:8px;overflow:auto}
    </style>
    """

    if logged_in:
        body = f"{style}<div class=\"card\"><h1>Welcome</h1><p class=\"muted\">You are signed in via SSO.</p><p><a class=\"btn\" href=\"/logout\">Logout</a></p><h3>User claims</h3><pre>{userinfo}</pre><p><a href=\"http://localhost:3000\" target=\"_top\">Back to Portal</a></p></div>"
    else:
        login_url = reverse('login')
        body = f"{style}<div class=\"card\"><h1>Welcome</h1><p class=\"muted\">This Django sample app uses SSO. Click below to sign in.</p><p><a class=\"btn\" href=\"{login_url}\">Login</a></p><p><a href=\"http://localhost:3000\" target=\"_top\">Back to Portal</a></p></div>"

    return HttpResponse(body)


def loggedout_view(request):
    style = """
    <style>
    body{font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:32px; background:#f6f8fa}
    .card{background:#fff;padding:24px;border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,0.06);max-width:900px;margin:12px auto}
    .btn{display:inline-block;padding:10px 16px;background:#ff7a18;color:#fff;border-radius:8px;text-decoration:none;font-weight:700}
    .muted{color:#4b5563}
    </style>
    """
    
    login_url = reverse('login')
    body = f"{style}<div class=\"card\"><h1>Logged out</h1><p class=\"muted\">You have been successfully logged out.</p><p><a class=\"btn\" href=\"{login_url}\">Login again</a></p><p><a href=\"http://localhost:3000\" target=\"_top\">Back to Portal</a></p></div>"
    return HttpResponse(body)


urlpatterns = [
    path('auth/authenticate/', login_view, name='login'),
    path('auth/callback/', callback_view, name='oidc_callback'),
    path('logout', logout_view, name='logout'),
    path('loggedout', loggedout_view, name='loggedout'),
    path('private', private_view, name='private'),
    path('', index),
]
