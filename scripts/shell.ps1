param(
  [string]$Database = "dev"
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
docker compose -f $compose run --rm odoo19_1 odoo shell -d $Database
