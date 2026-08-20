# Inheritance

Prefer extension. Do not duplicate native classes or view architectures.

## Model: extension (`_inherit` only)

Adds fields/methods on the same model and table.

```python
from odoo import fields, models

class SaleOrder(models.Model):
    _inherit = "sale.order"

    warranty_days = fields.Integer(string="Warranty (days)")
```

Resolve `_inherit` / xml ids with `find_model.py` and Grep. Overrides must call `super()`. Extra fields uninstall with the module. Renaming or changing the type of a stored field on a shipped module needs `migrations/` — [uninstall-and-migration.md](uninstall-and-migration.md). Extra stored secrets or prod flags on a native table need `data/neutralize.sql` — [neutralize.md](neutralize.md).

## Model: new (`_name`)

```python
class EquipmentItem(models.Model):
    _name = "equipment.item"
    _description = "Equipment item"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True)
```

## Prototype (`_name` + `_inherit` of a concrete model)

Copies the parent model into a **new** table. Rare. Only when you truly need a separate model.

## Delegation (`_inherits`)

`_inherits = {"parent.model": "parent_id"}` with a required `Many2one`. Use the same pattern as the native file you opened (e.g. `product.product` → `product.template`).

## View inherit

`inherit_id` + `xpath` / field `position`. See [views-odoo19.md](views-odoo19.md). Grep `model="ir.ui.view"` in the native module for the xml id; do not guess `sale.view_order_form` without a hit.
