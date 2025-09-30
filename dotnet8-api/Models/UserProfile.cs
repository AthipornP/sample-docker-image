using System.Security.Claims;

namespace Dotnet8Api.Models;

public sealed record UserProfile(
    string? UserId,
    string? Username,
    string? Email,
    string? FirstName,
    string? LastName,
    bool IsAuthenticated,
    IDictionary<string, object?> TokenPayload)
{
    public static UserProfile FromClaimsPrincipal(ClaimsPrincipal principal, IDictionary<string, object?> tokenPayload)
    {
        var userId = principal.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? principal.FindFirst("sub")?.Value;
        var username = principal.FindFirst("preferred_username")?.Value ?? principal.Identity?.Name;
        var email = principal.FindFirst(ClaimTypes.Email)?.Value ?? principal.FindFirst("email")?.Value;
        var firstName = principal.FindFirst(ClaimTypes.GivenName)?.Value ?? principal.FindFirst("given_name")?.Value;
        var lastName = principal.FindFirst(ClaimTypes.Surname)?.Value ?? principal.FindFirst("family_name")?.Value;

        return new UserProfile(
            userId,
            username,
            email,
            firstName,
            lastName,
            principal.Identity?.IsAuthenticated ?? false,
            tokenPayload
        );
    }
}
