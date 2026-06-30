#!/bin/bash
# ============================================================
#  Pierinelli ERP - arranque auto-inicializador (Render / Docker)
#  - Crea la BD e instala modulos + demo + idioma en el 1er deploy.
#  - Guarda adjuntos en la BD (Render free no tiene disco persistente).
# ============================================================
set -e

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo}"
DB_NAME="${DB_NAME:-pierinelli}"
HTTP_PORT="${PORT:-8069}"

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

echo ">>> Verificando si la BD '${DB_NAME}' esta inicializada ..."
INIT=$(python3 - "$DB_HOST" "$DB_PORT" "$DB_USER" "$DB_PASSWORD" "$DB_NAME" <<'PYEOF'
import sys, psycopg2
host, port, user, pwd, db = sys.argv[1:6]
try:
    c = psycopg2.connect(host=host, port=port, user=user, password=pwd,
                         dbname=db, connect_timeout=5)
    cur = c.cursor()
    cur.execute("select 1 from information_schema.tables where table_name='ir_module_module' limit 1")
    print("yes" if cur.fetchone() else "no")
    c.close()
except Exception:
    print("no")
PYEOF
)

if [ "$INIT" != "yes" ]; then
    echo ">>> Inicializando '${DB_NAME}': modulos + demo + idioma (puede tardar unos minutos) ..."
    odoo ${DB_ARGS} -d "${DB_NAME}" \
        -i pierinelli_branding,pierinelli_data,pierinelli_demo \
        --load-language=es_419 --stop-after-init

    echo ">>> Migrando adjuntos a la BD (persistencia sin disco) ..."
    odoo shell ${DB_ARGS} -d "${DB_NAME}" <<'PYSHELL'
env['ir.config_parameter'].sudo().set_param('ir_attachment.location', 'db')
env['ir.attachment'].sudo().search([]).force_storage()
env.cr.commit()
PYSHELL
    echo ">>> Inicializacion completa."
else
    echo ">>> BD ya inicializada, omitiendo init."
fi

echo ">>> Iniciando servidor Odoo en el puerto ${HTTP_PORT} ..."
exec odoo ${DB_ARGS} -d "${DB_NAME}" --db-filter="^${DB_NAME}$" --http-port="${HTTP_PORT}" "$@"
