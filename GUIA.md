# Guía — ERP Pierinelli (Odoo 19 Community)

Backend de gestión para **Pierinelli** (revestimientos de piedra premium), personalizado con
su identidad visual (negro / blanco / dorado), en **español**, con **Ventas** e **Inventario**
listos y una **demo funcional** cargada.

---

## 1. Requisitos del entorno

| Componente | Versión / Dato |
|---|---|
| Odoo | 19.0 Community (carpeta `odoo/`) |
| Python | 3.11 (entorno virtual en `.venv/`) |
| PostgreSQL | 18 (servicio en `localhost:5432`) |
| Base de datos | `odoo` |
| Usuario BD | `Odoo` / contraseña `Odoo` |
| Contraseña maestra | `pierinelli-admin-2026` (en `odoo.conf`) |

> La configuración vive en **`odoo.conf`** (raíz del proyecto). Incluye las rutas de
> módulos (core + `custom_addons`), la carpeta de datos `.odoo_data/` y el modo desarrollo.

---

## 2. Cómo arrancar el sistema

Desde la raíz del proyecto (`f:\Repositorios\Pierinelli`):

```powershell
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf
```

Luego abrir en el navegador: **http://localhost:8069**

Para **detener**: `Ctrl + C` en la terminal.

### Acceso
- Usuario: `admin`
- Contraseña: la que definiste al crear la base (la de tu instalación).

La pantalla de **login** ya muestra el fondo oscuro con el **logo blanco Pierinelli** y el botón dorado.

---

## 3. Idioma

El sistema está en **Español (Latinoamérica)** (`es_419`):
- El usuario `admin` y la compañía están en español.
- Los **nuevos contactos/usuarios** se crean en español por defecto.

Para cambiar el idioma de un usuario puntual:
**Ajustes → Usuarios y Compañías → Usuarios →** (usuario) **→ Preferencias → Idioma**.

---

## 4. Estructura del proyecto

> **Regla de oro:** nunca se edita el núcleo de Odoo (`odoo/addons/*`). Toda la
> personalización vive en **`custom_addons/`**, para poder actualizar Odoo sin perder nada.

```
Pierinelli/
├── odoo/                  # Núcleo de Odoo 19 (no tocar)
├── custom_addons/         # Personalización propia
│   ├── pierinelli_branding/   # Identidad visual (negro/blanco/dorado + logo)
│   └── pierinelli_data/       # Datos del negocio (compañía, almacenes, productos)
├── .venv/                 # Entorno Python
├── odoo.conf              # Configuración
└── GUIA.md                # Este documento
```

### `pierinelli_branding` — identidad visual
- Acento **dorado `#C9962F`** en botones, enlaces y elementos activos.
- Barra superior **negra**.
- **Login** con fondo oscuro y logo blanco.

### `pierinelli_data` — datos del negocio
- **Compañía:** Pierinelli (Miraflores), `info@pierinelli.com`, +51 960 750 867, moneda **PEN**.
- **5 almacenes:** Urban Gallery (UG), Principal/Zárate (PRIN), Villa El Salvador (VES),
  Trujillo (TRU), Arequipa (AQP).
- **8 categorías** de piedra: Cuarcita, Granito, Mármol, Ónix, Piedra Sinterizada,
  Porcelánico, Cuarzo, Solid Surface.
- **6 productos** de muestra, vendidos por **m²**, con stock inicial en Urban Gallery.
- Multi-almacén activado.

---

## 5. Datos cargados (catálogo de muestra)

| Código | Producto | Categoría | Precio (S/ por m²) |
|---|---|---|---|
| CUA-ENIGMA | Cuarcita Enigma | Cuarcita | 850 |
| ONX-ORO | Ónix Oro | Ónix | 1200 |
| GRA-MAORI | Granito Maori | Granito | 650 |
| MAR-PORTORO | Mármol Portoro | Mármol | 1500 |
| SIN-AMAZONICO | Piedra Sinterizada Amazónico | Sinterizada | 900 |
| CRZ-CALACATTA | Cuarzo Silestone Calacatta Gold | Cuarzo | 780 |

---

## 6. Demo funcional para mostrar al cliente

Ya está cargada una **venta completa de extremo a extremo**:

- **Cliente:** Constructora Andina Demo S.A.C.
- **Pedido:** `S00002` — confirmado — **Total: S/ 50,800**
  - Mármol Portoro × 15 m²
  - Cuarcita Enigma × 22 m²
  - Ónix Oro × 8 m²
- **Entrega:** `UG/OUT/00002` — **validada (Hecho)** → el stock se descontó del almacén.

### Recorrido sugerido en la reunión
1. **Login** → mostrar la marca (logo + dorado).
2. **Ventas → Pedidos** → abrir `S00002` (cotización confirmada con total y líneas).
3. **Inventario → Operaciones** → abrir la entrega `UG/OUT/00002` (estado *Hecho*).
4. **Inventario → Productos** → abrir un producto y ver el **stock disponible** por almacén.
5. **Inventario → Reportes → Existencias** → mostrar las cantidades por almacén.

---

## 7. Cómo registrar una venta (paso a paso)

1. **Ventas → Pedidos → Nuevo**.
2. Elegir o crear el **Cliente**.
3. En **Otra información**, confirmar el **Almacén** de despacho (UG, PRIN, etc.).
4. Agregar **líneas de producto** (cantidad en **m²**).
5. **Confirmar** → Odoo genera automáticamente la **entrega** en Inventario.
6. Ir a la **entrega** (botón *Entrega* arriba del pedido) → **Validar** para descontar stock.

---

## 8. Mantenimiento

### Reaplicar cambios de un módulo (tras editar código/SCSS/datos)
```powershell
# Actualizar módulo de marca
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf -d odoo -u pierinelli_branding --stop-after-init

# Actualizar datos del negocio
.venv\Scripts\python.exe odoo\odoo-bin -c odoo.conf -d odoo -u pierinelli_data --stop-after-init
```
> En modo desarrollo (`dev_mode` ya activo en `odoo.conf`), los cambios de **SCSS y plantillas**
> se recargan sin reiniciar; basta refrescar el navegador.

### Respaldo de la base de datos
Desde **http://localhost:8069/web/database/manager** (contraseña maestra `pierinelli-admin-2026`),
o por línea de comandos con `pg_dump`.

---

## 9. Pendientes / próximos pasos sugeridos

- **Localización Perú (SUNAT):** facturación electrónica, RUC, tipos de comprobante.
- **Logo para PDFs:** el logo blanco no se ve sobre fondo blanco de facturas/cotizaciones;
  preparar una versión en negro o sobre banda oscura.
- **Atributos de producto:** acabado, espesor, formato/placa.
- **Control por placa/lote** (trazabilidad de cada placa de piedra).
- **Usuarios y permisos** por rol (vendedor, almacenero, administrador).
- **Catálogo completo** importado desde su web/listas reales.

---

*Toda la personalización está aislada en `custom_addons/`; el núcleo de Odoo permanece intacto
y actualizable.*
