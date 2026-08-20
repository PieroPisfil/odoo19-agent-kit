# Module skeleton (Odoo 19)

Place modules in `addons/<technical_name>/` (lowercase, underscores).

```
<technical_name>/
├── __init__.py              # import models; define hooks here if needed
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── <model>.py
├── views/
│   └── <model>_views.xml
├── security/
│   └── ir.model.access.csv
├── data/                    # optional XML data (xmlids → clean uninstall)
│   └── neutralize.sql       # only if secrets / live outbound APIs (not in manifest data)
├── tests/
│   ├── __init__.py
│   └── test_*.py
└── migrations/              # only when an upgrade must transform data/schema
    └── 19.0.x.y.z/
        ├── pre-migrate.py
        └── post-migrate.py
```

Add `controllers/` or `static/src/` only when needed. OWL: [owl.md](owl.md).

Do not add `uninstall_hook`, `migrations/`, or `data/neutralize.sql` by default. Criteria: [uninstall-and-migration.md](uninstall-and-migration.md), [neutralize.md](neutralize.md).

## `__init__.py`

```python
from . import models
```

## `models/__init__.py`

```python
from . import sale_order
```

## `__manifest__.py`

```python
{
    "name": "Sale Warranty",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "summary": "Warranty days on sales orders",
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    # "uninstall_hook": "uninstall_hook",  # only if native leftovers need revert
}
```

- `depends` must include every native module you inherit (models, views, xml ids).
- List XML/CSV in load order: security → data → views.
- Put data in XML/CSV so uninstall can drop it via xmlid. Bump `version` and add `migrations/<target>/` when changing stored fields on an already shipped module.
- `data/neutralize.sql` is auto-loaded on restore/duplicate `--neutralize`. Never list it in `data`.

## New model vs inherit

See [inheritance.md](inheritance.md). Use `odoo-bin scaffold` only as a file stub; still apply Odoo 19 view rules in [views-odoo19.md](views-odoo19.md).
