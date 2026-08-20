# Uninstall and migrations (Odoo 19)

Apply this on **every** create or edit of a module in `addons/`. Do not ship schema or data changes without deciding: Odoo already cleans it, `uninstall_hook` must revert it, or a `migrations/` script must transform it.

Verify hook/script signatures in `odoo-src/odoo/modules/loading.py` and `odoo-src/odoo/modules/migration.py` if anything here looks stale.

## What Odoo already does

On uninstall (`ir.module.module.module_uninstall` → `ir.model.data._module_data_uninstall`):

- Records whose **only** xmlid belongs to the module are unlinked (views, menus, actions, XML/CSV data, mail templates, crons, security, …).
- `ir.model` / `ir.model.fields` / selections / SQL constraints owned by the module are dropped (tables, columns, FKs, m2m relation tables).
- Copied views with `key` like `<module>.%` are removed.

On **first install** only: `pre_init_hook` then data load then `post_init_hook`.

On **upgrade** (`-u` / Apps upgrade): `migrations` `pre-` → init/data → `post-` → after all modules `end-`.

`noupdate="1"` only skips rewriting XML on upgrade. Those records **are still deleted on uninstall**.

Do **not** write an `uninstall_hook` just because the module adds `_name` models or `_inherit` fields. That is already cleaned.

## Uninstall criteria (design + hook)

Decide **before** writing models/data:

| Keep this way | Why |
| --- | --- |
| Data in XML/CSV with a module xmlid | Uninstall deletes it |
| New `_name` model or extra `_inherit` fields | Uninstall drops table/columns |
| Mutate a **native** record (other module's xmlid), `ir.config_parameter` from Python, or `create()` without xmlid | Survives uninstall unless a hook reverts/unlinks it |
| Extra SQL tables/indexes from `init()` / raw DDL | Survive unless the hook drops them |
| `ondelete='restrict'` from a **native** model onto a custom comodel | Can **block** uninstall |

Write `uninstall_hook` only when at least one is true:

1. The module wrote or patched records it does not own (native actions/domains, company settings, ICP keys, selection values on native fields).
2. `post_init_hook` / Python `create()` produced records without xmlids that must not remain.
3. Uninstall must be **refused** while leftover usage would be unsafe (raise `UserError`). Pattern: `cloud_storage_google` tests call the hook directly.

Hook signature in Odoo 19 is **`(env,)`**, not `(cr, registry)`:

```python
# __init__.py
from odoo.exceptions import UserError

def uninstall_hook(env):
    action = env.ref("sale.action_orders", raise_if_not_found=False)
    if action and action.domain and "x_my_filter" in (action.domain or ""):
        action.domain = []
    env["ir.config_parameter"].search([("key", "like", "my_module.%")]).unlink()
```

```python
# __manifest__.py
"uninstall_hook": "uninstall_hook",
```

Rules for the hook:

- Always `raise_if_not_found=False` on `env.ref`.
- Keep it reversible and small. Flush is done by the loader after the call.
- If the hook exists, add a test that **calls `uninstall_hook(self.env)`** (see `odoo-src/addons/cloud_storage_google/tests/`). Do not `button_uninstall` inside `TransactionCase` (Odoo forbids module ops in tests).

Prefer fixing the design (XML xmlids, no native-record writes) over adding a hook.

`pre_init_hook` / `post_init_hook` are install-time only. Use `post_init` for one-shot data that then needs a matching uninstall revert. Use `pre_init` only for install-on-huge-DB column pre-creates (native `hr_timesheet`); skip it on typical custom modules.

## Migration criteria (edits to an installed module)

ORM already: creates new tables/columns; loads new XML; unlinks xmlids that disappeared (`noupdate` false) via `_process_end`.

You **must** bump `__manifest__.py` `version` and add a script when an upgrade would otherwise **lose or corrupt data**, including:

- Rename a **stored** field or column (otherwise ORM adds an empty new column; old data stays orphaned or is dropped with the old field).
- Incompatible type/comodel change on a stored field.
- Split/merge models, rename `_name` / `_table` (avoid if possible).
- Change Selection keys that are already stored.
- Move values between tables/fields; backfill that defaults cannot express.
- SQL constraints/indexes that `init()` or raw DDL created and that the new code no longer defines.

No script needed (still bump patch if you want a visible upgrade): new optional field, new view/xpath, new method, new ACL, removing a field whose data may be discarded (say so in the reply).

Versioning in this workspace:

- Manifest: `19.0.x.y.z` (keep the `19.0` prefix).
- Bump `z` for compatible adds; bump `y` (or `x`) when a migration script is required.
- Folder name = **target** version the script belongs to, either `19.0.x.y.z` or the module-only part `x.y.z` (loader prefixes `release.major_version`). Prefer the full `19.0.x.y.z` so it matches the manifest.

```
addons/<module>/
├── __manifest__.py          # version = "19.0.1.1.0"
└── migrations/
    └── 19.0.1.1.0/
        ├── pre-migrate.py   # before ORM/XML of this module
        ├── post-migrate.py  # after ORM/XML of this module
        └── end-cleanup.py   # after every module in the graph (rare)
```

`upgrades/` is also scanned; use `migrations/` like Community addons.

Each file must start with `pre-`, `post-`, or `end-` and define:

```python
def migrate(cr, version):
    """version is the *currently installed* module version, not the target."""
```

Loader rejects any other signature (`odoo-src/odoo/modules/migration.py`).

**pre-** — schema still old. Use SQL / `odoo.tools.sql` for `RENAME COLUMN`, copies, constraint swaps. Do this **before** the ORM creates the new column.

```python
def migrate(cr, version):
    cr.execute(
        "ALTER TABLE sale_order RENAME COLUMN warranty_days TO warranty_period"
    )
```

**post-** — new fields exist. ORM `Environment` is OK when you need xmlids:

```python
from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # transform data, rewrite xmlids, UPDATE stored selection keys
```

**end-** — only for cleanup that must see the full upgraded registry.

`migrations/0.0.0/` runs on **every** version change (`pre` first, `post`/`end` last). Do not put one-shot renames there.

Do not invent `cr.execute` when the ORM can do the work in **post-**. Do not put migration logic in `post_init_hook` (install only).

## Decision checklist (copy into the task)

```
Lifecycle:
- [ ] New XML/CSV data has xmlids (uninstallable without a hook)
- [ ] No silent writes to native xmlid records / ICP / create() leftovers
- [ ] ondelete on native→custom Many2one will not block uninstall
- [ ] uninstall_hook(env) only if leftover native state exists; test calls the hook
- [ ] Stored field rename/type/_name change on an already shipped module
      → bump 19.0.x.y.z and migrations/<target>/pre-migrate.py
- [ ] Selection key or data backfill → post-migrate.py
- [ ] Field removal: confirm data loss is acceptable (no script) or copy in pre-
- [ ] Neutralize: secrets or live APIs → data/neutralize.sql (see neutralize.md)
```

If the user is only scaffolding a new module with xmlid data and extra fields, the outcome is: **no hook, no migrations folder, no neutralize.sql**. Still run the checklist and mention it when closing the task.
