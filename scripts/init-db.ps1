param(
  [string]$Database = "dev"
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
Write-Host "Creando base de datos '$Database' con el modulo base..."
docker compose -f $compose run --rm odoo19_1 odoo -d $Database -i base --stop-after-init --no-http
Write-Host "Listo. Base '$Database' inicializada."
