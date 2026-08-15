param(
  [int]$Lines = 200,
  [switch]$Follow
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
if ($Follow) {
  docker compose -f $compose logs -f --tail=$Lines odoo19_1
} else {
  docker compose -f $compose logs --no-color --tail=$Lines odoo19_1
}
