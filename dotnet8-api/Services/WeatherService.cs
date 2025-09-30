using System.Text.Json;

namespace Dotnet8Api.Services;

public sealed class WeatherService
{
    private static readonly Uri BaseUri = new("https://goweather.xyz/");

    private readonly IHttpClientFactory _httpClientFactory;

    public WeatherService(IHttpClientFactory httpClientFactory)
    {
        _httpClientFactory = httpClientFactory;
    }

    public async Task<WeatherResult> GetWeatherAsync(string city, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(city))
        {
            throw new ArgumentException("City must be provided", nameof(city));
        }

        var client = _httpClientFactory.CreateClient("weather-api");
        client.BaseAddress ??= BaseUri;

        try
        {
            var path = $"weather/{Uri.EscapeDataString(city.ToLowerInvariant())}";
            using var response = await client.GetAsync(path, cancellationToken).ConfigureAwait(false);
            response.EnsureSuccessStatusCode();
            await using var stream = await response.Content.ReadAsStreamAsync(cancellationToken).ConfigureAwait(false);
            var json = await JsonSerializer.DeserializeAsync<JsonElement>(stream, cancellationToken: cancellationToken).ConfigureAwait(false);
            return WeatherResult.Success(json);
        }
        catch (Exception ex)
        {
            return WeatherResult.Failure(ex.Message);
        }
    }
}

public sealed record WeatherResult(bool IsSuccess, JsonElement? Data, string? Error)
{
    public static WeatherResult Success(JsonElement data) => new(true, data, null);
    public static WeatherResult Failure(string? error) => new(false, null, error);
}
