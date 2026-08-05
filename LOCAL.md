# Ejecutar en LOCAL (Windows / PowerShell)

Requisitos ya instalados: Python 3.11 (`.venv`), PostgreSQL, BD `odoo`.

## Solo arrancar (si la BD ya está cargada)
```powershell
.\arrancar.ps1
```
→ http://localhost:8069 · detener con `Ctrl+C`.
El script `arrancar.ps1` asegura que **wkhtmltopdf** esté en el PATH (para los PDF)
y luego lanza Odoo. Equivale a `.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf`
más el ajuste del PATH.

> **PDF en local:** requieren **wkhtmltopdf 0.12.6 (patched qt)**. En Render/Docker ya
> viene en la imagen `odoo:19`; en Windows se instala una vez:
> ```powershell
> # El release 0.12.6-1 es el ultimo con build de Windows (los posteriores solo traen
> # .deb/.rpm). /S = silencioso, /D = destino (debe ir al final y SIN comillas).
> .\wkhtmltox-0.12.6-1.msvc2015-win64.exe /S /D=E:\DevTools\wkhtmltopdf
> ```
> Descarga: github.com/wkhtmltopdf/packaging/releases/tag/0.12.6-1
> `arrancar.ps1` busca primero `E:\DevTools\wkhtmltopdf\bin` y luego `C:\Program Files\wkhtmltopdf\bin`.

## Cargar todo desde cero (BD limpia + datos)
```powershell
# 0) Detén Odoo (Ctrl+C)

# 1) Recrear la BD limpia  (la clave del rol 'odoo' esta en odoo.conf)
$env:PGPASSWORD='<clave-del-rol-odoo>'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U odoo -h localhost -d postgres -c "DROP DATABASE IF EXISTS odoo;"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U odoo -h localhost -d postgres -c "CREATE DATABASE odoo TEMPLATE template0 ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C';"

# 2) Instalar módulos + idioma
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf -d odoo -i pierinelli_branding,pierinelli_data,pierinelli_pe,pierinelli_reportes,pierinelli_almacenes,pierinelli_planchas,pierinelli_mcp_inventario,web_responsive,crm,account_edi --load-language=es_419 --stop-after-init

# 3) Cargar datos (catálogo real + IGV + facturas + pagos + usuarios)
#    OJO: se usa cmd, porque PowerShell NO acepta "<"
cmd /c ".venv\Scripts\python.exe odoo\odoo-bin shell -c odoo.conf -d odoo < seed_pe.py"

# 4) Arrancar
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf
```
El paso 3 debe terminar con `SEED COMPLETO` (con la versión vigente de `SEED_VERSION`).

## Instalar en otro disco / otra máquina (desde cero)

`odoo/`, `.venv/` y `odoo.conf` **no viajan por git** — se recrean así:

```powershell
# 1) El proyecto
git clone https://github.com/gsreyes17/pierinelli-erp.git Pierinelli
cd Pierinelli

# 2) Núcleo Odoo 19 (--depth 1 ahorra ~2 GB)
git clone --branch 19.0 --depth 1 https://github.com/odoo/odoo.git odoo

# 3) Entorno Python (requiere Python 3.11)
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r odoo\requirements.txt

# 4) Rol de PostgreSQL dedicado — Odoo ABORTA si db_user es el superusuario
#    ("Using the database user 'postgres' is a security risk, aborting").
#    Hay que crear un rol propio con CREATEDB:
$env:PGPASSWORD='<clave-del-superusuario-postgres>'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h localhost -d postgres `
  -c "CREATE ROLE odoo WITH LOGIN CREATEDB PASSWORD '<clave-del-rol-odoo>';"

# 5) odoo.conf: copiarlo de la instalación anterior (tiene credenciales,
#    está en .gitignore). Si no existe, crear uno con esta plantilla:
#      [options]
#      addons_path = <ruta>\odoo\addons,<ruta>\custom_addons
#      data_dir    = <ruta>\.odoo_data
#      db_host = localhost / db_port = 5432
#      db_user = odoo / db_password = <clave> / db_name = odoo
#      list_db = True / workers = 0 / limit_time_cpu = 0 / limit_time_real = 0

# 6) BD + datos: seguir "Cargar todo desde cero" (arriba)
```

Requisitos del sistema (una sola vez por máquina): PostgreSQL, Python 3.11 y
`winget install wkhtmltopdf.wkhtmltox` para los PDF.
> La BD vive en Postgres (C:) y **sobrevive** a un cambio de disco del proyecto,
> pero sus adjuntos/imágenes viven en `.odoo_data/` junto al proyecto. Lo simple:
> recrear la BD con el seed en la instalación nueva.

## Usuarios de ejemplo (referencia de permisos)
Todos con contraseña **`pierinelli`**. El `admin` conserva tu contraseña.

| Login | Rol | Qué apps ve |
|---|---|---|
| `gerente` | Gerente General | Todo (responsable de Ventas, Inventario, Compras, Contabilidad) |
| `vendedor` | Vendedor | Ventas |
| `almacen` | Almacenero | Inventario |
| `compras` | Comprador | Compras |
| `contabilidad` | Contadora | Contabilidad |

> Para probar un rol: cierra sesión y entra con ese login. Verás **solo sus apps**.

## Notas
- **Odoo rechaza el usuario `postgres`**: el core aborta el arranque si `db_user` es el
  superusuario (`Using the database user 'postgres' is a security risk, aborting`).
  No hay flag para desactivarlo → siempre un rol dedicado con `LOGIN CREATEDB`.
- **PowerShell no soporta `<`** para redirigir → el seed se corre con `cmd /c "... < seed_pe.py"`
  (o `Get-Content seed_pe.py | .venv\Scripts\python.exe odoo\odoo-bin shell -c odoo.conf -d odoo`).
- Crear una BD nueva en Windows requiere `TEMPLATE template0 ... LC_COLLATE 'C' LC_CTYPE 'C'`
  (evita el error de *collation*).
- Warning "virtual real time limit … reached": es cosmético (conexiones keep-alive ociosas), no un error.
- Recargar el catálogo/datos tras cambios del seed: sube `SEED_VERSION` en `seed_pe.py` y repite el paso 3.

Para desplegar en la nube → **[RENDER.md](RENDER.md)**.
