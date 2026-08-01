# Pierinelli ERP

Backend de gestión sobre **Odoo 19 Community**, personalizado para **Pierinelli**
(revestimientos de piedra premium — cuarcita, granito, mármol, ónix, sinterizada,
porcelánico, cuarzo, solid surface).

**Incluye:** marca propia (negro/blanco/dorado), español, **inventario por plancha**
(cada plancha con código interno, medidas, foto, condición y reserva), multi-almacén
(5 sedes), costo promedio con valorización en tiempo real, ventas, compras,
**facturación con IGV 18%**, 17 reportes PDF con marca (10 contables + 7 de almacén)
y dashboard "Panorama de Almacenes". Con datos de ejemplo reproducibles.

---

## Documentación

| Documento | Para qué |
|---|---|
| **[PLAN_INVENTARIO_V2.md](PLAN_INVENTARIO_V2.md)** | El plan aprobado del modelo por plancha: decisiones, fases y limitaciones. |
| **[ALCANCE_PEDIDO_VS_BONUS.md](ALCANCE_PEDIDO_VS_BONUS.md)** | Qué pidió el cliente vs. qué damos de valor agregado. |
| **[CONTEXTO_PROYECTO.md](CONTEXTO_PROYECTO.md)** | Síntesis completa del proyecto para retomar contexto. |
| **[AVANCES_V2.md](AVANCES_V2.md)** | Registro de lo ya implementado del plan, bloque por bloque. |
| **[GUIA.md](GUIA.md)** | Guión de demo y cómo usar cada módulo. |
| **[GUIA_ALMACENES.md](GUIA_ALMACENES.md)** | Manual del inventario multi-sede. |
| **[LOCAL.md](LOCAL.md)** | Ejecutar en local (Windows) + usuarios de ejemplo. |
| **[RENDER.md](RENDER.md)** | Desplegar en la nube (Render / Docker / VPS). |

## Arranque rápido (local)
```powershell
.\arrancar.ps1
```
→ http://localhost:8069  (cargar datos desde cero: ver [LOCAL.md](LOCAL.md))

## Cómo funciona este entorno (local vs. nube)

El proyecto vive en **tres capas**; solo la del medio viaja entre ellas:

```
┌─ LOCAL (tu máquina) ──────────────────────────────────────────┐
│  odoo/        núcleo Odoo 19 clonado — SOLO local, NO en git  │
│  .venv/       Python del proyecto  — SOLO local, NO en git    │
│  odoo.conf    config local (credenciales) — NO en git         │
│  PostgreSQL local (BD "odoo")                                 │
└───────────────────────────────────────────────────────────────┘
┌─ GIT (lo que se versiona y se sube) ──────────────────────────┐
│  custom_addons/   los 6 módulos propios                       │
│  seed_pe.py       datos de ejemplo reproducibles              │
│  entrypoint.sh · Dockerfile · render.yaml · config/odoo.conf  │
│  *.md             documentación                               │
└───────────────────────────────────────────────────────────────┘
┌─ RENDER (nube) ───────────────────────────────────────────────┐
│  Imagen Docker oficial odoo:19  →  aporta el núcleo de Odoo   │
│  + lo de git (addons, seed, entrypoint)                       │
│  + PostgreSQL de Render                                       │
└───────────────────────────────────────────────────────────────┘
```

**La carpeta `odoo/` no se sube nunca** (está en `.gitignore`): en la nube ese rol
lo cumple la imagen `odoo:19`. Pero **en local sí es imprescindible** — Windows no
usa Docker aquí: `arrancar.ps1` ejecuta `odoo\odoo-bin` directamente. Si se borra,
el entorno local deja de funcionar.

## Estructura del proyecto
```
Pierinelli/
├── odoo/                       # Núcleo Odoo 19 (solo local; en deploy = imagen odoo:19)
├── custom_addons/              # Lo propio (esto es lo que se desarrolla)
│   ├── pierinelli_branding/    # Marca: login, colores, logo
│   ├── pierinelli_data/        # Compañía, almacenes, familias/subfamilias
│   ├── pierinelli_pe/          # Localización Perú (l10n_pe + purchase)
│   ├── pierinelli_planchas/    # Inventario por plancha (modelo V2)
│   ├── pierinelli_reportes/    # 10 reportes financieros PCGE en PDF
│   ├── pierinelli_almacenes/   # Dashboard Panorama + 7 reportes de almacén
│   └── web_responsive/         # Menú de apps a pantalla completa (OCA)
├── seed_pe.py                  # Datos de ejemplo + contabilidad con IGV
├── arrancar.ps1                # Arranque local (inyecta wkhtmltopdf al PATH)
├── config/odoo.conf            # Config de producción (contenedor)
├── Dockerfile · docker-compose.yml · render.yaml · entrypoint.sh
```

## Notas
- **Colores:** negro `#111111` · blanco `#FFFFFF` · dorado `#C9962F`.
- **SUNAT:** es una **simulación** (IGV, RUC, Factura). El envío real requiere
  certificado digital + OSE + módulo EDI, fuera de Community.
- **PDF en local:** requieren wkhtmltopdf 0.12.6 (`winget install wkhtmltopdf.wkhtmltox`);
  `arrancar.ps1` lo pone en el PATH.
- **Local en Windows:** el seed se corre con `cmd /c "... < seed_pe.py"` (PowerShell
  no acepta `<`).
