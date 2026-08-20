# Neutralize (local test databases)

Odoo runs `{module}/data/neutralize.sql` when a database is duplicated or restored with neutralization, or via `odoo neutralize -d <db>`. Path is hardcoded in `odoo-src/odoo/modules/neutralize.py`. The file is **not** listed in `__manifest__.py` `data` (that would execute it on every install).

Apply this on **every** create or edit. Most modules need no file. If the module can send mail, hit live APIs, or store secrets, write `data/neutralize.sql`.

## When to add it

Write the file if the module, after a production dump is copied locally, could still:

- Call a live API (EDI, payment, SMS, IAP, OAuth, shipping, cloud storage, custom HTTP)
- Keep API keys, tokens, passwords, certificates, or webhook URLs in `ir.config_parameter` or custom fields
- Keep a **production** flag (`prod_environment`, provider `state`, `edi_mode`, live endpoints)
- Own outgoing connectors that `base` / `mail` / `payment` do not already disable

Do **not** add it for extra fields, views, ACLs, or business documents with no outbound side effects.

`base` already deactivates `ir.mail_server`, almost all crons, webhooks on `ir.actions.server`, and sets `database.is_neutralized`. Do not repeat that. Neutralize **this module's** leftovers only. Copy style from a native file that does the same job (`mail`, `payment`, `cloud_storage_google`, `delivery`).

## File

```
addons/<module>/data/neutralize.sql
```

Idempotent SQL only (safe to run twice). Disable or dummy secrets; do not drop tables or delete orders/invoices.

```sql
-- disable live integration
UPDATE my_backend
   SET prod_environment = false,
       api_token = NULL
 WHERE api_token IS NOT NULL;

DELETE FROM ir_config_parameter
 WHERE key IN ('my_module.api_key', 'my_module.webhook_url');
```

Rules:

- Tables/columns must exist when the module is installed (the loader only opens the file for installed modules).
- Prefer `UPDATE` / `DELETE … WHERE` / dummy values. `INSERT … ON CONFLICT` if you must insert a flag.
- Do not put `neutralize.sql` in manifest `data`.
- Do not neutralize other modules' columns unless this module added them (`_inherit` fields on native tables: yes, neutralize those).

## Checklist

```
Neutralize:
- [ ] Module holds secrets or talks to an external system → data/neutralize.sql
- [ ] File is NOT in __manifest__.py data
- [ ] SQL is idempotent and does not destroy business records
- [ ] Does not duplicate base/mail cron/mail-server neutralization
```

If there is nothing outbound: **no file**. Mention that when closing the task.
