param(
  [switch]$Volumes
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
if ($Volumes) {
  docker compose -f $compose down -v
} else {
  docker compose -f $compose down
}
