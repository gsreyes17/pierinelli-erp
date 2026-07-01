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
MODULES="pierinelli_branding,pierinelli_data,pierinelli_pe,web_responsive,mrp"
SEED_PATH="/usr/local/bin/seed_pe.py"

DB_ARGS="--db_host=${DB_HOST} --db_port=${DB_PORT} --db_user=${DB_USER} --db_password=${DB_PASSWORD}"

echo ">>> Esperando PostgreSQL en ${DB_HOST}:${DB_PORT} ..."
python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" <<'PYEOF'
import sys, time, psycopg2
host, port, user, pwd = sys.argv[1:5]
for _ in range(60):
    try:
        psycopg2.connect(host=host, port=port, user=user, password=pwd,
                         dbname="postgres", connect_timeout=3).close()
        print("PostgreSQL listo"); sys.exit(0)
    except Exception:
        time.sleep(2)
print("ERROR: no se pudo conectar a PostgreSQL"); sys.exit(1)
PYEOF

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

run_seed() {
    echo ">>> Ejecutando seed (contabilidad PE + datos con IGV) ..."
    odoo shell ${DB_ARGS} -d "${DB_NAME}" < "${SEED_PATH}"
}

migrate_attachments() {
    echo ">>> Migrando adjuntos a la BD (persistencia sin disco) ..."
    odoo shell ${DB_ARGS} -d "${DB_NAME}" <<'PYSHELL'
env['ir.config_parameter'].sudo().set_param('ir_attachment.location', 'db')
env['ir.attachment'].sudo().search([]).force_storage()
env.cr.commit()
PYSHELL
}

if [ "$INIT" != "yes" ]; then
    echo ">>> Inicializando '${DB_NAME}': modulos + idioma (puede tardar) ..."
    odoo ${DB_ARGS} -d "${DB_NAME}" -i "${MODULES}" --load-language=es_419 --stop-after-init
    run_seed
    migrate_attachments
    set_version
    echo ">>> Inicializacion completa."
else
    STORED=$(get_version)
    if [ "$STORED" != "$CODE_VERSION" ]; then
        echo ">>> Codigo nuevo (${CODE_VERSION}, antes '${STORED}') -> instalando/actualizando modulos ..."
        odoo ${DB_ARGS} -d "${DB_NAME}" -i "${MODULES}" -u "${MODULES}" --stop-after-init
        run_seed
        migrate_attachments
        set_version
        echo ">>> Actualizacion completa."
    else
        echo ">>> Codigo sin cambios, omitiendo actualizacion."
    fi
fi

echo ">>> Iniciando servidor Odoo en el puerto ${HTTP_PORT} ..."
exec odoo ${DB_ARGS} -d "${DB_NAME}" --db-filter="^${DB_NAME}$" --http-port="${HTTP_PORT}" "$@"
