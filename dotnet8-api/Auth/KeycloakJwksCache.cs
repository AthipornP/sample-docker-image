using Microsoft.IdentityModel.Tokens;

namespace Dotnet8Api.Auth;

// จัดการ cache ของ JWKS (กุญแจสาธารณะจาก Keycloak) เพื่อลดจำนวนครั้งที่ต้องเรียก Keycloak
public sealed class KeycloakJwksCache
{
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly KeycloakJwtOptions _options;
    private readonly SemaphoreSlim _refreshLock = new(1, 1);

    private JsonWebKeySet? _cachedKeySet;
    private DateTimeOffset _lastUpdated = DateTimeOffset.MinValue;

    public KeycloakJwksCache(IHttpClientFactory httpClientFactory, KeycloakJwtOptions options)
    {
        _httpClientFactory = httpClientFactory;
        _options = options;
    }

    public async Task<JsonWebKeySet> GetKeySetAsync(CancellationToken cancellationToken = default)
    {
        // ถ้ายังไม่หมดอายุ cache ให้ใช้กุญแจเดิม
        if (_cachedKeySet is not null && DateTimeOffset.UtcNow - _lastUpdated < _options.CacheDuration)
        {
            return _cachedKeySet;
        }

        await _refreshLock.WaitAsync(cancellationToken).ConfigureAwait(false);
        try
        {
            // ตรวจอีกครั้งหลังจาก lock เผื่อว่ามี thread อื่นดึงข้อมูลอัปเดตให้แล้ว
            if (_cachedKeySet is not null && DateTimeOffset.UtcNow - _lastUpdated < _options.CacheDuration)
            {
                return _cachedKeySet;
            }

            // เรียก Keycloak เพื่อดึง JWKS และเก็บลง cache
            var client = _httpClientFactory.CreateClient("keycloak-jwks");
            using var response = await client.GetAsync(_options.JwksUrl, cancellationToken).ConfigureAwait(false);
            response.EnsureSuccessStatusCode();
            var payload = await response.Content.ReadAsStringAsync(cancellationToken).ConfigureAwait(false);
            _cachedKeySet = new JsonWebKeySet(payload);
            _lastUpdated = DateTimeOffset.UtcNow;
            return _cachedKeySet;
        }
        finally
        {
            _refreshLock.Release();
        }
    }
}
