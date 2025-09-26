# Rebuild and recreate the php service on port 8080
$compose = "docker compose -f \"$PSScriptRoot\docker-compose.yml\""

# Check if port 8080 is in use
$portInUse = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Port 8080 is in use. Please stop the service using it or change the port." -ForegroundColor Yellow
    exit 1
}

Write-Host "Building and recreating php service..."
Invoke-Expression "$compose build --no-cache"
Invoke-Expression "$compose up -d --force-recreate"
Invoke-Expression "$compose logs --no-color --tail 200"
