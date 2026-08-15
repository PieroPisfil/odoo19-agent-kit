# Indice estructural "bajo demanda": consulta los campos reales de un modelo
# directamente contra la instancia Odoo corriendo (fields_get()), sin mantener
# una base de metadata aparte. Siempre refleja tu instalacion real (custom
# modules incluidos), no solo lo que dice el codigo fuente nativo.
param(
  [Parameter(Mandatory=$true)][string]$Model,
  [string]$Database = "dev"
)
$compose = Join-Path $PSScriptRoot "..\docker-compose.yml"

$py = @"
import json
m = env['$Model']
fields = m.fields_get()
out = {}
for name, f in fields.items():
    out[name] = {
        'type': f.get('type'),
        'relation': f.get('relation'),
        'required': f.get('required', False),
        'string': f.get('string'),
    }
print(json.dumps(out, indent=2, ensure_ascii=False))
"@

$py | docker compose -f $compose run --rm -T odoo19_1 odoo shell -d $Database --no-http
