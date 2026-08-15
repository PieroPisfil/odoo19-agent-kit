# Module skeleton (Odoo 19)

Place modules in `custom_addons/<technical_name>/` (lowercase, underscores).

```
<technical_name>/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── <model>.py
├── views/
│   └── <model>_views.xml
├── security/
│   └── ir.model.access.csv
└── data/                    # optional XML data
```

Add `controllers/` or `static/src/` only when needed. OWL: [owl.md](owl.md).

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
}
```

- `depends` must include every native module you inherit (models, views, xml ids).
- List XML/CSV in load order: security → data → views.

## New model vs inherit

See [inheritance.md](inheritance.md). Use `odoo-bin scaffold` only as a file stub; still apply Odoo 19 view rules in [views-odoo19.md](views-odoo19.md).
