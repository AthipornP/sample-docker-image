namespace Dotnet8Api.Auth;

// โครงสร้างสำหรับตั้งค่าการตรวจสอบ JWT จาก Keycloak เช่น URL ของ JWKS และเวลาคง cache
public sealed class KeycloakJwtOptions
{
    public required string JwksUrl { get; init; }
    public string? Issuer { get; init; }
    public string? Audience { get; init; }
    public TimeSpan CacheDuration { get; init; } = TimeSpan.FromHours(1);
}
