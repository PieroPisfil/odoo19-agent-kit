param(
  [Parameter(Mandatory=$true)][string]$Module,
  [string]$Database = "dev"
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
docker compose -f $compose run --rm odoo19_1 odoo -d $Database -u $Module --test-enable --stop-after-init --log-level=test
if ($LASTEXITCODE -eq 0) {
  # Igual que install/update-module.ps1: esto tambien actualiza el modulo
  # en la BD, asi que el servidor web persistente necesita reiniciarse
  # para reflejarlo si vas a revisarlo en el navegador despues.
  $running = docker compose -f $compose ps -q odoo19_1
  if ($running) {
    Write-Host "Reiniciando el servidor web para que tome los cambios..."
    docker compose -f $compose restart odoo19_1
  }
}
