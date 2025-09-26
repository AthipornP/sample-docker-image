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
    
    // Start the authentication process
    $oidc->authenticate();
    
} catch (Exception $e) {
    echo "<h1>Login Error</h1>";
    echo "<p>Error: " . htmlspecialchars($e->getMessage()) . "</p>";
    echo "<p><a href='/'>Back to Home</a></p>";
}
