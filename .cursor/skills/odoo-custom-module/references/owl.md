# OWL (only if the user asked for frontend)

Backend Python/XML covers most custom modules. Use this when adding JS/XML assets.

## Manifest assets

```python
"assets": {
    "web.assets_backend": [
        "my_module/static/src/**/*",
    ],
},
```

Prefer a narrow glob matching files you add. Confirm the bundle name (`web.assets_backend`, `web.assets_frontend`) against a native module that does the same kind of UI.

## Extend a component

Grep the native component `class` / `registry.category` in `odoo/addons/<module>/static/src`. Patch or subclass the same way that file does in 19.0 (do not invent legacy widget APIs).

```javascript
import { patch } from "@web/core/utils/patch";
```

## QWeb OWL templates

```xml
<templates xml:space="preserve">
    <t t-name="my_module.Flag" t-inherit="parent_addon.TemplateName" t-inherit-mode="extension">
        <xpath expr="//div[hasclass('o_target')]" position="inside">
            <span>Extra</span>
        </xpath>
    </t>
</templates>
```

Read the parent template file before xpath. Keep JS/XML diffs small.
