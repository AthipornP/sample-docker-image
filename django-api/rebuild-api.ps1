# Django REST API Docker Rebuild Script

Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker compose down

Write-Host "Removing old images..." -ForegroundColor Yellow
docker rmi django-api-django-api -ErrorAction SilentlyContinue

Write-Host "Building new image..." -ForegroundColor Green
docker compose build --no-cache

Write-Host "Starting containers..." -ForegroundColor Green
docker compose up -d

Write-Host "Waiting for container to start..." -ForegroundColor Yellow
Start-Sleep 5

Write-Host "Testing API health check..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/health/" -Method Get
    Write-Host "Health check successful:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nDjango API is running on http://localhost:8001" -ForegroundColor Green
Write-Host "Available endpoints:" -ForegroundColor Cyan
Write-Host "- GET /api/health/ (public)" -ForegroundColor White
Write-Host "- GET /api/profile/ (requires JWT)" -ForegroundColor White
Write-Host "- GET /api/weather/bangkok/ (requires JWT)" -ForegroundColor White