#!/bin/bash
# ============================================================
#  Pierinelli ERP - arranque auto-inicializador (Render / Docker)
#  - 1er deploy: crea BD + instala modulos + demo + idioma.
#  - Deploys siguientes: si cambio el codigo, actualiza modulos
#    (recarga plantillas y recompila assets). Detecta el cambio
#    por el commit de git (RENDER_GIT_COMMIT).
#  - Guarda adjuntos en la BD (Render free no tiene disco).
# ============================================================
set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"
DB_NAME="${DB_NAME:-pierinelli}"
HTTP_PORT="${PORT:-8069}"
CODE_VERSION="${RENDER_GIT_COMMIT:-${CODE_VERSION:-manual}}"
MODULES="pierinelli_branding,pierinelli_data,pierinelli_pe,pierinelli_reportes,pierinelli_almacenes,pierinelli_planchas,pierinelli_mcp_inventario,web_responsive,crm,account_edi,stock_landed_costs"
SEED_PATH="/usr/local/bin/seed_pe.py"

DB_ARGS="--db_host=${DB_HOST} --db_port=${DB_PORT} --db_user=${DB_USER} --db_password=${DB_PASSWORD}"

echo ">>> Esperando PostgreSQL en ${DB_HOST}:${DB_PORT} ..."
python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import socket
import sys
import time

import psycopg2

host, port, user, pwd, db = sys.argv[1:6]

# En Render el usuario solo accede a SU base; probamos con la base del proyecto
# y como respaldo con 'postgres'.
ultimo = None
fallo_dns = False

for _ in range(60):
    # Separar "no resuelve el nombre" de "no conecta / credenciales": son
    # problemas distintos y el mensaje generico no dejaba saber cual era.
    try:
        socket.getaddrinfo(host, None)
        fallo_dns = False
    except socket.gaierror as e:
        fallo_dns, ultimo = True, e
        time.sleep(2)
        continue

    for dbname in (db, "postgres"):
        try:
            psycopg2.connect(host=host, port=port, user=user, password=pwd,
                             dbname=dbname, connect_timeout=5).close()
            print("PostgreSQL listo (%s)" % dbname)
            sys.exit(0)
        except Exception as e:
            ultimo = e
    time.sleep(2)

print("")
print("=" * 68)
if fallo_dns:
    print("ERROR: el hostname '%s' NO RESUELVE." % host)
    print("No es un problema de usuario ni de contrasena: el contenedor no")
    print("encuentra la base. Causas, de mas a menos probable:")
    print("")
    print("  1. LA BASE Y EL SERVICIO WEB ESTAN EN REGIONES DISTINTAS.")
    print("     El hostname interno (dpg-xxxxxxxx-a) solo resuelve dentro de")
    print("     la MISMA region. Comprueba la region de los dos en Render y")
    print("     ponlas iguales (ver 'region' en render.yaml).")
    print("")
    print("  2. La base fue borrada o expiro (el Postgres free de Render")
    print("     caduca a los ~30 dias). Si ya no aparece en el dashboard,")
    print("     crea una nueva y vuelve a aplicar el blueprint.")
    print("")
    print("  3. El servicio web se creo a mano y no por el blueprint, asi")
    print("     que DB_HOST no se rellena solo.")
    print("")
    print("  ALTERNATIVA si necesitas cruzar regiones: en el dashboard, pon")
    print("  DB_HOST manualmente al hostname EXTERNO de la base, con la forma")
    print("  dpg-xxxxxxxx-a.<region>-postgres.render.com")
else:
    print("ERROR: el hostname resuelve pero no se pudo conectar.")
    print("Revisa usuario, contrasena, puerto y que la base este activa.")
print("Ultimo error: %s" % ultimo)
print("=" * 68)
sys.exit(1)
PYEOF

# ============================================================
#  Reset opcional de la BD (RESET_DB)
# ------------------------------------------------------------
#  Para volver a empezar con datos limpios SIN borrar la base en Render (que
#  cambiaria el hostname y las credenciales). Se pone RESET_DB con cualquier
#  valor en las variables de entorno del servicio.
#
#  Funciona como TOKEN, no como interruptor: el valor usado queda guardado en
#  la BD y solo se borra cuando CAMBIA. Asi, dejarse RESET_DB=1 puesto no
#  destruye los datos en cada deploy; para borrar otra vez se pone otro valor
#  (RESET_DB=2). Sin esto, olvidarse la variable puesta seria una bomba.
#
#  No se hace DROP DATABASE porque en Render el rol no es dueno del cluster y
#  ademas estaria conectado a ella.
#
#  TAMPOCO se hace "DROP SCHEMA public CASCADE": Odoo tiene ~900 tablas y ese
#  CASCADE las borra en UNA transaccion, tomando un lock por objeto. Postgres
#  se queda sin tabla de locks y aborta con:
#      OutOfMemory: out of shared memory
#      HINT: You might need to increase max_locks_per_transaction
#  En Render ese parametro es gestionado y no se puede subir. Por eso se borra
#  POR LOTES, cada lote en su propia transaccion (autocommit).
# ============================================================
if [ -n "${RESET_DB}" ]; then
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" "$RESET_DB" <<'PYEOF'
import sys

import psycopg2
from psycopg2 import sql

host, port, user, pwd, db, token = sys.argv[1:7]

try:
    con = psycopg2.connect(host=host, port=port, user=user, password=pwd,
                           dbname=db, connect_timeout=10)
except Exception as e:
    print(">>> RESET_DB omitido (no se pudo conectar): %s" % e)
    sys.exit(0)

con.autocommit = True
cur = con.cursor()

# ¿Ya se aplico este mismo token? Entonces no hay nada que borrar.
anterior = None
try:
    cur.execute("SELECT value FROM ir_config_parameter "
                "WHERE key = 'pierinelli.reset_token'")
    fila = cur.fetchone()
    anterior = fila[0] if fila else None
except Exception:
    con.rollback()  # la tabla aun no existe: base vacia

if anterior == token:
    print(">>> RESET_DB='%s' ya aplicado antes; no se borra nada." % token)
    con.close()
    sys.exit(0)

print(">>> RESET_DB='%s' (antes '%s'): BORRANDO el contenido de '%s' ..."
      % (token, anterior, db))

LOTE = 50          # objetos por transaccion: holgado para max_locks_per_transaction
MAX_VUELTAS = 40   # tope de seguridad para no girar indefinidamente


def listar(consulta):
    cur.execute(consulta)
    return [fila[0] for fila in cur.fetchall()]


def borrar_en_lotes(nombres, tipo):
    """DROP por lotes; cada lote es su propia transaccion (autocommit)."""
    for i in range(0, len(nombres), LOTE):
        grupo = nombres[i:i + LOTE]
        cur.execute(sql.SQL("DROP {} IF EXISTS {} CASCADE").format(
            sql.SQL(tipo),
            sql.SQL(", ").join(sql.Identifier("public", n) for n in grupo)))


SQL_TABLAS = "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
SQL_VISTAS = ("SELECT table_name FROM information_schema.views "
              "WHERE table_schema = 'public'")
SQL_SECUENCIAS = ("SELECT sequence_name FROM information_schema.sequences "
                  "WHERE sequence_schema = 'public'")
SQL_TIPOS = ("SELECT t.typname FROM pg_type t "
             "JOIN pg_namespace n ON n.oid = t.typnamespace "
             "WHERE n.nspname = 'public' AND t.typtype = 'e'")

# Las vistas primero (dependen de tablas). Luego tablas, repitiendo: un CASCADE
# puede arrastrar objetos y cambiar lo que queda.
borrar_en_lotes(listar(SQL_VISTAS), "VIEW")

total = 0
for vuelta in range(MAX_VUELTAS):
    tablas = listar(SQL_TABLAS)
    if not tablas:
        break
    total += len(tablas)
    borrar_en_lotes(tablas, "TABLE")
else:
    print(">>> AVISO: quedaron tablas sin borrar tras %d vueltas." % MAX_VUELTAS)

borrar_en_lotes(listar(SQL_SECUENCIAS), "SEQUENCE")
borrar_en_lotes(listar(SQL_TIPOS), "TYPE")

restantes = len(listar(SQL_TABLAS))
con.close()
if restantes:
    print(">>> ERROR: siguen existiendo %d tablas; no se vacio la base."
          % restantes)
    sys.exit(1)
print(">>> Base vaciada (%d tablas). Se reinstalara todo desde cero en este "
      "mismo arranque." % total)
PYEOF
fi

# ¿La BD ya esta inicializada?
INIT=$(python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db = sys.argv[1:6]
try:
    c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db, connect_timeout=5)
    cur = c.cursor()
    cur.execute("select 1 from information_schema.tables where table_name='ir_module_module' limit 1")
    print("yes" if cur.fetchone() else "no"); c.close()
except Exception:
    print("no")
PYEOF
)

# Lee la version de codigo guardada en la BD
get_version() {
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db = sys.argv[1:6]
try:
    c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db, connect_timeout=5)
    cur = c.cursor()
    cur.execute("select value from ir_config_parameter where key='pierinelli.code_version' limit 1")
    r = cur.fetchone(); print(r[0] if r else ""); c.close()
except Exception:
    print("")
PYEOF
}

# Guarda la version de codigo actual en la BD
set_version() {
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" "$CODE_VERSION" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db, ver = sys.argv[1:7]
c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
cur = c.cursor()
cur.execute("""insert into ir_config_parameter(key, value) values('pierinelli.code_version', %s)
               on conflict(key) do update set value=excluded.value""", (ver,))
c.commit(); c.close()
PYEOF
}

# Deja constancia del RESET_DB ya aplicado, para que el mismo valor no vuelva a
# borrar la base en el siguiente deploy (ver el bloque RESET_DB de mas arriba).
set_reset_token() {
    [ -n "${RESET_DB}" ] || return 0
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" "$RESET_DB" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db, token = sys.argv[1:7]
c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
cur = c.cursor()
cur.execute("""insert into ir_config_parameter(key, value) values('pierinelli.reset_token', %s)
               on conflict(key) do update set value=excluded.value""", (token,))
c.commit(); c.close()
PYEOF
}

run_seed() {
    echo ">>> Ejecutando seed (contabilidad PE + datos con IGV) ..."
    odoo shell ${DB_ARGS} -d "${DB_NAME}" < "${SEED_PATH}"
}

# Limpia restos del antiguo modulo hebrea_website (extraido del repo). Si la BD
# lo tiene registrado como instalado pero el codigo ya no existe, Odoo falla con
# "Some modules are not loaded ... ['hebrea_website']". Aqui se neutraliza por
# SQL (idempotente) y se desinstala 'website' para dejar Pierinelli puro.
cleanup_hebrea() {
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db = sys.argv[1:6]
try:
    c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
    cur = c.cursor()
    cur.execute("SELECT state FROM ir_module_module WHERE name='hebrea_website'")
    r = cur.fetchone()
    if r and r[0] not in ('uninstalled', 'uninstallable'):
        # vistas que creo el modulo (quedarian huerfanas y romperian el sitio)
        cur.execute("""DELETE FROM ir_ui_view WHERE id IN
                       (SELECT res_id FROM ir_model_data
                        WHERE module='hebrea_website' AND model='ir.ui.view')""")
        cur.execute("DELETE FROM ir_model_data WHERE module='hebrea_website'")
        cur.execute("UPDATE ir_module_module SET state='uninstalled' WHERE name='hebrea_website'")
        c.commit()
        print(">>> hebrea_website neutralizado (uninstalled + vistas eliminadas)")
    c.close()
except Exception as e:
    print(">>> cleanup hebrea omitido: %s" % e)
PYEOF
}

# Devuelve el estado del modulo website en la BD
website_state() {
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db = sys.argv[1:6]
try:
    c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
    cur = c.cursor()
    cur.execute("SELECT state FROM ir_module_module WHERE name='website'")
    r = cur.fetchone(); print(r[0] if r else "absent"); c.close()
except Exception:
    print("absent")
PYEOF
}

uninstall_website() {
    echo ">>> Desinstalando modulo 'website' (Pierinelli puro) ..."
    odoo shell ${DB_ARGS} -d "${DB_NAME}" <<'PYSHELL' || true
mod = env['ir.module.module'].search([('name', '=', 'website'), ('state', '=', 'installed')])
if mod:
    try:
        mod.button_immediate_uninstall()
        env.cr.commit()
        print(">>> website desinstalado")
    except Exception as e:
        print(">>> no se pudo desinstalar website: %s" % e)
else:
    print(">>> website ya no esta instalado")
PYSHELL
}

# Guarda los adjuntos en la BD, porque Render free NO tiene disco persistente:
# el filestore vive en el contenedor y desaparece en cada deploy/reinicio.
#
# Se hace por SQL y no con "odoo shell" a proposito: shell arranca el registro
# completo (~30 s en free) solo para escribir una fila.
#
# CRITICO: hay que llamarlo ANTES de instalar los modulos. Todo adjunto creado
# mientras el parametro no esta puesto se escribe en el filestore del disco; al
# reiniciarse el contenedor esos ficheros ya no existen y la BD queda con filas
# apuntando a la nada -> el log se llena de:
#     FileNotFoundError: '/var/lib/odoo/filestore/<db>/xx/xxxxxxxx'
set_attachments_db() {
    echo ">>> Configurando adjuntos en la BD ..."
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db = sys.argv[1:6]
c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
cur = c.cursor()
cur.execute("""insert into ir_config_parameter(key, value)
               values('ir_attachment.location', 'db')
               on conflict(key) do update set value = excluded.value""")
c.commit(); c.close()
PYEOF
}

# Mueve a la BD los adjuntos que quedaron en el filestore de disco. Aun con el
# orden corregido, la instalacion de 'base' crea unos pocos (banderas de idioma,
# iconos de menu) ANTES de que exista ir_config_parameter. Hay que migrarlos EN
# ESTE MISMO ARRANQUE, mientras sus ficheros todavia existen: tras un redeploy
# ya no estarian (y los iconos de menu no se regeneran solos, a diferencia de
# los bundles de assets).
migrate_disk_attachments() {
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import os
import sys

import psycopg2

host, port, user, pwd, db = sys.argv[1:6]
RAIZ = os.environ.get('ODOO_DATA_DIR', '/var/lib/odoo')

c = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
cur = c.cursor()
cur.execute("SELECT id, store_fname FROM ir_attachment "
            "WHERE store_fname IS NOT NULL")
migrados = perdidos = 0
for att_id, fname in cur.fetchall():
    ruta = os.path.join(RAIZ, 'filestore', db, fname)
    try:
        with open(ruta, 'rb') as f:
            datos = f.read()
    except OSError:
        perdidos += 1
        continue
    cur.execute("UPDATE ir_attachment SET db_datas = %s, store_fname = NULL "
                "WHERE id = %s", (psycopg2.Binary(datos), att_id))
    migrados += 1
c.commit(); c.close()
if migrados or perdidos:
    print(">>> Adjuntos migrados del disco a la BD: %d (ilegibles: %d)"
          % (migrados, perdidos))
PYEOF
}

# Repara las BD que ya venian de antes: borra los bundles de assets cuyo fichero
# se perdio con el filestore efimero. Son regenerables por definicion, asi que
# Odoo los vuelve a crear (ya en la BD) al primer acceso; sin esto, cada arranque
# escupe un traceback por cada uno. Solo se tocan adjuntos de assets
# (res_model='ir.ui.view', res_id=0, public, url /web/assets/...) y solo si el
# fichero REALMENTE no esta: nunca se borra un adjunto de negocio.
repair_filestore() {
    python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import os
import sys

import psycopg2

host, port, user, pwd, db = sys.argv[1:6]
RAIZ = os.environ.get('ODOO_DATA_DIR', '/var/lib/odoo')

try:
    c = psycopg2.connect(host=host, port=port, user=user, password=pwd,
                         dbname=db, connect_timeout=10)
except Exception as e:
    print(">>> Reparacion de filestore omitida (sin conexion): %s" % e)
    sys.exit(0)

cur = c.cursor()
cur.execute("""SELECT id, store_fname FROM ir_attachment
                WHERE res_model = 'ir.ui.view' AND res_id = 0
                  AND public = true AND url LIKE '/web/assets/%%'
                  AND store_fname IS NOT NULL""")
huerfanos = [
    fila[0] for fila in cur.fetchall()
    if not os.path.exists(os.path.join(RAIZ, 'filestore', db, fila[1]))
]

if huerfanos:
    cur.execute("DELETE FROM ir_attachment WHERE id = ANY(%s)", (huerfanos,))
    c.commit()
    print(">>> Filestore: %d bundles de assets huerfanos eliminados "
          "(Odoo los regenera solo)." % len(huerfanos))
c.close()
PYEOF
}

# Los tableros estandar de Odoo guardan su definicion JSON como un adjunto.
# Algunas BDs creadas antes de configurar ``ir_attachment.location = db``
# conservan ese adjunto en el filestore efimero de Render. A diferencia de los
# bundles, si se elimina sin mas el tablero queda sin JSON y responde 500.
# Reponemos solamente los cuatro tableros distribuidos por Odoo desde los JSON
# que ya vienen dentro de la imagen; no se toca ningun tablero creado por un
# usuario ni adjuntos de negocio.
repair_standard_dashboards() {
    odoo shell ${DB_ARGS} -d "${DB_NAME}" <<'PYSHELL'
import base64
import os

from odoo.tools import file_open

dashboard_sources = {
    'spreadsheet_dashboard_account.dashboard_invoicing':
        'spreadsheet_dashboard_account/data/files/invoicing_dashboard.json',
    'spreadsheet_dashboard_stock_account.spreadsheet_dashboard_warehouse_metrics':
        'spreadsheet_dashboard_stock_account/data/files/warehouse_metrics_dashboard.json',
    'spreadsheet_dashboard_sale.spreadsheet_dashboard_sales':
        'spreadsheet_dashboard_sale/data/files/sales_dashboard.json',
    'spreadsheet_dashboard_sale.spreadsheet_dashboard_product':
        'spreadsheet_dashboard_sale/data/files/product_dashboard.json',
}

data_dir = '/var/lib/odoo'
repaired = []
for xmlid, source in dashboard_sources.items():
    dashboard = env.ref(xmlid, raise_if_not_found=False)
    if not dashboard:
        continue
    attachment = env['ir.attachment'].search([
        ('res_model', '=', 'spreadsheet.dashboard'),
        ('res_field', '=', 'spreadsheet_binary_data'),
        ('res_id', '=', dashboard.id),
    ], limit=1)
    missing = not attachment or (
        attachment.store_fname and not attachment.db_datas and
        not os.path.exists(os.path.join(data_dir, 'filestore', env.cr.dbname,
                                        attachment.store_fname))
    )
    if missing:
        with file_open(source, 'rb') as stream:
            dashboard.write({'spreadsheet_binary_data': base64.b64encode(stream.read())})
        repaired.append(dashboard.name)

if repaired:
    env.cr.commit()
    print('>>> Tableros estandar reparados en PostgreSQL: %s' % ', '.join(repaired))
PYSHELL
}

if [ "$INIT" != "yes" ]; then
    # 'base' primero y solo: crea ir_config_parameter para poder mandar los
    # adjuntos a la BD ANTES de que la instalacion de los demas modulos genere
    # los primeros ficheros en el filestore efimero (ver set_attachments_db).
    echo ">>> Preparando '${DB_NAME}': modulo base ..."
    odoo ${DB_ARGS} -d "${DB_NAME}" -i base --stop-after-init
    set_attachments_db
    echo ">>> Instalando modulos + idioma (puede tardar) ..."
    odoo ${DB_ARGS} -d "${DB_NAME}" -i "${MODULES}" --load-language=es_419 --stop-after-init
    migrate_disk_attachments
    run_seed
    set_version
    set_reset_token
    echo ">>> Inicializacion completa."
else
    # BD anterior al cambio de orden: primero rescatar lo que aun exista en el
    # disco de ESTE contenedor, luego limpiar los assets cuyo fichero ya se
    # perdio (Odoo los regenera en la BD).
    set_attachments_db
    migrate_disk_attachments
    repair_filestore
    repair_standard_dashboards
    # Limpieza de restos de hebrea_website (no-op si la BD ya esta limpia)
    cleanup_hebrea
    if [ "$(website_state)" = "installed" ]; then
        uninstall_website
    fi
    STORED=$(get_version)
    if [ "$STORED" != "$CODE_VERSION" ]; then
        echo ">>> Codigo nuevo (${CODE_VERSION}, antes '${STORED}') -> instalando/actualizando modulos ..."
        odoo ${DB_ARGS} -d "${DB_NAME}" -i "${MODULES}" -u "${MODULES}" --stop-after-init
        run_seed
        set_version
        set_reset_token
        echo ">>> Actualizacion completa."
    else
        echo ">>> Codigo sin cambios, omitiendo actualizacion."
        # El token se guarda igualmente: si la BD ya estaba limpia y no hubo
        # cambios de codigo, RESET_DB no debe re-disparar en el proximo deploy.
        set_reset_token
    fi
fi

echo ">>> Iniciando servidor Odoo en el puerto ${HTTP_PORT} ..."
exec odoo ${DB_ARGS} -d "${DB_NAME}" --db-filter="^${DB_NAME}$" --http-port="${HTTP_PORT}" "$@"
