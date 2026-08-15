# Security

Every new `_name` model needs ACL. `_inherit` of an existing model usually does **not** need a new `ir.model.access.csv` row unless you add a new model.

## `security/ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_equipment_item_user,equipment.item.user,model_equipment_item,base.group_user,1,1,1,0
access_equipment_item_manager,equipment.item.manager,model_equipment_item,base.group_system,1,1,1,1
```

- `model_<name_with_underscores>`: `equipment.item` → `model_equipment_item`.
- List this file in `__manifest__.py` `data` **before** views.

## Record rules (optional)

```xml
<record id="equipment_item_comp_rule" model="ir.rule">
    <field name="name">Equipment: multi-company</field>
    <field name="model_id" ref="model_equipment_item"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="global" eval="True"/>
</record>
```

Copy domain style from a native `ir.rule` on a similar model (Grep `model="ir.rule"` in that addon). Put rules in `security/<module>_security.xml` and list it before the CSV if groups are defined there.

## Groups

Define `res.groups` in XML only when the module needs its own permission group. Otherwise reuse `base.group_user` / the parent app's groups (e.g. `sales_team.group_sale_manager`). Grep `res.groups` in the depended native module.
