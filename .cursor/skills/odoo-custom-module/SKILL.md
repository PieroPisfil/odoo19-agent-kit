---
name: odoo-custom-module
description: Scaffolds and extends Odoo 19 Community custom modules in custom_addons/ by looking up native models via catalog and Grep, inheriting instead of copying core, and following Odoo 19 ORM/view conventions. Use when creating or customizing an Odoo module, inheriting a native model, adding fields, views, security, menus, or OWL assets, or when the user mentions Odoo 19 addons.
---

# Odoo 19 custom modules

Write only under `custom_addons/`. `odoo/` is read-only Community 19.0.

## Workflow

Copy and track:

```
Task:
- [ ] New model vs _inherit of a native model
- [ ] find_model.py (or Grep _name / _inherit)
- [ ] Read only that class or method (line range)
- [ ] Scaffold in custom_addons/<module>/
- [ ] depends = native modules actually inherited
- [ ] security + views/menus
```

1. If the user did not say whether this is a **new** model or an **extension**, ask.
2. Resolve native models:

   ```bash
   python .cursor/skills/odoo-custom-module/scripts/find_model.py sale.order
   ```

   If the catalog is missing, run `python .cursor/skills/odoo-custom-module/scripts/index_native.py` first.
3. `Read` the listed file around the class (about 80–150 lines) or `Grep` the method. Do **not** `@` `odoo/addons/<module>`.
4. Multi-file native flows (confirm, posting, pickings): delegate to Explore or `odoo-native-lookup`. Do not load those files into this chat. One field/view inherit → `find_model.py` is enough. Do not launch several explorers in parallel.
5. Create or edit files in `custom_addons/<module>/` using [references/module-skeleton.md](references/module-skeleton.md).
6. Match field/method/`xpath` style to the native file you opened. Odoo 19 details: [references/views-odoo19.md](references/views-odoo19.md), [references/inheritance.md](references/inheritance.md), [references/security.md](references/security.md). OWL only if the user asked for frontend: [references/owl.md](references/owl.md).

## Hard rules

- Never edit `odoo/`.
- Never copy a native module into `custom_addons/`.
- `__manifest__.py` `version` starts with `19.0`. `depends` lists every inherited native module.
- Views: `list` not `tree`; `invisible`/`readonly`/`required` expressions, not `attrs`.

## Runtime

Odoo runs with `docker compose up -d` (port 8070). `custom_addons/` is `/mnt/extra-addons`. After scaffolding, the module is installed in Apps (Update Apps List) or:

```bash
docker compose run --rm --no-deps odoo odoo -d odoo19 -i <module> --stop-after-init
docker compose restart odoo
```

Upgrade an already installed module with `-u` instead of `-i`.

## Scripts

- **find_model.py** — module, file, class, inherit list, method **names** (not bodies). Add `-v` only if you need every extender path.
- **index_native.py** — rebuild `catalogs/models.tsv` and `catalogs/modules.tsv` after updating `odoo/`.
