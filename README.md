# Pierinelli ERP

Backend de gestión sobre **Odoo 19 Community**, personalizado para **Pierinelli**
(revestimientos de piedra premium — cuarcita, granito, mármol, ónix, sinterizada, porcelánico,
cuarzo, solid surface).

**Incluye:** marca propia (negro/blanco/dorado), español, catálogo por **m²**, inventario
**multi-almacén (5 sedes)**, cotizaciones y ventas, compras, **facturación con IGV 18% +
estados financieros (simulación SUNAT)** y menú de apps a pantalla completa. Con datos de
ejemplo reproducibles. (El CRM lo gestiona la empresa en su propio sistema.)

---

## Documentación
| Documento | Para qué |
|---|---|
| **[PRESENTACION.md](PRESENTACION.md)** | Speech para el cliente, apartado por apartado, con los pasos a mostrar. |
| **[GUIA.md](GUIA.md)** | Guión de demo, cómo usar cada módulo, usuarios y el seed. |
| **[LOCAL.md](LOCAL.md)** | Ejecutar en local (Windows) + usuarios de ejemplo. |
| **[RENDER.md](RENDER.md)** | Desplegar en la nube (Render / Docker / VPS). |

## Arranque rápido (local)
```powershell
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf
```
→ http://localhost:8069  (cargar datos de ejemplo desde cero: ver [LOCAL.md](LOCAL.md))

## Estructura del proyecto
```
Pierinelli/
├── odoo/                     # Núcleo Odoo 19 (no se toca; en deploy = imagen odoo:19)
├── custom_addons/            # Lo propio
│   ├── pierinelli_branding/  # Marca: login, colores, logo
│   ├── pierinelli_data/      # Compañía, almacenes, categorías, productos
│   ├── pierinelli_pe/        # Localización Perú (l10n_pe + purchase) para SUNAT
│   └── web_responsive/       # Menú de apps a pantalla completa (OCA)
├── seed_pe.py                # Datos de ejemplo + contabilidad con IGV (post-install)
├── config/odoo.conf          # Config de producción (contenedor)
├── Dockerfile · docker-compose.yml · render.yaml · entrypoint.sh
├── GUIA.md · LOCAL.md · RENDER.md · README.md
```

## Notas
- **Colores:** negro `#111111` · blanco `#FFFFFF` · dorado `#C9962F`.
- **SUNAT:** es una **simulación** (IGV, RUC, Factura). El envío real requiere certificado
  digital + OSE + módulo EDI (OCA/Enterprise), fuera de Community.
- **Local en Windows:** el seed se corre con `cmd /c "... < seed_pe.py"` (PowerShell no acepta `<`).
