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

# Primer arranque: crear BD + instalar módulos + idioma español
docker compose run --rm odoo odoo \
  -d pierinelli -i pierinelli_branding,pierinelli_data \
  --load-language=es_419 --stop-after-init

docker compose restart odoo
```
Abrir http://localhost:8069

---

## 4A. Desplegar en un VPS (recomendado)

1. Crea un VPS (Ubuntu) e instala Docker + Docker Compose.
2. Clona el repo y levanta:
   ```bash
   git clone https://github.com/<tu-usuario>/pierinelli-erp.git
   cd pierinelli-erp
   docker compose up -d --build
   docker compose run --rm odoo odoo -d pierinelli \
     -i pierinelli_branding,pierinelli_data --load-language=es_419 --stop-after-init
   docker compose restart odoo
   ```
3. Pon **Nginx + HTTPS** (Let's Encrypt) delante del puerto 8069.

---

## 4B. Desplegar en Render

1. Sube el repo a GitHub.
2. En Render: **New + → Blueprint** y apunta a este repo (usa `render.yaml`).
3. Render crea la base PostgreSQL y el servicio web Docker con disco persistente.
4. **Inicialización (una vez)**: en el **Shell** del servicio web, ejecuta:
   ```bash
   odoo -d pierinelli -i pierinelli_branding,pierinelli_data \
     --load-language=es_419 --stop-after-init
   ```
   (o restaura un backup — ver §5).
5. Entra por la URL pública. Cambia `admin_passwd` en `config/odoo.conf` antes de producción.

---

## 5. Llevar la DEMO EXACTA al servidor (recomendado para el cliente)

Los módulos recrean **productos, almacenes y categorías** al instalarse, pero el **pedido de
demo `S00002`** y la **activación del idioma** se hicieron en tu BD local. Para que el servidor
se vea idéntico, **restaura un respaldo de tu BD local**:

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
