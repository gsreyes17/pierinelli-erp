# Despliegue y compartición — Pierinelli ERP (Odoo 19)

Cómo guardar el proyecto en Git y lanzarlo a un servidor (Render o VPS).

---

## 0. Idea clave

- **No subas el núcleo de Odoo** (`odoo/`, ~1GB). En el servidor se usa la **imagen oficial
  `odoo:19`** y solo necesitas tu carpeta **`custom_addons/`** + los archivos de despliegue.
- Tu repo queda pequeño: `custom_addons/`, `Dockerfile`, `docker-compose.yml`, `render.yaml`,
  `config/odoo.conf`, `GUIA.md`, `DEPLOY.md`.
- El `.gitignore` ya excluye `odoo/`, `.venv/`, `.odoo_data/` y `odoo.conf` local.

---

## 1. Guardar y compartir con Git

```bash
cd f:/Repositorios/Pierinelli
git init
git add .gitignore .dockerignore custom_addons config Dockerfile docker-compose.yml render.yaml GUIA.md DEPLOY.md
git commit -m "Pierinelli ERP: branding + datos + despliegue"

# Subir a GitHub (crea antes el repo vacio en github.com)
git branch -M main
git remote add origin https://github.com/<tu-usuario>/pierinelli-erp.git
git push -u origin main
```

> El `custom_addons/` contiene los dos módulos (`pierinelli_branding`, `pierinelli_data`).
> Eso es lo único propio que necesita el servidor.

---

## 2. ¿Dónde desplegar? (comparación honesta)

| Opción | Costo aprox. | Facilidad | Notas |
|---|---|---|---|
| **VPS + Docker** (Hetzner, DigitalOcean) | **US$ 5–12/mes** | Media | **Mejor relación precio/rendimiento** para Odoo. Control total. |
| **Render** (Docker + Postgres) | US$ ~7–25/mes | Alta | Fácil con `render.yaml`. Requiere plan con **≥1GB RAM** y **disco persistente**. |
| **Odoo.sh** (oficial) | US$ ~24+/mes | Muy alta | Lo más simple para Odoo, pero más caro y atado a Odoo. |

> ⚠️ **Odoo necesita ≥1GB RAM.** Planes gratuitos (512MB) **no** lo soportan bien.
> Para demo al cliente: VPS pequeño o Render plan Standard.

---

## 3. Probar en local con Docker (igual que producción)

```bash
docker compose up -d --build
docker compose logs -f odoo     # ver el progreso de la auto-inicializacion
```
El `entrypoint.sh` **se auto-inicializa**: crea la BD e instala módulos + **demo** + idioma
español en el primer arranque. No hay que correr ningún comando de init manual.
Abrir http://localhost:8069 — para reiniciar desde cero: `docker compose down -v && docker compose up -d`.

---

## 4A. Desplegar en un VPS (recomendado)

1. Crea un VPS (Ubuntu, **≥2GB RAM**) e instala Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   ```
2. Clona el repo y levanta (se auto-inicializa con la demo):
   ```bash
   git clone https://github.com/<tu-usuario>/pierinelli-erp.git
   cd pierinelli-erp
   docker compose up -d --build
   docker compose logs -f odoo
   ```
3. Pon **HTTPS** con un dominio: lo más simple es **Caddy** (reverse proxy automático con
   Let's Encrypt), o **Nginx + certbot**, delante del puerto 8069.
4. Producción: en `config/odoo.conf` sube `workers = 2` (con ≥2GB RAM) y cambia `admin_passwd`.

> Otras PaaS Docker (Railway, Fly.io, Koyeb) usan el mismo `Dockerfile`: conectas el repo y
> defines las variables `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME` apuntando a tu PostgreSQL.

---

## 4B. Desplegar en Render

Ver la guía dedicada **[RENDER.md](RENDER.md)** (incluye plan free y el Blueprint `render.yaml`).
También se auto-inicializa; no requiere comandos manuales.

---

## 5. ¿Demo fresca o estado EXACTO?

- **Demo fresca (por defecto):** el módulo `pierinelli_demo` ya **reproduce toda la demo**
  (clientes, ventas entregadas, embudo CRM, idioma) en cualquier instalación desde cero.
  No necesitas hacer nada extra: el auto-init la carga.
- **Estado EXACTO de tu BD local** (si hiciste cambios manuales que quieras conservar tal cual):
  **restaura un respaldo de tu BD local**:

1. **Respaldar** (local): http://localhost:8069/web/database/manager → *Backup* de la BD `odoo`
   (descarga un `.zip` que **incluye el filestore**: imágenes, adjuntos).
2. **Restaurar** (servidor): abre `https://<tu-servidor>/web/database/manager`
   (clave maestra = `admin_passwd` del `config/odoo.conf`) → *Restore* → sube el `.zip`.

> Esto trae TODO: módulos, branding, productos, almacenes, el pedido S00002, la entrega
> validada y el idioma. Es la vía más fiel para la presentación.
> Requisito: el servidor debe tener la **misma versión de Odoo (19) y los mismos módulos**
> (ya están en la imagen).

---

## 6. Checklist de producción

- [ ] Cambiar `admin_passwd` en `config/odoo.conf`.
- [ ] HTTPS (Render lo da; en VPS usar Nginx + Let's Encrypt). `proxy_mode=True` ya está.
- [ ] `workers = 2` (o más) en `config/odoo.conf` si el servidor tiene ≥2GB RAM.
- [ ] Backups automáticos de la BD (cron `pg_dump` o backup de Render).
- [ ] Disco persistente montado en `/var/lib/odoo` (filestore) — ya en `render.yaml`/compose.
