param(
    [switch]$NoCache
)

Set-Location -Path $PSScriptRoot

if ($NoCache) {
    docker compose build --no-cache
} else {
    docker compose build
}

docker compose up -d
