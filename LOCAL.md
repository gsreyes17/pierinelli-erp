# Ejecutar en LOCAL (Windows / PowerShell)

Requisitos ya instalados: Python 3.11 (`.venv`), PostgreSQL, BD `odoo`.

## Solo arrancar (si la BD ya está cargada)
```powershell
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf
```
→ http://localhost:8069 · detener con `Ctrl+C`.

## Cargar todo desde cero (BD limpia + datos)
```powershell
# 0) Detén Odoo (Ctrl+C)

# 1) Recrear la BD limpia
$env:PGPASSWORD='Odoo'
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U Odoo -h localhost -d postgres -c "DROP DATABASE IF EXISTS odoo;"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U Odoo -h localhost -d postgres -c "CREATE DATABASE odoo TEMPLATE template0 ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C';"

# 2) Instalar módulos + idioma
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf -d odoo -i pierinelli_branding,pierinelli_data,pierinelli_pe,web_responsive --load-language=es_419 --stop-after-init

# 3) Cargar datos (catálogo real + IGV + facturas + pagos + usuarios)
#    OJO: se usa cmd, porque PowerShell NO acepta "<"
cmd /c ".venv\Scripts\python.exe odoo\odoo-bin shell -c odoo.conf -d odoo < seed_pe.py"

# 4) Arrancar
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf
```
El paso 3 debe terminar con `SEED COMPLETO (version 5)`.

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
- **PowerShell no soporta `<`** para redirigir → el seed se corre con `cmd /c "... < seed_pe.py"`
  (o `Get-Content seed_pe.py | .venv\Scripts\python.exe odoo\odoo-bin shell -c odoo.conf -d odoo`).
- Crear una BD nueva en Windows requiere `TEMPLATE template0 ... LC_COLLATE 'C' LC_CTYPE 'C'`
  (evita el error de *collation*).
- Warning "virtual real time limit … reached": es cosmético (conexiones keep-alive ociosas), no un error.
- Recargar el catálogo/datos tras cambios del seed: sube `SEED_VERSION` en `seed_pe.py` y repite el paso 3.

Para desplegar en la nube → **[RENDER.md](RENDER.md)**.
