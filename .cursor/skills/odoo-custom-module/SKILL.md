---
name: odoo-custom-module
description: Scaffolds and extends Odoo 19 Community custom modules in addons/ by looking up native models via catalog and Grep, inheriting instead of copying core, following Odoo 19 ORM/view conventions, and applying uninstall-hook, version-migration, and neutralize.sql criteria. Use when creating or customizing an Odoo module, inheriting a native model, adding fields, views, security, menus, OWL assets, uninstall_hook, migrations/, or data/neutralize.sql, or when the user mentions Odoo 19 addons.
---

# Odoo 19 custom modules

Write only under `addons/`. `odoo-src/` is read-only Community 19.0.

## Workflow

Copy and track:

```
Task:
- [ ] New model vs _inherit of a native model
- [ ] find_model.py (or Grep _name / _inherit)
- [ ] Read only that class or method (line range)
- [ ] Scaffold in addons/<module>/
- [ ] depends = native modules actually inherited
- [ ] security + views/menus
- [ ] Uninstall: xmlids vs uninstall_hook leftovers
- [ ] Migration: bump 19.0.x.y.z + migrations/ if stored schema/data changes
- [ ] Neutralize: data/neutralize.sql if secrets or live outbound APIs
```

1. If the user did not say whether this is a **new** model or an **extension**, ask.
2. Resolve native models:

   ```bash
   python .cursor/skills/odoo-custom-module/scripts/find_model.py sale.order
   ```

   If the catalog is missing, run `python .cursor/skills/odoo-custom-module/scripts/index_native.py` first.
3. `Read` the listed file around the class (about 80–150 lines) or `Grep` the method. Do **not** `@` `odoo-src/addons/<module>`.
4. Multi-file native flows (confirm, posting, pickings): delegate to Explore or `odoo-native-lookup`. Do not load those files into this chat. One field/view inherit → `find_model.py` is enough. Do not launch several explorers in parallel.
5. Create or edit files in `addons/<module>/` using [references/module-skeleton.md](references/module-skeleton.md).
6. Match field/method/`xpath` style to the native file you opened. Odoo 19 details: [references/views-odoo19.md](references/views-odoo19.md), [references/inheritance.md](references/inheritance.md), [references/security.md](references/security.md). OWL only if the user asked for frontend: [references/owl.md](references/owl.md).
7. Before finishing, apply [references/uninstall-and-migration.md](references/uninstall-and-migration.md) and [references/neutralize.md](references/neutralize.md). Default for a new xmlid-only module with no outbound APIs: no hook, no `migrations/`, no `neutralize.sql`. Still run the checklists. Mention the decisions when closing the task.

## Hard rules

- Never edit `odoo-src/`.
- Never copy a native module into `addons/`.
- `__manifest__.py` `version` starts with `19.0`. `depends` lists every inherited native module.
- Views: `list` not `tree`; `invisible`/`readonly`/`required` expressions, not `attrs`.
- Uninstall: Odoo already drops this module's xmlid records, `_name` tables, and extra `_inherit` columns. `uninstall_hook(env)` only to revert native leftovers or block uninstall.
- Upgrade: renaming/changing type of a stored field on a shipped module requires a version bump and `migrations/<target>/pre-migrate.py` with `def migrate(cr, version)`.
- Neutralize: if the module stores secrets or can call live services after a production dump is restored locally, add `data/neutralize.sql` (not in manifest `data`). Skip it when there is no outbound side effect.

## Runtime

`scripts/up.ps1` → http://localhost:8070 (service `odoo19_1`, DB `dev`). `addons/` is `/mnt/extra-addons`. After scaffolding: `scripts/install-module.ps1 -Module <module>`. Later edits: `scripts/update-module.ps1` and `scripts/test-module.ps1`.

## Scripts

- **find_model.py** — module, file, class, inherit list, method **names** (not bodies). Add `-v` only if you need every extender path.
- **index_native.py** — rebuild `catalogs/models.tsv` and `catalogs/modules.tsv` after updating `odoo-src/`.
