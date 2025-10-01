# PHP API

Simple PHP API that mirrors the Django and .NET examples. It verifies Keycloak-issued JWT tokens before serving data.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/health` | Health probe (no auth) |
| GET | `/api/weather/london` | Weather data for London (requires JWT) |
| GET | `/api/user/profile` | Returns claims extracted from JWT |

## Local development

```powershell
cd php-api
composer install
```

Run the container without cache:

```powershell
docker compose build --no-cache
docker compose up -d
```

Environment variables are defined in `.env` (see `.env.example`).
