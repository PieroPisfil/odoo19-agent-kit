# Odoo 19 custom-module workspace

Write new and inherited modules only in `addons/`. Treat `odoo-src/` (Community 19.0 clone) as read-only reference. Do not put project modules in `addons-third-party/` (third-party only).

`--addons-path` (agent / clone lookup): `odoo-src/addons` (Community) and `odoo-src/odoo/addons` (base). Runtime (`config/odoo.conf`): `/mnt/extra-addons,/mnt/addons-third-party` → host `addons/`, `addons-third-party/`. Native addons at runtime come from the `odoo:19.0` image, not from `odoo-src/`.

Runtime: Docker Compose at repo root (`docker-compose.yml`). Service `odoo19_1`, Postgres `postgres16_1`. Image built from `./Dockerfile` (`FROM odoo:19.0`). Do not install Odoo on the host Python (Odoo 19 expects 3.12).

```powershell
scripts/up.ps1
# http://localhost:8070 — DB `dev`, usuario admin / admin
scripts/logs.ps1 -Follow
```

Tras crear un módulo: `scripts/install-module.ps1 -Module <nombre>` (primera vez) o `scripts/update-module.ps1 -Module <nombre>`. Tests: `scripts/test-module.ps1 -Module <nombre>`. Si el manifiesto o la seguridad no entran: `docker compose restart odoo19_1` y Upgrade del módulo.

## Before writing code

1. Resolve the native model with:

   `python .cursor/skills/odoo-custom-module/scripts/find_model.py <model>`

2. Read only that class or method (line range / Grep). Do not `@` addon folders. Catalog `FILE` paths may start with `odoo/`; open the same path under `odoo-src/` (`odoo/addons/...` → `odoo-src/addons/...`, `odoo/odoo/addons/...` → `odoo-src/odoo/addons/...`).
3. Prefer `_inherit` over copying native files. Never edit `odoo-src/`.

## Uninstall, migrations, neutralize

Before finishing a create or edit, apply `.cursor/skills/odoo-custom-module/references/uninstall-and-migration.md` and `neutralize.md`.

- Put master data in XML/CSV (xmlids). Odoo already deletes those records and drops this module's tables/extra columns on uninstall.
- `uninstall_hook(env)` only to revert writes to native records / `ir.config_parameter` / `create()` without xmlids, or to raise `UserError` and block uninstall. If the hook exists, test by calling it (not `button_uninstall` in `TransactionCase`).
- If the module may already be installed and you rename or change the type of a stored field: bump `__manifest__.py` `version` (`19.0.x.y.z`) and add `migrations/<target>/pre-migrate.py` with `def migrate(cr, version)`. Selection-key or data backfills go in `post-migrate.py`.
- If the module stores secrets or can call live services after restoring a production dump locally, add `data/neutralize.sql` (auto-loaded; do not list it in manifest `data`). `base` already disables mail servers, crons, and webhooks.
- New xmlid-only modules with no outbound APIs do not need a hook, `migrations/`, or `neutralize.sql`; still record that decision.

## After updating `odoo-src/`

```bash
python .cursor/skills/odoo-custom-module/scripts/index_native.py
```

Broad native flows (confirm, posting, stock moves): use Explore or the `odoo-native-lookup` subagent. Simple field/view inherits: `find_model.py` is enough.
