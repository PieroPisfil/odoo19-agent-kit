param()
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"
docker compose -f $compose up -d
Write-Host "Odoo disponible en http://localhost:8069 (puede tardar unos segundos en arrancar)."
