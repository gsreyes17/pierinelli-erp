# Desplegar la demo en Render (capa gratuita)

Guía paso a paso para subir la demo de Pierinelli ERP a **Render** usando el plan **free**.

> El repo ya está preparado para **auto-inicializarse**: en el primer arranque crea la base de
> datos e instala los módulos + la demo (clientes, ventas, CRM) + el idioma español. No necesitas
> restaurar ningún respaldo.

---

## ⚠️ Lee esto primero (honestidad sobre el plan free)

| Límite del plan free | Efecto en Odoo |
|---|---|
| **512 MB RAM** | Odoo es pesado. La **primera inicialización** (instalar módulos) puede ser lenta o, en el peor caso, fallar por memoria. Mitigación abajo. |
| **Sin disco persistente** | Los adjuntos se guardan en la **BD** (ya configurado). El logo del PDF y datos sobreviven. |
| **Se suspende por inactividad** | Tras ~15 min sin uso, el servicio "duerme". La siguiente visita tarda ~50 s en despertar. |
| **PostgreSQL free expira** (~30 días) | Para una demo está bien. Para algo permanente, sube a un plan pago o VPS. |

**Si la inicialización falla por memoria:** cambia temporalmente el servicio web a plan **Starter**
(US$ 7/mes) solo para el primer arranque; cuando la BD ya esté creada, puedes bajarlo a free.

---

## Paso 1 — Subir el proyecto a GitHub

```bash
cd f:/Repositorios/Pierinelli
git init
git add .gitignore .dockerignore custom_addons config Dockerfile entrypoint.sh \
        docker-compose.yml render.yaml GUIA.md DEPLOY.md RENDER.md
git commit -m "Pierinelli ERP listo para Render"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/pierinelli-erp.git
git push -u origin main
```

> No se sube el núcleo de Odoo (`.gitignore` lo excluye); Render usa la imagen oficial `odoo:19`.

---

## Paso 2 — Crear los servicios en Render con el Blueprint

1. Entra a https://dashboard.render.com → **New +** → **Blueprint**.
2. Conecta tu cuenta de GitHub y elige el repo `pierinelli-erp`.
3. Render leerá `render.yaml` y propondrá crear:
   - **pierinelli-db** (PostgreSQL, free)
   - **pierinelli-odoo** (Web Service Docker, free)
4. Pulsa **Apply**. Render construye la imagen y conecta la BD automáticamente
   (las variables `DB_HOST`, `DB_USER`, etc. se inyectan solas).

---

## Paso 3 — Esperar la primera inicialización

- En **pierinelli-odoo → Logs** verás:
  ```
  >>> Inicializando 'pierinelli': modulos + demo + idioma ...
  >>> Migrando adjuntos a la BD ...
  >>> Iniciando servidor Odoo ...
  ```
- La primera vez tarda varios minutos (instala módulos y crea la demo).
- Cuando el **Health check** (`/web/health`) pase a verde, está listo.

---

## Paso 4 — Entrar

- Abre la URL pública (algo como `https://pierinelli-odoo.onrender.com`).
- Verás el **login con la marca Pierinelli**.
- Usuario inicial: `admin` / contraseña: `admin` (créala/cámbiala en el primer acceso si lo pide).

> Ya estará todo: español, 5 almacenes, catálogo, **pedidos de venta**, **entregas validadas**,
> **embudo CRM** y **cotizaciones PDF con logo**.

---

## Paso 5 — Seguridad mínima (recomendado)

- Cambia `admin_passwd` en `config/odoo.conf` (clave maestra) y vuelve a desplegar.
- Cambia la contraseña del usuario `admin` desde la interfaz.

---

## Probarlo localmente antes (opcional, idéntico a Render)

Con Docker instalado:
```bash
docker compose up -d --build
# ver el progreso de la inicializacion:
docker compose logs -f odoo
```
Abrir http://localhost:8069 — se inicializa solo, igual que en Render.
Para reiniciar desde cero: `docker compose down -v` (borra la BD) y `up` de nuevo.
