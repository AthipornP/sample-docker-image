<?php
require __DIR__.'/vendor/autoload.php';

use Jumbojett\OpenIDConnectClient;

session_start();

$logged_in = isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;

function render($logged_in) {
    $actions = '';
    if ($logged_in) {
        $actions = '<a class="btn btn-primary" href="/private.php">Private</a> <a class="btn btn-accent" href="/logout.php">Logout</a>';
    } else {
        $actions = '<a class="btn btn-accent" href="/login.php">Login with SSO</a>';
    }

    $html = "<!doctype html>
<html>
<head>
    <meta charset='utf-8' />
    <meta name='viewport' content='width=device-width, initial-scale=1' />
    <title>PHP Sample App</title>
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
</head>
<body>
    <main class='hero'>
        <div class='card'>
            <h1>Customer Portal — PHP Sample</h1>
            <p class='lead'>This is a minimal PHP sample demonstrating OIDC login and access token display.</p>
            <div class='actions'>
                $actions
                <a class='btn btn-ghost' href='http://localhost:3000' target='_top'>Back to Portal</a>
            </div>
            <div class='footer'><small>Running in container — use this for development & testing only.</small></div>
        </div>
    </main>
</body>
</html>";

    echo $html;
}

render($logged_in);
