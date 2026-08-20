# Agente de desarrollo Odoo 19

Este proyecto es un entorno para que un agente (tú) diseñe e implemente
módulos personalizados de Odoo 19, usando el código fuente oficial como
referencia bajo demanda y una instancia Odoo real en Docker para validar
todo lo que escribe.

## Estructura del proyecto

```
odoo19_docker/
├── odoo-src/              Checkout de solo lectura de odoo/odoo rama 19.0.
│                          NUNCA se edita. Es la referencia de "cómo funciona Odoo".
├── addons/                Aquí vive TODO el código nuevo que escribes.
├── addons-third-party/    Addons de terceros (no pongas módulos del proyecto aquí).
├── config/                odoo.conf (addons_path de runtime).
├── docker-compose.yml     Stack de desarrollo (Odoo + Postgres) en la raíz del repo.
├── Dockerfile             Imagen local FROM odoo:19.0.
└── scripts/               Wrappers de docker compose para el ciclo de desarrollo.
```

Runtime: servicio `odoo19_1`, Postgres `postgres16_1`. `addons/` se monta en
`/mnt/extra-addons` y `addons-third-party/` en `/mnt/addons-third-party`.
Los addons nativos en el contenedor vienen de la imagen `odoo:19.0`, no de
`odoo-src/`.

## Cómo buscar en Odoo (sin gastar contexto de más)

`odoo-src/` es la fuente de verdad de "cómo debería comportarse Odoo". Búscalo
con Grep/Glob igual que harías con cualquier código, en vez de asumir que
conoces la API de memoria:

- Antes de usar un campo, método o modelo que no hayas visto en este proyecto,
  búscalo primero en `odoo-src/addons/<modulo>/models/` o `odoo-src/odoo/`.
- Para entender qué hereda o extiende un modelo, busca `_inherit = "modelo.x"`
  y `_name = "modelo.x"` en `odoo-src/addons/**`.
- Lee solo los fragmentos relevantes (rangos de líneas), no el archivo completo
  si es muy largo, salvo que lo necesites para entender el contexto.
- Los tests nativos (`odoo-src/addons/<modulo>/tests/`) son a menudo la mejor
  documentación de cómo se espera usar una API — revísalos cuando la duda sea
  sobre el "flujo correcto" y no solo sobre la firma de un método.
- Para saber qué campos tiene un modelo **en tu instalación real** (incluyendo
  módulos custom instalados), no leas código: ejecuta
  `scripts/inspect-model.ps1 -Model sale.order`. Es más barato y siempre
  exacto porque consulta `fields_get()` contra la instancia viva, en vez de
  mantener un índice aparte que se puede desincronizar.
- `find_model.py` puede imprimir `FILE` con prefijo `odoo/`; abre la misma ruta
  bajo `odoo-src/` (`odoo/addons/...` → `odoo-src/addons/...`,
  `odoo/odoo/addons/...` → `odoo-src/odoo/addons/...`).

No copies módulos nativos completos al contexto ni los repitas en tus
respuestas. Trae solo lo que necesitas para la tarea actual.

## Reglas de desarrollo (no negociables)

- Nunca asumas que existe una API, campo o método de Odoo sin haberlo
  verificado en `odoo-src/` o con `inspect-model.ps1`. Si no lo encuentras,
  dilo explícitamente en vez de inventarlo.
- Nunca modifiques archivos dentro de `odoo-src/` ni de módulos nativos.
  Todo se hace por herencia (`_inherit`) desde `addons/`.
- Extiende vistas nativas con `<xpath>` sobre `inherit_id`, nunca reescribas
  la vista completa.
- Prefiere el ORM de Odoo sobre SQL crudo (`self.env.cr.execute`). Usa SQL
  directo solo cuando el ORM genuinamente no lo permite, y explica por qué.
- Todo modelo nuevo necesita reglas de seguridad: `ir.model.access.csv` como
  mínimo, y `record rules` si hay multi-compañía o visibilidad restringida.
- Todo módulo nuevo necesita tests (`tests/test_*.py` con `TransactionCase` o
  similar) que cubran al menos el camino feliz de la lógica de negocio nueva.
- Verifica que las dependencias reales estén declaradas en `__manifest__.py`
  (`depends`) — no asumas que un modelo está disponible porque "siempre lo
  está"; depende de qué módulos estén instalados.
- No inventes IDs XML (`<record id="...">`) de módulos nativos: búscalos en
  `odoo-src/` antes de referenciarlos (por ejemplo en herencia de vistas o
  grupos de seguridad).
- Antes de dar una tarea por terminada: instala/actualiza el módulo y corre
  sus tests contra el Odoo de desarrollo (ver abajo). No declares éxito solo
  porque el código "se ve correcto".
- Antes de terminar un alta o un cambio de módulo, aplica los criterios de
  desinstalación, migración y neutralize (skill
  `.cursor/skills/odoo-custom-module/references/uninstall-and-migration.md` y
  `neutralize.md`). Los xmlids y los campos extra del módulo los limpia Odoo.
  Un `uninstall_hook(env)` solo revierte residuos en registros nativos / ICP /
  `create()` sin xmlid, o bloquea la desinstalación. Si el módulo ya puede
  estar instalado y renombras o cambias el tipo de un campo stored: sube
  `version` (`19.0.x.y.z`) y añade `migrations/<version>/pre-migrate.py` con
  `def migrate(cr, version)`. Si el módulo guarda secretos o puede pegarle a
  APIs reales al restaurar un dump de producción en local: crea
  `data/neutralize.sql` (no lo listes en `data` del manifiesto).

## Ciclo de desarrollo (Docker local)

Instancia de desarrollo aislada — Odoo 19 + Postgres, sin acceso a producción
(no existe tal acceso configurado en este proyecto).

```powershell
# Levantar el stack (primera vez y siguientes)
scripts/up.ps1
# http://localhost:8070

# Primera vez: crear la base de datos "dev" con el módulo base
scripts/init-db.ps1

# Instalar un módulo nuevo de addons/ por primera vez
scripts/install-module.ps1 -Module nombre_del_modulo

# Después de cambiar código: actualizar el módulo
scripts/update-module.ps1 -Module nombre_del_modulo

# Actualizar y correr sus tests automáticos
scripts/test-module.ps1 -Module nombre_del_modulo

# Ver logs (últimas N líneas, o -Follow para seguir en vivo)
scripts/logs.ps1 -Lines 300

# Consultar campos reales de un modelo en la instancia viva
scripts/inspect-model.ps1 -Model sale.order

# Shell interactivo de Odoo (uso humano/exploratorio)
scripts/shell.ps1
```

Flujo esperado al implementar algo:
1. Buscar en `odoo-src/` lo necesario (modelos, métodos, vistas relacionadas).
2. Escribir el módulo en `addons/<nombre>/`.
3. `install-module.ps1` (primera vez) o `update-module.ps1` (iteraciones).
4. `test-module.ps1` y revisar la salida / `logs.ps1` si algo falla.
5. Corregir y repetir el paso 3-4 hasta que instale limpio y los tests pasen.
6. Solo entonces reportar la tarea como completa.

`scripts/reset-db.ps1 -Force` borra la base "dev" por completo — es local y
desechable, pero igual pide confirmación al usuario antes de ejecutarlo si no
fue él quien lo pidió explícitamente.

Nota técnica: `install-module.ps1`, `update-module.ps1` y `test-module.ps1`
corren en un contenedor Docker efímero (`docker compose run --rm odoo19_1`),
separado del contenedor web persistente que levanta `up.ps1`. Esto es necesario
porque Odoo fuerza el arranque de su servidor HTTP interno cuando se usa
`--test-enable`, sin importar `--no-http`, y chocaría con el puerto del
contenedor principal si se usara el mismo. Como consecuencia, el contenedor
web persistente no se entera solo de los módulos instalados/actualizados por
esos comandos — por eso los tres scripts reinician automáticamente el
contenedor `odoo19_1` al terminar. Si algún día ves el error
`KeyError: 'mi.modelo'` o un 404 al abrir la web justo después de instalar,
la causa es esta, y la solución es la misma:
`docker compose restart odoo19_1`.

## Estructura esperada de un módulo nuevo

```
addons/<nombre_modulo>/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── *.py
├── views/
│   └── *.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml        (si hace falta record rules o grupos)
├── data/                    (datos iniciales, si aplica)
│   └── neutralize.sql       (solo si hay secretos o APIs en vivo; no va en el manifiesto)
├── wizard/                  (TransientModel, si aplica)
├── tests/
│   ├── __init__.py
│   └── test_*.py
└── migrations/              (solo si un upgrade debe transformar datos/esquema)
    └── 19.0.x.y.z/
        ├── pre-migrate.py
        └── post-migrate.py
```

No añadas `uninstall_hook`, `migrations/` ni `data/neutralize.sql` por
defecto. Datos en XML/CSV (con xmlid) se desinstalan solos. El hook va en
`__init__.py` y se declara en `__manifest__.py` solo si hay residuos nativos
que revertir. `neutralize.sql` lo carga Odoo al restaurar/duplicar con
`--neutralize`; no lo pongas en la lista `data` del manifiesto.

## Notas de versión

Este proyecto está fijado a **Odoo 19.0** (`odoo-src` es un checkout shallow
de esa rama, y la imagen Docker es `odoo:19.0`). No mezcles patrones o APIs de
otras versiones de Odoo sin verificar que siguen existiendo en 19.0.
