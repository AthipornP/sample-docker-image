using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.OpenIdConnect;
using Microsoft.Extensions.Caching.Memory;
using Microsoft.IdentityModel.Protocols.OpenIdConnect;

var builder = WebApplication.CreateBuilder(args);

// Read OAuth/OIDC settings from environment (.env provided to container)
var oauthIssuer = builder.Configuration["OAUTH_ISSUER"];
var oauthClientId = builder.Configuration["OAUTH_CLIENT_ID"];
var oauthClientSecret = builder.Configuration["OAUTH_CLIENT_SECRET"];
var oauthRedirect = builder.Configuration["OAUTH_REDIRECT_URI"];
var portalHost = builder.Configuration["PORTAL_HOST"] ?? builder.Configuration["HOST"] ?? "localhost";
var portalPort = builder.Configuration["PORTAL_PORT"] ?? "3000";
var portalUrl = $"http://{portalHost}{(string.IsNullOrEmpty(portalPort) || portalPort == "80" ? string.Empty : ":" + portalPort)}";

// <oidc-snippet>
// Configure authentication: cookie + OpenID Connect
builder.Services.AddAuthentication(options =>
{
	options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
	options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
})
	.AddCookie(options =>
	{
		// Use a distinct cookie name to reduce collisions with other apps on the same host
		options.Cookie.Name = ".dotnet_auth";
		// Keep the cookie on the app root path; you can further scope this if you host under a sub-path
		options.Cookie.Path = "/";
		options.Cookie.SameSite = Microsoft.AspNetCore.Http.SameSiteMode.Lax;
		// Consider setting SecurePolicy and other attributes in production
	})
	.AddOpenIdConnect(OpenIdConnectDefaults.AuthenticationScheme, options =>
	{
		options.Authority = oauthIssuer;
		options.ClientId = oauthClientId;
		options.ClientSecret = oauthClientSecret;
		options.ResponseType = OpenIdConnectResponseType.Code;
		// Avoid persisting tokens into the authentication cookie (this can make cookies very large
		// and cause 'Request Header Fields Too Large' errors when multiple apps share the same domain)
		options.SaveTokens = false;
		options.GetClaimsFromUserInfoEndpoint = true;
		options.Scope.Clear();
		options.Scope.Add("openid");
		options.Scope.Add("profile");
		options.Scope.Add("email");

		// Store access token server-side in memory cache during sign-in so we can display it
		options.Events = new OpenIdConnectEvents
		{
			OnTokenValidated = ctx =>
			{
				try
				{
					var cache = ctx.HttpContext.RequestServices.GetRequiredService<IMemoryCache>();
					var userId = ctx.Principal?.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? ctx.Principal?.FindFirst("sub")?.Value;
					var access = ctx.TokenEndpointResponse?.AccessToken;
					if (!string.IsNullOrEmpty(userId) && !string.IsNullOrEmpty(access))
					{
						cache.Set($"access_token:{userId}", access, TimeSpan.FromMinutes(60));
					}
				}
				catch { }
				return Task.CompletedTask;
			}
		};

		// Use the default callback path (/signin-oidc). Do not override with OAUTH_REDIRECT_URI here.
	});

// Register authorization services (required for UseAuthorization)
builder.Services.AddAuthorization();

// Register an in-memory cache to keep tokens server-side (avoids storing tokens in cookies)
builder.Services.AddMemoryCache();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();


// Login endpoint: trigger OIDC challenge
app.MapGet("/auth/login", async (HttpContext ctx) =>
{
	// after login return to /private by default
	var props = new AuthenticationProperties { RedirectUri = "/private" };
	await ctx.ChallengeAsync(OpenIdConnectDefaults.AuthenticationScheme, props);
});

// Logout endpoint: sign out locally (clear cookie) and redirect to home
app.MapGet("/auth/logout", async (HttpContext ctx) =>
{
	// remove server-side cached token for this user (best-effort)
	try
	{
		var cache = ctx.RequestServices.GetService<IMemoryCache>();
		var userId = ctx.User?.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? ctx.User?.FindFirst("sub")?.Value;
		if (cache != null && !string.IsNullOrEmpty(userId)) cache.Remove($"access_token:{userId}");
	}
	catch { }

	await ctx.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
	return Results.Redirect("/");
});

// </oidc-snippet>

var oidcCodeSnippet = LoadOidcSnippet();
var escapedOidcCode = System.Net.WebUtility.HtmlEncode(oidcCodeSnippet);
var codeSectionHtml = $@"<div id='oidc-code-wrapper' class='code-wrapper' aria-hidden='true' style='display:none;'>
		<h3>OIDC integration code</h3>
		<pre><code>{escapedOidcCode}</code></pre>
		<p class='muted'>This snippet is loaded directly from <code>Program.cs</code> at runtime.</p>
	</div>";
var toggleScript = @"<script>
(function () {
	const btn = document.getElementById('show-code-btn');
	const wrapper = document.getElementById('oidc-code-wrapper');
	if (!btn || !wrapper) { return; }
	btn.addEventListener('click', function () {
		const isHidden = wrapper.style.display === 'none' || wrapper.getAttribute('aria-hidden') === 'true';
		wrapper.style.display = isHidden ? 'block' : 'none';
		wrapper.setAttribute('aria-hidden', isHidden ? 'false' : 'true');
		btn.textContent = isHidden ? 'Hide OIDC Code' : 'Show OIDC Code';
	});
})();
</script>";

// Home page: shows Login button when not authenticated
app.MapGet("/", (HttpContext ctx) =>
{
	var isAuth = ctx.User?.Identity?.IsAuthenticated ?? false;
	var actions = new List<string>();
	if (isAuth)
	{
		actions.Add("<a href='/private' class='btn btn-primary'>Private</a>");
		actions.Add("<a href='/auth/logout' class='btn btn-accent'>Logout</a>");
	}
	else
	{
		actions.Add("<a href='/auth/login' class='btn btn-accent'>Login with SSO</a>");
	}
	actions.Add($"<a class='btn btn-ghost' href='{portalUrl}' target='_top'>Back to Portal</a>");
	actions.Add("<button class='btn btn-ghost btn-code' type='button' id='show-code-btn'>Show OIDC Code</button>");

	var actionsHtml = string.Join("\n                ", actions);
	var body = $@"<!doctype html>
<html>
<head>
	<meta charset='utf-8' />
	<meta name='viewport' content='width=device-width, initial-scale=1' />
	<title>.NET 8 Sample App</title>
	<style>
		:root {{ --bg:#f6f8fa; --card:#ffffff; --accent:#1976d2; --orange:#ff7a18; --muted:#6b7280 }}
		body {{ margin:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial;background:var(--bg);color:#0f1724 }}
		.hero {{ display:flex;align-items:center;justify-content:center;min-height:60vh;padding:3rem 1rem }}
		.card {{ background:var(--card);padding:2rem;border-radius:12px;box-shadow:0 12px 40px rgba(15,23,42,0.08);max-width:900px;width:100%;text-align:center }}
		h1 {{ margin:0;font-size:2.25rem;color:var(--accent) }}
		p.lead {{ color:#334155;margin:0.5rem 0 1.25rem }}
		.actions {{ display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;margin-top:1rem }}
		.btn {{ display:inline-flex;align-items:center;justify-content:center;padding:10px 16px;border-radius:8px;text-decoration:none;color:#fff;font-weight:700;min-width:160px;cursor:pointer;border:none }}
		button.btn {{ font:inherit }}
		.btn-primary {{ background:linear-gradient(90deg,var(--accent),#42a5f5) }}
		.btn-accent {{ background:linear-gradient(90deg,#ff8a00,var(--orange)) }}
		.btn-ghost {{ background:#e2e8f0;color:#0f1724;font-weight:600;border-radius:8px;padding:10px 16px }}
		.btn-code {{ min-width:200px }}
		.code-wrapper {{ margin-top:1.5rem;text-align:left }}
		.code-wrapper pre {{ background:#0f1724;color:#e6edf3;padding:16px;border-radius:12px;overflow:auto;font-size:0.95rem;line-height:1.5 }}
		.muted {{ color:var(--muted) }}
		.footer {{ text-align:center;margin-top:1.25rem;color:var(--muted) }}
	</style>
</head>
<body>
	<main class='hero'>
		<div class='card'>
			<h1>Customer Portal — .NET Sample</h1>
			<p class='lead'>This is a minimal sample app demonstrating OIDC login and access token display.</p>
			<div class='actions'>
				{actionsHtml}
			</div>
			{codeSectionHtml}
			<div class='footer'><small>Running in container — use this for development & testing only.</small></div>
		</div>
	</main>
	{toggleScript}
</body>
</html>";
	return Results.Content(body, "text/html");
});

// Protected private page
app.MapGet("/private", async (HttpContext ctx) =>
{
	if (!(ctx.User?.Identity?.IsAuthenticated ?? false))
	{
		// redirect to login
		return Results.Redirect("/auth/login");
	}

	// build claims JSON: group duplicate claim types (e.g. groups) into arrays to avoid ToDictionary collisions
	var claimsDict = ctx.User.Claims
		.GroupBy(c => c.Type)
		.ToDictionary(g => g.Key, g => g.Count() == 1 ? (object)g.First().Value : (object)g.Select(c => c.Value).ToArray());

	var claimsJson = System.Text.Json.JsonSerializer.Serialize(claimsDict, new System.Text.Json.JsonSerializerOptions { WriteIndented = true });

	// get access token: try token store first (we disabled SaveTokens to keep cookies small)
	var accessToken = await ctx.GetTokenAsync("access_token");
	if (string.IsNullOrEmpty(accessToken))
	{
		try
		{
			var cache = ctx.RequestServices.GetService<IMemoryCache>();
			var userId = ctx.User?.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? ctx.User?.FindFirst("sub")?.Value;
			if (cache != null && !string.IsNullOrEmpty(userId) && cache.TryGetValue($"access_token:{userId}", out string cached))
			{
				accessToken = cached;
			}
		}
		catch { }
	}
	accessToken ??= "(no access_token)";

	var html = $@"<div style='font-family:Segoe UI, Roboto, Arial; padding:24px; max-width:900px; margin:24px auto; background:#fff; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.06)'>
		<h1>Private page</h1>
		<p>You successfully authenticated via SSO.</p>
		<h3>User claims</h3>
		<pre style='background:#0f1724;color:#e6edf3;padding:12px;border-radius:8px;overflow:auto'><code>{System.Net.WebUtility.HtmlEncode(claimsJson)}</code></pre>
		<h3>Access token</h3>
		<div style='background:#071226;color:#dbeefd;padding:12px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-word'><code>{System.Net.WebUtility.HtmlEncode(accessToken)}</code></div>
	<p style='margin-top:12px;'><a href='/' style='display:inline-block;padding:8px 12px;background:#1976d2;color:#fff;border-radius:6px;text-decoration:none;font-weight:600;margin-right:8px;'>Home</a><a href='/auth/logout' style='display:inline-block;padding:8px 12px;background:#ff7a18;color:#fff;border-radius:6px;text-decoration:none;font-weight:700;margin-right:8px;'>Logout</a><a href='{portalUrl}' style='display:inline-block;padding:8px 12px;background:#6b7280;color:#fff;border-radius:6px;text-decoration:none;font-weight:600;'>Back to Portal</a></p>
	</div>";

	return Results.Content(html, "text/html");
});

app.Run();

static string LoadOidcSnippet()
{
	const string fallback = "// Unable to load OIDC code snippet at runtime.";
	var candidates = new[]
	{
		Path.Combine(AppContext.BaseDirectory, "Program.cs"),
		Path.Combine(AppContext.BaseDirectory, "..", "Program.cs"),
		Path.Combine(AppContext.BaseDirectory, "..", "..", "Program.cs")
	};

	foreach (var path in candidates)
	{
		try
		{
			if (!File.Exists(path))
			{
				continue;
			}

			var source = File.ReadAllText(path);
			var snippet = ExtractOidcSnippet(source);
			if (!string.IsNullOrWhiteSpace(snippet))
			{
				return snippet.Trim();
			}
		}
		catch
		{
			// ignored - we'll fall back to the default string
		}
	}

	return fallback;
}

static string ExtractOidcSnippet(string source)
{
	const string start = "// <oidc-snippet>";
	const string end = "// </oidc-snippet>";
	var startIndex = source.IndexOf(start, StringComparison.Ordinal);
	var endIndex = source.IndexOf(end, StringComparison.Ordinal);

	if (startIndex >= 0 && endIndex > startIndex)
	{
		var contentStart = startIndex + start.Length;
		var length = endIndex - contentStart;
		return source.Substring(contentStart, length);
	}

	return string.Empty;
}
