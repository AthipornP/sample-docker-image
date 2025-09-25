import base64
import hashlib
import os
import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login, get_user_model
from django.urls import reverse
import requests
import json
import html


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode('ascii')


def login_view(request):
    # generate PKCE code verifier and challenge
    code_verifier = _base64url_encode(secrets.token_bytes(32))
    code_challenge = _base64url_encode(hashlib.sha256(code_verifier.encode('ascii')).digest())
    # store verifier in session for callback
    request.session['pkce_code_verifier'] = code_verifier

    # Build authorization request
    auth_endpoint = getattr(settings, 'OIDC_OP_AUTHORIZATION_ENDPOINT')
    client_id = settings.OIDC_RP_CLIENT_ID
    redirect_uri = settings.OAUTH_REDIRECT_URI or request.build_absolute_uri(reverse('oidc_callback'))
    state = secrets.token_urlsafe(16)
    request.session['oidc_auth_state'] = state

    params = {
        'response_type': 'code',
        'scope': 'openid email',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'state': state,
        'nonce': secrets.token_urlsafe(16),
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }
    url = auth_endpoint + '?' + urlencode(params)
    return HttpResponseRedirect(url)


def callback_view(request):
    error = request.GET.get('error')
    if error:
        return HttpResponseBadRequest(f"OIDC error: {error} - {request.GET.get('error_description')}")

    code = request.GET.get('code')
    state = request.GET.get('state')
    if not code or state != request.session.get('oidc_auth_state'):
        return HttpResponseBadRequest('Invalid OIDC response')

    # Exchange code for tokens using PKCE (send code_verifier)
    token_endpoint = getattr(settings, 'OIDC_OP_TOKEN_ENDPOINT')
    client_id = settings.OIDC_RP_CLIENT_ID
    client_secret = settings.OIDC_RP_CLIENT_SECRET
    redirect_uri = settings.OAUTH_REDIRECT_URI or request.build_absolute_uri(reverse('oidc_callback'))
    code_verifier = request.session.get('pkce_code_verifier')
    if not code_verifier:
        return HttpResponseBadRequest('Missing PKCE verifier in session')

    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': client_id,
        'code_verifier': code_verifier,
    }
    # include client_secret if present (confidential client)
    if client_secret:
        data['client_secret'] = client_secret

    r = requests.post(token_endpoint, data=data, timeout=10)
    if not r.ok:
        return HttpResponseBadRequest(f'Token exchange failed: {r.status_code} {r.text}')

    tokens = r.json()

    # store tokens in session
    request.session['oidc_tokens'] = tokens
    request.session['oidc_id_token'] = tokens.get('id_token')

    # Fetch userinfo to get a stable identifier (sub) and preferred username/email
    access_token = tokens.get('access_token')
    userinfo = {}
    try:
        if access_token and getattr(settings, 'OIDC_OP_USER_ENDPOINT', None):
            r_ui = requests.get(settings.OIDC_OP_USER_ENDPOINT, headers={'Authorization': f'Bearer {access_token}'}, timeout=5)
            if r_ui.ok:
                userinfo = r_ui.json()
    except Exception:
        userinfo = {}

    # persist userinfo into session for private pages
    request.session['oidc_userinfo'] = userinfo

    sub = userinfo.get('sub') or tokens.get('id_token') or 'sso-user'
    preferred = userinfo.get('preferred_username') or userinfo.get('email') or sub

    # Create or get a Django user and log them in properly
    User = get_user_model()
    try:
        user, created = User.objects.get_or_create(username=preferred, defaults={'email': userinfo.get('email', '')})
    except Exception:
        # fallback: create a simple user with username=sub
        user, created = User.objects.get_or_create(username=sub)

    # perform django login to set _auth_user_id correctly (integer PK)
    auth_login(request, user)

    return redirect('/')


def logout_view(request):
    # Perform local-only logout: clear the session and redirect to exempt page.
    # clear local session
    request.session.flush()

    # Redirect to a dedicated logged-out page that doesn't require authentication
    return redirect('/loggedout')


def private_view(request):
    # Require session 'oidc_tokens' to be present
    if not request.session.get('oidc_tokens'):
        return redirect(reverse('login') + f'?next={request.path}')

    info = request.session.get('oidc_userinfo', {})
    style = """
    <style>
    body{font-family:Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; padding:32px; background:#f6f8fa}
    .card{background:#fff;padding:24px;border-radius:10px;box-shadow:0 8px 24px rgba(15,23,42,0.06);max-width:900px;margin:12px auto}
    .btn{display:inline-block;padding:10px 16px;color:#fff;border-radius:8px;text-decoration:none;font-weight:700}
    .btn-orange{background:#ff7a18}
    .btn-blue{background:#1976d2}
    pre{background:#0f1724;color:#e6edf3;padding:12px;border-radius:8px;overflow:auto}
    </style>
    """

    # Render the user claims as a JSON code block (escaped for HTML safety)
    try:
        pretty = json.dumps(info, indent=2, ensure_ascii=False)
    except Exception:
        pretty = str(info)
    escaped = html.escape(pretty)

    json_html = f"""
    <pre style=\"background:#0f1724;color:#e6edf3;padding:12px;border-radius:8px;overflow:auto\"><code>{escaped}</code></pre>
    """

    # also show access token in a separate code block
    tokens = request.session.get('oidc_tokens', {}) or {}
    access_token = tokens.get('access_token')
    if access_token:
        access_escaped = html.escape(access_token)
        access_html = f"""
        <h3>Access token</h3>
        <pre style=\"background:#071226;color:#dbeefd;padding:12px;border-radius:8px;overflow:auto;word-break:break-all\"><code>{access_escaped}</code></pre>
        """
    else:
        access_html = "<p class=\"muted\">No access token present in session.</p>"

    body = f"{style}<div class=\"card\"><h1>Protected page</h1><p>You successfully authenticated via SSO.</p><h3>User claims</h3>{json_html}{access_html}<p><a class=\"btn btn-orange\" href=\"/logout\">Logout</a> <a class=\"btn btn-blue\" style=\"margin-left:12px;\" href=\"/\">Home</a></p></div>"
    return HttpResponse(body)
