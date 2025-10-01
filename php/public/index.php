<?php
require __DIR__.'/vendor/autoload.php';
require_once __DIR__.'/helpers.php';

use Jumbojett\OpenIDConnectClient;

session_start();

$logged_in = isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
$portalUrl = portal_url();
$escapedOidcCode = htmlspecialchars(load_oidc_snippet(), ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

function load_oidc_snippet(): string
{
    $files = [
        'login.php' => __DIR__ . '/login.php',
        'callback.php' => __DIR__ . '/callback.php',
        'helpers.php' => __DIR__ . '/helpers.php',
    ];

    $chunks = [];
    foreach ($files as $label => $path) {
        if (!file_exists($path)) {
            continue;
        }
        $contents = file_get_contents($path);
        if ($contents === false) {
            continue;
        }
        $chunks[] = "// {$label}\n" . trim($contents);
    }

    if (empty($chunks)) {
        return "// Unable to load OIDC code snippet at runtime.";
    }

    return implode("\n\n", $chunks);
}

function render($logged_in, $portalUrl, $escapedOidcCode)
{
    $actions = [];
    if ($logged_in) {
        $actions[] = '<a class="btn btn-primary" href="/private.php">Private</a>';
        $actions[] = '<a class="btn btn-accent" href="/logout.php">Logout</a>';
    } else {
        $actions[] = '<a class="btn btn-accent" href="/login.php">Login with SSO</a>';
    }

    $actions[] = "<a class='btn btn-ghost' href='{$portalUrl}' target='_top'>Back to Portal</a>";
    $actions[] = "<button class='btn btn-ghost btn-code' type='button' id='show-code-btn'>Show OIDC Code</button>";

    $actionsHtml = implode("\n                ", $actions);

    $codeSection = "<div id='oidc-code-wrapper' class='code-wrapper' aria-hidden='true' style='display:none;'>
                <h3>OIDC integration code</h3>
                <pre><code>{$escapedOidcCode}</code></pre>
                <p class='muted'>This snippet is generated from the live PHP sources (<code>login.php</code>, <code>callback.php</code>, and helper functions).</p>
            </div>";

    $toggleScript = "<script>
(function(){
    const btn = document.getElementById('show-code-btn');
    const wrapper = document.getElementById('oidc-code-wrapper');
    if(!btn || !wrapper){ return; }
    btn.addEventListener('click', function(){
        const isHidden = wrapper.style.display === 'none' || wrapper.getAttribute('aria-hidden') === 'true';
        wrapper.style.display = isHidden ? 'block' : 'none';
        wrapper.setAttribute('aria-hidden', isHidden ? 'false' : 'true');
        btn.textContent = isHidden ? 'Hide OIDC Code' : 'Show OIDC Code';
    });
})();
</script>";

    $html = <<<HTML
<!doctype html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PHP Sample App</title>
    <style>
        :root { --bg:#f6f8fa; --card:#ffffff; --accent:#1976d2; --orange:#ff7a18; --muted:#6b7280 }
        body { margin:0;font-family:Inter,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial;background:var(--bg);color:#0f1724 }
        .hero { display:flex;align-items:center;justify-content:center;min-height:60vh;padding:3rem 1rem }
        .card { background:var(--card);padding:2rem;border-radius:12px;box-shadow:0 12px 40px rgba(15,23,42,0.08);max-width:900px;width:100%;text-align:center }
        h1 { margin:0;font-size:2.25rem;color:var(--accent) }
        p.lead { color:#334155;margin:0.5rem 0 1.25rem }
        .actions { display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;margin-top:1rem }
        .btn { display:inline-flex;align-items:center;justify-content:center;padding:10px 16px;border-radius:8px;text-decoration:none;color:#fff;font-weight:700;min-width:160px;cursor:pointer;border:none }
        button.btn { font:inherit }
        .btn-primary { background:linear-gradient(90deg,var(--accent),#42a5f5) }
        .btn-accent { background:linear-gradient(90deg,#ff8a00,var(--orange)) }
        .btn-ghost { background:#e2e8f0;color:#0f1724;font-weight:600;border-radius:8px;padding:10px 16px }
        .btn-code { min-width:200px }
        .code-wrapper { margin-top:1.5rem;text-align:left }
        .code-wrapper pre { background:#0f1724;color:#e6edf3;padding:16px;border-radius:12px;overflow:auto;font-size:0.95rem;line-height:1.5 }
        .muted { color:var(--muted) }
        .footer { text-align:center;margin-top:1.25rem;color:var(--muted) }
    </style>
</head>
<body>
    <main class='hero'>
        <div class='card'>
            <h1>Customer Portal — PHP Sample</h1>
            <p class='lead'>This is a minimal PHP sample demonstrating OIDC login and access token display.</p>
            <div class='actions'>
                {$actionsHtml}
            </div>
            {$codeSection}
            <div class='footer'><small>Running in container — use this for development & testing only.</small></div>
        </div>
    </main>
    {$toggleScript}
</body>
</html>
HTML;

    echo $html;
}

render($logged_in, $portalUrl, $escapedOidcCode);
