using System.Security.Claims;
using Dotnet8Api.Auth;
using Dotnet8Api.Models;
using Dotnet8Api.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Configuration.AddEnvironmentVariables();

builder.Services.AddHttpClient();
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
        policy
            .AllowAnyOrigin()
            .AllowAnyHeader()
            .AllowAnyMethod());
});
builder.Services.AddSingleton(provider =>
{
    var configuration = provider.GetRequiredService<IConfiguration>();
    var jwksUrl = configuration["KEYCLOAK_CERT_URL"] ?? throw new InvalidOperationException("KEYCLOAK_CERT_URL environment variable is required.");
    var issuer = configuration["KEYCLOAK_ISSUER"] ?? configuration["KEYCLOAK_URL"];
    var audience = configuration["KEYCLOAK_AUDIENCE"];
    var cacheSeconds = configuration.GetValue<int?>("KEYCLOAK_JWKS_CACHE_SECONDS") ?? 3600;

    return new KeycloakJwtOptions
    {
        JwksUrl = jwksUrl,
        Issuer = issuer,
        Audience = audience,
        CacheDuration = TimeSpan.FromSeconds(cacheSeconds)
    };
});
builder.Services.AddSingleton<KeycloakJwksCache>();
builder.Services.AddSingleton<KeycloakJwtValidator>();
builder.Services.AddSingleton<WeatherService>();
var app = builder.Build();

app.UseCors();
app.UseMiddleware<KeycloakJwtMiddleware>();

app.MapGet("/api/health", () => Results.Json(new
{
    status = "healthy",
    message = "dotnet8-api is running",
    version = "1.0.0"
}));

app.MapGet("/api/weather/tokyo", async (HttpContext context, WeatherService weatherService, CancellationToken cancellationToken) =>
{
    if (context.User.Identity?.IsAuthenticated != true)
    {
        return Results.Unauthorized();
    }

    var weatherResult = await weatherService.GetWeatherAsync("tokyo", cancellationToken);
    if (!weatherResult.IsSuccess)
    {
        return Results.Json(new
        {
            error = "Failed to fetch weather data",
            detail = weatherResult.Error
        }, statusCode: StatusCodes.Status503ServiceUnavailable);
    }

    var tokenPayload = context.Items[KeycloakJwtMiddleware.TokenPayloadKey] as IDictionary<string, object?> ?? new Dictionary<string, object?>();
    var userProfile = UserProfile.FromClaimsPrincipal(context.User, tokenPayload);

    return Results.Json(new
    {
        user = userProfile,
        weather = weatherResult.Data,
        location = "Tokyo",
        message = "Weather data retrieved successfully"
    });
});

app.MapGet("/api/user/profile", (HttpContext context) =>
{
    if (context.User.Identity?.IsAuthenticated != true)
    {
        return Results.Unauthorized();
    }

    var tokenPayload = context.Items[KeycloakJwtMiddleware.TokenPayloadKey] as IDictionary<string, object?> ?? new Dictionary<string, object?>();
    var userProfile = UserProfile.FromClaimsPrincipal(context.User, tokenPayload);

    return Results.Json(new
    {
        user = userProfile,
        message = "User profile retrieved successfully"
    });
});

app.Run();
