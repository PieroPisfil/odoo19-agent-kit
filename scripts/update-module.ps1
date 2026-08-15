param(
  [Parameter(Mandatory=$true)][string]$Module,
  [string]$Database = "dev"
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
docker compose -f $compose run --rm odoo19_1 odoo -d $Database -u $Module --stop-after-init --no-http
if ($LASTEXITCODE -eq 0) {
  # Mismo motivo que en install-module.ps1: el servidor web persistente no
  # relee el registro de modelos solo, hay que reiniciarlo tras actualizar.
  $running = docker compose -f $compose ps -q odoo19_1
  if ($running) {
    Write-Host "Reiniciando el servidor web para que tome los cambios..."
    docker compose -f $compose restart odoo19_1
  }
}
