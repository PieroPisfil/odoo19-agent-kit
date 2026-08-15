param(
  [Parameter(Mandatory=$true)][string]$Module,
  [string]$Database = "dev"
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
docker compose -f $compose run --rm odoo19_1 odoo -d $Database -i $Module --stop-after-init --no-http
if ($LASTEXITCODE -eq 0) {
  # El servidor web persistente (docker compose up) carga su registro de
  # modelos una sola vez al arrancar; sin reiniciarlo, no ve el modulo
  # recien instalado y el navegador tira 404/KeyError sobre sus modelos.
  $running = docker compose -f $compose ps -q odoo19_1
  if ($running) {
    Write-Host "Reiniciando el servidor web para que tome el modulo instalado..."
    docker compose -f $compose restart odoo19_1
  }
}
