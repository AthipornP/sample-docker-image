using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text.Json;
using Microsoft.IdentityModel.Tokens;

namespace Dotnet8Api.Auth;

// ตัว Validator สำหรับตรวจสอบลายเซ็นและข้อมูลภายใน JWT ที่ออกโดย Keycloak
public sealed class KeycloakJwtValidator
{
    private readonly KeycloakJwksCache _jwksCache;
    private readonly KeycloakJwtOptions _options;

    public KeycloakJwtValidator(KeycloakJwksCache jwksCache, KeycloakJwtOptions options)
    {
        _jwksCache = jwksCache;
        _options = options;
    }

    public async Task<KeycloakValidationResult> ValidateAsync(string token, CancellationToken cancellationToken = default)
    {
        // ใช้ JwtSecurityTokenHandler ของ .NET ในการตรวจสอบความถูกต้องของ token
        var handler = new JwtSecurityTokenHandler();
        var validationParameters = await BuildValidationParametersAsync(cancellationToken).ConfigureAwait(false);

        // หากตรวจสอบผ่าน จะได้ ClaimsPrincipal และ security token กลับมา
        var principal = handler.ValidateToken(token, validationParameters, out var securityToken);
        if (securityToken is not JwtSecurityToken jwt)
        {
            throw new SecurityTokenException("Token is not a JWT.");
        }

        // เก็บ payload ของ JWT ที่ยังมีข้อมูลไว้เป็น dictionary เพื่อใช้งานต่อ
        var payload = jwt.Payload
            .Where(kvp => kvp.Value is not null)
            .ToDictionary(kvp => kvp.Key, kvp => kvp.Value);

        return new KeycloakValidationResult(principal, payload);
    }

    private async Task<TokenValidationParameters> BuildValidationParametersAsync(CancellationToken cancellationToken)
    {
        // ดึงชุดกุญแจสาธารณะ (JWKS) จาก cache เพื่อใช้ตรวจลายเซ็นของ token
        var keySet = await _jwksCache.GetKeySetAsync(cancellationToken).ConfigureAwait(false);

        // กำหนดกฎการตรวจสอบต่าง ๆ เช่น issuer, audience, วันหมดอายุ และลายเซ็น
        var parameters = new TokenValidationParameters
        {
            ValidateIssuer = !string.IsNullOrWhiteSpace(_options.Issuer),
            ValidIssuer = _options.Issuer,
            ValidateAudience = !string.IsNullOrWhiteSpace(_options.Audience),
            ValidAudience = _options.Audience,
            ValidateLifetime = true,
            RequireExpirationTime = true,
            RequireSignedTokens = true,
            ValidateIssuerSigningKey = true,
            IssuerSigningKeys = keySet.GetSigningKeys(),
            ClockSkew = TimeSpan.FromMinutes(2)
        };

        return parameters;
    }
}

public sealed record KeycloakValidationResult(ClaimsPrincipal Principal, IDictionary<string, object?> Payload);
