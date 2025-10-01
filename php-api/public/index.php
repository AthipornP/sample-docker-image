<?php
declare(strict_types=1);

require __DIR__ . '/../vendor/autoload.php';

use Dotenv\Dotenv;
use Firebase\JWT\JWT;
use Firebase\JWT\JWK;

$dotenv = Dotenv::createImmutable(dirname(__DIR__));
$dotenv->safeLoad();

const DEFAULT_JWKS_CACHE_SECONDS = 3600;

apply_cors();

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

set_exception_handler(function (Throwable $e): void {
    error_response('Internal server error', 500, ['detail' => $e->getMessage()]);
});

handle_request();

/**
 * จัดการ routing แบบง่าย ๆ ด้วยการตรวจสอบ method และ path
 */
function handle_request(): void
{
    $method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
    $path = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';

    switch (true) {
        case $method === 'GET' && $path === '/api/health':
            json_response([
                'status' => 'healthy',
                'message' => 'PHP API is running',
                'version' => '1.0.0',
            ]);
            return;

        case $method === 'GET' && $path === '/api/weather/london':
            $payload = require_auth();
            $weather = fetch_weather('london');
            $profile = build_user_profile($payload);

            json_response([
                'user' => $profile,
                'weather' => $weather,
                'location' => 'London',
                'message' => 'Weather data retrieved successfully',
            ]);
            return;

        case $method === 'GET' && $path === '/api/user/profile':
            $payload = require_auth();
            $profile = build_user_profile($payload);

            json_response([
                'user' => $profile,
                'message' => 'User profile retrieved successfully',
            ]);
            return;

        default:
            error_response('Not found', 404);
    }
}

/**
 * ตั้งค่า header สำหรับ CORS ให้ทุก response
 */
function apply_cors(): void
{
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Headers: Authorization, Content-Type, Accept');
    header('Access-Control-Allow-Methods: GET, OPTIONS');
    header('Vary: Origin');
}

/**
 * Helper สำหรับตอบกลับเป็น JSON เสริมด้วยสถานะ HTTP
 */
function json_response(array $payload, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

/**
 * สร้าง error response พร้อมแนบรายละเอียดเพิ่มเติมตามต้องการ
 */
function error_response(string $message, int $status = 400, array $extra = []): void
{
    $body = array_merge([
        'error' => $message,
    ], $extra);

    json_response($body, $status);
}

/**
 * ดึง bearer token จาก Authorization header
 */
function extract_bearer_token(): ?string
{
    $header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';

    if ($header === '' && function_exists('apache_request_headers')) {
        $headers = apache_request_headers();
        if (isset($headers['Authorization'])) {
            $header = $headers['Authorization'];
        }
    }

    if ($header === '' || stripos($header, 'Bearer ') !== 0) {
        return null;
    }

    return trim(substr($header, 7));
}

/**
 * ดึง JWKS จาก Keycloak แล้ว cache ไว้ในหน่วยความจำเพื่อลดการเรียกซ้ำ
 */
function load_jwks(): array
{
    static $cachedJwks = null;
    static $cachedAt = 0;

    $jwksUrl = $_ENV['KEYCLOAK_CERT_URL'] ?? '';
    if ($jwksUrl === '') {
        throw new RuntimeException('KEYCLOAK_CERT_URL environment variable is required.');
    }

    $cacheSeconds = (int) ($_ENV['KEYCLOAK_JWKS_CACHE_SECONDS'] ?? DEFAULT_JWKS_CACHE_SECONDS);

    if ($cachedJwks !== null && (time() - $cachedAt) < $cacheSeconds) {
        return $cachedJwks;
    }

    $client = curl_init($jwksUrl);
    curl_setopt_array($client, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
    ]);

    $response = curl_exec($client);
    if ($response === false) {
        $error = curl_error($client);
        curl_close($client);
        throw new RuntimeException('Failed to fetch JWKS: ' . $error);
    }

    $status = curl_getinfo($client, CURLINFO_RESPONSE_CODE);
    curl_close($client);

    if ($status < 200 || $status >= 300) {
        throw new RuntimeException('Failed to fetch JWKS: HTTP ' . $status);
    }

    $jwks = json_decode($response, true);
    if (!is_array($jwks) || !isset($jwks['keys'])) {
        throw new RuntimeException('Invalid JWKS payload.');
    }

    $cachedJwks = $jwks;
    $cachedAt = time();

    return $cachedJwks;
}

/**
 * ตรวจสอบความถูกต้องของ JWT และคืน payload กลับมา
 */
function verify_jwt(string $token): array
{
    $jwks = load_jwks();

    // แปลง JWKS ให้กลายเป็น key ที่ firebase/php-jwt เข้าใจได้ (ปล่อยให้เลือกอัลกอริทึมจาก JWKS)
    $keys = JWK::parseKeySet($jwks);

    // ปรับ leeway เล็กน้อยสำหรับกรณีเวลาคลาดเคลื่อน
    JWT::$leeway = 60;

    $decoded = JWT::decode($token, $keys);
    $payload = json_decode(json_encode($decoded, JSON_THROW_ON_ERROR), true, 512, JSON_THROW_ON_ERROR);

    $expectedIssuer = $_ENV['KEYCLOAK_ISSUER'] ?? '';
    if ($expectedIssuer !== '' && ($payload['iss'] ?? null) !== $expectedIssuer) {
        throw new UnexpectedValueException('Invalid token issuer.');
    }

    $expectedAudience = $_ENV['KEYCLOAK_AUDIENCE'] ?? '';
    if ($expectedAudience !== '') {
        $aud = $payload['aud'] ?? null;
        if (is_array($aud)) {
            if (!in_array($expectedAudience, $aud, true)) {
                throw new UnexpectedValueException('Invalid token audience.');
            }
        } elseif ($aud !== $expectedAudience) {
            throw new UnexpectedValueException('Invalid token audience.');
        }
    }

    return $payload;
}

/**
 * บังคับให้ endpoint ตรวจสอบ JWT และคืน payload หากผ่าน
 */
function require_auth(): array
{
    $token = extract_bearer_token();
    if ($token === null) {
        error_response('Missing bearer token', 401);
    }

    try {
        return verify_jwt($token);
    } catch (Throwable $e) {
        error_response('Invalid token', 401, ['detail' => $e->getMessage()]);
    }
}

/**
 * แปลง payload มาเป็นข้อมูลผู้ใช้ที่อ่านง่ายขึ้น
 */
function build_user_profile(array $payload): array
{
    $fullName = $payload['name'] ?? trim((string) (($payload['given_name'] ?? '') . ' ' . ($payload['family_name'] ?? '')));

    return [
        'user_id' => $payload['sub'] ?? null,
        'username' => $payload['preferred_username'] ?? ($payload['email'] ?? null),
        'email' => $payload['email'] ?? null,
        'full_name' => $fullName !== '' ? $fullName : null,
        'token_payload' => $payload,
    ];
}

/**
 * เรียกข้อมูลสภาพอากาศจาก goweather.xyz
 */
function fetch_weather(string $city): array
{
    $url = 'https://goweather.xyz/weather/' . rawurlencode($city);

    $client = curl_init($url);
    curl_setopt_array($client, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_FOLLOWLOCATION => true,
    ]);

    $response = curl_exec($client);
    if ($response === false) {
        $error = curl_error($client);
        curl_close($client);
        throw new RuntimeException('Failed to fetch weather data: ' . $error);
    }

    $status = curl_getinfo($client, CURLINFO_RESPONSE_CODE);
    curl_close($client);

    if ($status < 200 || $status >= 300) {
        throw new RuntimeException('Weather API returned HTTP ' . $status);
    }

    $data = json_decode($response, true);
    if (!is_array($data)) {
        throw new RuntimeException('Weather API returned invalid JSON');
    }

    return $data;
}
