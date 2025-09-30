# dotnet8-api

Minimal ASP.NET Core 8 API that mirrors the Django API behaviour and validates Keycloak JWT tokens.

## Features

- 🔐 Custom middleware that validates incoming bearer tokens using Keycloak JWKS
- 🌤️ `/api/weather/tokyo` – fetches weather from [goweather.xyz](https://goweather.xyz) and augments the response with JWT user data
- 🙋 `/api/user/profile` – returns user profile information extracted from JWT claims
- ❤️ `/api/health` – unauthenticated health check endpoint

## Configuration

Environment variables (see `.env`):

- `KEYCLOAK_CERT_URL` – **required** JWKS endpoint
- `KEYCLOAK_ISSUER` / `KEYCLOAK_URL` – expected issuer (optional, but recommended)
- `KEYCLOAK_AUDIENCE` – expected audience (optional)
- `KEYCLOAK_JWKS_CACHE_SECONDS` – JWKS cache lifetime (defaults to 3600 seconds)
- `DOTNET_API_PORT` – host port for docker compose (defaults to 5100)

## Run locally with Docker

```powershell
cd dotnet8-api
docker compose up --build
```

The API becomes available at `http://localhost:5100`.

## Direct dotnet run (optional)

```powershell
cd dotnet8-api
dotnet restore
dotnet run
```

> Ensure the environment variables above are configured before running.
