<?php
require __DIR__.'/vendor/autoload.php';
session_start();

if (!isset($_SESSION['authenticated']) || $_SESSION['authenticated'] !== true) {
    header('Location: /login.php');
    exit;
}

$access = $_SESSION['access_token'] ?? 'No access token available';
$userinfo = $_SESSION['userinfo'] ?? [];

$claims = json_encode($userinfo, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
$escaped = htmlspecialchars($claims, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
$tokenEscaped = htmlspecialchars($access, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');

$html = "<!doctype html>
<html>
<head>
    <meta charset='utf-8' />
    <meta name='viewport' content='width=device-width, initial-scale=1' />
    <title>Private - PHP Sample</title>
    <style>
        body{font-family:Segoe UI, Roboto, Arial; padding:24px; max-width:900px; margin:24px auto; background:#fff; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.06)}
        pre{background:#0f1724;color:#e6edf3;padding:12px;border-radius:8px;overflow:auto}
        .token{background:#071226;color:#dbeefd;padding:12px;border-radius:8px;overflow:auto;white-space:pre-wrap;word-break:break-word}
        a.btn{display:inline-block;padding:8px 12px;border-radius:6px;text-decoration:none;color:#fff;margin-right:8px}
        .home{background:#1976d2}
        .logout{background:#ff7a18}
        .portal{background:#6b7280}
    </style>
</head>
<body>
    <h1>Private page</h1>
    <p>You successfully authenticated via SSO.</p>
    <h3>User claims</h3>
    <pre><code>{$escaped}</code></pre>
    <h3>Access token</h3>
    <div class='token'><code>{$tokenEscaped}</code></div>
    <p style='margin-top:12px;'><a class='btn home' href='/'>Home</a><a class='btn logout' href='/logout.php'>Logout</a><a class='btn portal' href='http://localhost:3000' target='_top'>Back to Portal</a></p>
</body>
</html>";

echo $html;
