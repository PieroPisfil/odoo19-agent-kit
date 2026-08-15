# Entorno de desarrollo Odoo 19 con agente

Guía práctica para usar este proyecto. Si buscas las reglas que sigue el
agente al escribir código, esas están en [AGENTS.md](AGENTS.md) y
[CLAUDE.md](CLAUDE.md) — este documento es para ti, el humano.

## 0. Qué es esto

```
odoo19_docker/
├── odoo-src/              Código fuente oficial de Odoo 19.0 (solo lectura, para que el agente lo consulte)
├── addons/                Tus módulos van aquí
├── addons-third-party/    Addons de terceros
├── config/                odoo.conf
├── docker-compose.yml     Odoo 19 + Postgres para desarrollo local
├── Dockerfile             Imagen local FROM odoo:19.0
├── scripts/               Comandos para instalar, actualizar, testear e inspeccionar
├── AGENTS.md / CLAUDE.md  Reglas del agente
└── README.md              Este archivo
```

No hay acceso a producción configurado en ningún lado — todo corre en Docker,
en tu máquina. El servicio web es `odoo19_1` (puerto host `8070` → contenedor
`8069`). La base de desarrollo por defecto es `dev`.

## 1. Requisitos

- Docker Desktop corriendo.
- PowerShell (los scripts son `.ps1`).

## 2. Primera vez

```powershell
scripts/up.ps1          # levanta Odoo + Postgres
scripts/init-db.ps1     # crea la base "dev" con el modulo base instalado
```

Después de esto, `http://localhost:8070` ya debería mostrar la pantalla de
login. Credenciales por defecto: usuario `admin`, contraseña `admin`.

## 3. Cómo pedirle un módulo al agente

Simplemente descríbele la funcionalidad, por ejemplo:

> "Crea un módulo que agregue un campo de margen a las líneas de venta,
> instálalo y corre los tests."

El agente (siguiendo `AGENTS.md` / `CLAUDE.md`) va a:
1. Buscar en `odoo-src/` los modelos y vistas relevantes (no te va a mostrar
   módulos nativos completos, solo lo que necesita).
2. Escribir el módulo en `addons/<nombre>/`.
3. Instalarlo y correr sus tests contra el Odoo de desarrollo.
4. Corregir y repetir hasta que todo pase, antes de decirte que terminó.

Puedes revisar el código que escribió como cualquier otro cambio en el repo
(`git diff`, tu editor, etc.) antes de confiar en él.

## 4. Comandos manuales (por si quieres hacerlo tú mismo)

| Comando | Qué hace |
|---|---|
| `scripts/up.ps1` | Levanta el stack (Odoo + Postgres) |
| `scripts/down.ps1` | Lo detiene. `-Volumes` además borra los datos |
| `scripts/init-db.ps1` | Crea la base `dev` con el módulo `base` (una sola vez) |
| `scripts/install-module.ps1 -Module <nombre>` | Instala un módulo nuevo por primera vez |
| `scripts/update-module.ps1 -Module <nombre>` | Reinstala/actualiza un módulo tras cambiar código |
| `scripts/test-module.ps1 -Module <nombre>` | Actualiza el módulo y corre sus tests automáticos |
| `scripts/logs.ps1 -Lines 200` | Muestra las últimas N líneas de log. `-Follow` para en vivo |
| `scripts/inspect-model.ps1 -Model <modelo>` | Lista los campos reales de un modelo (contra la instancia viva) |
| `scripts/shell.ps1` | Shell interactivo de Odoo (Python + ORM) |
| `scripts/reset-db.ps1 -Force` | Borra la base `dev` por completo (destructivo, local) |

Todos aceptan `-Database <nombre>` si alguna vez trabajas con otra base
además de `dev` (por defecto).

**Importante:** `install-module.ps1`, `update-module.ps1` y `test-module.ps1`
reinician automáticamente el servidor web (`odoo19_1`) al terminar, para que
los cambios se vean de inmediato en el navegador. Es normal ver "Reiniciando
el servidor web..." al final — espera unos segundos antes de recargar la
página.

## 5. Ejemplo de ciclo completo a mano

```powershell
scripts/up.ps1
scripts/init-db.ps1

# ... el modulo ya existe en addons/mi_modulo ...
scripts/install-module.ps1 -Module mi_modulo
scripts/test-module.ps1 -Module mi_modulo

# cambiaste algo en el codigo del modulo:
scripts/test-module.ps1 -Module mi_modulo   # re-instala y corre tests de nuevo

# ver que paso si algo fallo:
scripts/logs.ps1 -Lines 300

# ver los campos reales de un modelo (nativo o tuyo):
scripts/inspect-model.ps1 -Model sale.order
```

## 6. addons/

Los módulos del proyecto viven en `addons/` (por ejemplo `kaf_*`). Los addons
de terceros van en `addons-third-party/`. No copies módulos nativos de
`odoo-src/` a ninguna de esas carpetas: extiende con `_inherit`.

## 7. Problemas conocidos y cómo se resuelven

- **`KeyError: 'mi.modelo'` o 404 en el navegador justo después de instalar**:
  el servidor web no se reinició. Corre `docker compose restart odoo19_1`
  (los scripts de instalar/actualizar/testear ya lo hacen solos).
- **Docker Desktop no está corriendo**: todos los scripts van a fallar con
  errores de conexión a Docker. Ábrelo primero.
- **Quieres empezar de cero**: `scripts/reset-db.ps1 -Force` seguido de
  `scripts/init-db.ps1`.
