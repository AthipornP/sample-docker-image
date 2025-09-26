<?php
require __DIR__.'/vendor/autoload.php';
use Jumbojett\OpenIDConnectClient;
session_start();

$issuer = getenv('OAUTH_ISSUER');
$clientId = getenv('OAUTH_CLIENT_ID');
$clientSecret = getenv('OAUTH_CLIENT_SECRET');
$redirect = getenv('OAUTH_REDIRECT_URI') ?: 'http://localhost:8080/callback.php';

try {
    $oidc = new OpenIDConnectClient($issuer, $clientId, $clientSecret);
    $oidc->setRedirectURL($redirect);
    $oidc->addScope(['openid','profile','email']);
    $oidc->setVerifyHost(false);
    $oidc->setVerifyPeer(false);
    
    // Enable PKCE support
    $oidc->setCodeChallengeMethod('S256');
    
    // This will validate the callback and set session data
    $oidc->authenticate();
    
    // Store tokens and user info in session
    $_SESSION['access_token'] = $oidc->getAccessToken();
    $_SESSION['id_token'] = $oidc->getIdToken();
    $_SESSION['userinfo'] = $oidc->requestUserInfo();
    $_SESSION['authenticated'] = true;
    
    // Redirect to private page
    header('Location: /private.php');
    exit;
    
} catch (Exception $e) {
    echo "<h1>Authentication Error</h1>";
    echo "<p>Error: " . htmlspecialchars($e->getMessage()) . "</p>";
    echo "<p><a href='/'>Back to Home</a></p>";
}
