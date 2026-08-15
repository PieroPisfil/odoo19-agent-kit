# Destructivo: borra por completo la base de datos de desarrollo indicada.
# Solo afecta al Postgres local del stack docker (no toca produccion).
param(
  [string]$Database = "dev",
  [switch]$Force
)
if (-not $Force) {
  Write-Host "Esto eliminara la base de datos '$Database' por completo. Vuelve a ejecutar con -Force para confirmar." -ForegroundColor Yellow
  exit 1
}
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
docker compose -f $compose exec postgres16_1 psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS \`"$Database\`";"
Write-Host "Base '$Database' eliminada. Usa init-db.ps1 para recrearla."
