# Views (Odoo 19)

## list, not tree

```xml
<field name="view_mode">list,form</field>
```

```xml
<list string="Orders">
    <field name="name"/>
    <field name="partner_id"/>
</list>
```

## Modifiers: attributes, not `attrs`

```xml
<field name="warranty_days" invisible="not partner_id" readonly="state == 'done'" required="state == 'sale'"/>
```

Do not use `attrs="{...}"` or `states="draft,sale"`.

## Inherit a native form

```xml
<record id="view_order_form_warranty" model="ir.ui.view">
    <field name="name">sale.order.form.warranty</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='date_order']" position="after">
            <field name="warranty_days"/>
        </xpath>
    </field>
</record>
```

Grep the native view file for the target field/`name` before writing xpath. Prefer `position="after|before|inside"` on a stable field.

## Search

```xml
<search>
    <field name="name"/>
    <filter string="Confirmed" name="confirmed" domain="[('state', '=', 'sale')]"/>
    <group>
        <filter string="Customer" name="group_partner" context="{'group_by': 'partner_id'}"/>
    </group>
</search>
```

## Chatter (only if the model mixes `mail.thread`)

```xml
<chatter/>
```

Confirm against a native 19.0 form of a `mail.thread` model before adding chatter; do not invent legacy `oe_chatter` wrappers unless that native file still uses them.

## Menus

```xml
<menuitem id="menu_equipment_root" name="Equipment" sequence="50"/>
<menuitem id="menu_equipment_items" name="Items" parent="menu_equipment_root" action="action_equipment_item" sequence="10"/>
```
