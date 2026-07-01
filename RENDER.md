# Desplegar en RENDER (nube)

El proyecto se **auto-inicializa**: en el primer arranque crea la BD, instala los módulos,
carga el idioma y corre el seed (catálogo real + IGV + facturas + pagos + usuarios). No hay
que ejecutar comandos manuales.

> Se usa la imagen oficial `odoo:19`; solo se versiona `custom_addons/` + los archivos de
> despliegue. El núcleo de Odoo NO se sube (lo excluye `.gitignore`).

## Paso 1 — Subir el repo a GitHub
```powershell
git add -A
git commit -m "Pierinelli ERP"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/pierinelli-erp.git
git push -u origin main
```

## Paso 2 — Crear los servicios (Blueprint)
1. https://dashboard.render.com → **New +** → **Blueprint**.
2. Conecta el repo → Render lee `render.yaml` y propone crear:
   - **pierinelli-db** (PostgreSQL)
   - **pierinelli-odoo** (Web Service Docker)
3. **Apply.** Las variables de conexión (`DB_HOST`, `DB_USER`, …) se inyectan solas.

## Paso 3 — Esperar la inicialización
En **pierinelli-odoo → Logs** verás:
```
>>> Inicializando 'pierinelli': modulos + idioma ...
>>> Ejecutando seed (contabilidad PE + datos con IGV) ...
>>> Iniciando servidor Odoo ...
```
Cuando el health check `/web/health` pase a verde, entra por la URL pública.

## Paso 4 — Redeploys (automático)
El `entrypoint.sh` detecta el commit nuevo (`RENDER_GIT_COMMIT`) y corre `-i/-u` + el seed
automáticamente. Para actualizar: solo `git push`.

## Empezar de cero (BD limpia en Render)
Si cambiaste módulos/seed y quieres reinicializar limpio: **recrea la base PostgreSQL** en Render
(o cambia `DB_NAME` en el blueprint). En el siguiente arranque el entrypoint inicializa todo desde cero.

---

## ⚠️ Capa gratuita (512 MB) — honesto
Con contabilidad (`account` + `l10n_pe` + `purchase`) **más** el seed, el primer arranque es
**pesado** y puede fallar por memoria (OOM). Recomendación:
- Usa **Render Starter** (o sube a Starter solo para el primer deploy y luego baja), o un **VPS**.
- Sin disco persistente los adjuntos se guardan en la BD (ya configurado).
- El servicio se **suspende por inactividad** (~15 min) y la BD free **expira** (~30 días).

## Otros servidores (VPS / Docker)
El mismo `Dockerfile` corre en cualquier lado con Docker:
```bash
docker compose up -d --build
docker compose logs -f odoo
```
En un VPS Ubuntu: instala Docker (`curl -fsSL https://get.docker.com | sh`), clona el repo,
`docker compose up -d --build`, y pon **HTTPS** con Caddy o Nginx+certbot. Para producción,
en `config/odoo.conf` sube `workers = 2` y cambia `admin_passwd`.

## Backup / restore (opcional)
Para copiar un estado exacto entre entornos: `https://<servidor>/web/database/manager`
(clave maestra = `admin_passwd`) → *Backup* / *Restore* (el zip incluye el filestore).
