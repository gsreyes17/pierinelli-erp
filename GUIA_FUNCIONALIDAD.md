# Guía de funcionalidad y del seed — Pierinelli ERP

Dos partes:
1. **Cómo funciona el seed** (`seed_pe.py`): qué carga, cómo se ejecuta y cómo ampliarlo.
2. **Mapa de lo ya construido**: dónde está cada función en Odoo, cómo usarla, exponerla y demostrarla.

---

# PARTE 1 — El seed (`seed_pe.py`)

## 1.1 ¿Qué es y por qué existe?
Es un script que **rellena la base de datos con datos de ejemplo y configura la contabilidad
peruana**. Se ejecuta **después** de instalar los módulos (no durante), porque el plan de
cuentas peruano solo se carga de forma fiable con el sistema ya arrancado. Por eso NO está en
un módulo, sino en un script aparte que se corre con la consola de Odoo (`odoo shell`).

## 1.2 ¿Cuándo se ejecuta?
- **Automático** (Docker/Render): el `entrypoint.sh` lo corre solo en el primer arranque y en
  cada deploy con código nuevo. No tienes que hacer nada.
- **Manual** (local), cuando quieras cargarlo o recargarlo:
  ```bash
  .venv\Scripts\python.exe odoo\odoo-bin shell -c odoo.conf -d odoo < seed_pe.py
  ```

## 1.3 ¿Qué carga? (secciones del script)
| # | Sección | Qué crea |
|---|---|---|
| 1 | Plan contable | Carga el plan peruano `pe` → **IGV 18%** y tipos de comprobante |
| 2 | RUC compañía | Pone el RUC de Pierinelli y su tipo de identificación |
| 3 | IGV en productos | Aplica IGV 18% de venta y compra a todos los productos |
| 4 | Catálogo | +24 productos (30 en total) por tipo de piedra |
| 5 | Clientes | 18 clientes con **RUC válido** (dígito verificador correcto) |
| 6 | Proveedores | 5 proveedores con RUC |
| 7 | Stock | Reparte existencias en los **5 almacenes** |
| 8 | Compras | 5 órdenes de compra confirmadas y **recibidas** |
| 9 | Ventas + Facturas | 45 ventas; ~30 **Facturas electrónicas** posteadas con IGV |
| 10 | Transferencias | 3 traslados de stock **entre almacenes** |
| 11 | CRM | 12 oportunidades repartidas en el embudo |

## 1.4 Idempotencia (no duplica)
El script se puede correr varias veces sin duplicar datos:
- Al final guarda un parámetro `pierinelli.seed_pe_version = 1`.
- Si lo vuelves a correr y la versión coincide, **no hace nada**.
- Además, cada registro se busca antes de crear (por nombre / código / referencia).

## 1.5 Cómo AMPLIAR o cambiar los datos
Edita [seed_pe.py](seed_pe.py):

- **Más/menos ventas:** cambia el `range(45)` en la sección 9.
- **Más productos:** agrega filas a la lista `catalogo` (sección 4): `('Nombre', 'CODIGO', 'categoria', precio)`.
  Categorías válidas: `cuarcita, granito, marmol, onix, sinterizada, porcelanico, cuarzo, solid_surface`.
- **Más clientes:** agrega nombres a `nombres_cli` (sección 5). El RUC se genera solo.
- **Más oportunidades CRM:** agrega a la lista `temas` (sección 11).

**Para que se vuelva a ejecutar con los cambios**, sube el número de versión arriba del script:
```python
SEED_VERSION = '2'   # antes '1'
```
y córrelo de nuevo (o, en Render, haz push: el deploy lo corre solo).

## 1.6 Empezar de cero (borrar y recargar)
- **Local:** crea una BD nueva e instala + seed (ver `DEPLOY.md`).
- **Render free:** cambia `DB_NAME` en el blueprint o recrea la base PostgreSQL → el entrypoint
  reinicializa todo desde cero.

---

# PARTE 2 — Mapa de lo construido: usar, exponer y demostrar

> **Consejo:** activa el **Modo desarrollador** para ver todo (menús técnicos, campos, etc.):
> **Ajustes → (abajo) Activar el modo de desarrollador**.

## 2.1 Módulos instalados y para qué sirven
| Módulo | App en Odoo | Para qué |
|---|---|---|
| Ventas | **Ventas** | Cotizaciones, pedidos, clientes |
| Inventario | **Inventario** | Almacenes, stock, entregas, transferencias |
| Compras | **Compras** | Órdenes de compra a proveedores |
| Contabilidad / Facturación | **Contabilidad** | Facturas con IGV (simulación SUNAT) |
| CRM | **CRM** | Embudo de oportunidades |
| Pierinelli (branding/data/pe/demo) | — | Marca, catálogo, localización PE y datos |

## 2.2 Dónde está cada cosa (navegación)

### Ventas
- **Ventas → Pedidos → Cotizaciones / Pedidos**: verás las 45 ventas del seed.
- **Ventas → Clientes**: los 18 clientes con RUC.
- **Ventas → Productos → Productos**: el catálogo (30) con precio por m² e IGV.
- **Ventas → Informes**: gráficos por categoría, top productos (el "tablero").

### Inventario
- **Inventario** (panel): tarjetas por operación (Recepciones, Entregas, Transferencias internas).
- **Inventario → Productos → Productos**: stock disponible por producto.
- **Inventario → Informes → Existencias**: cantidades por almacén.
- **Inventario → Configuración → Almacenes**: los 5 almacenes (UG, PRIN, VES, TRU, AQP).
- **Inventario → Operaciones → Transferencias**: las entregas y los 3 traslados entre sedes.

### Compras
- **Compras → Pedidos → Pedidos de compra**: las 5 órdenes (confirmadas/recibidas).
- **Compras → Proveedores**: los 5 proveedores con RUC.

### Contabilidad / Facturación (SUNAT)
- **Contabilidad → Clientes → Facturas**: ~30 **Facturas** posteadas con **IGV 18%**.
  - Abre una factura → verás el **tipo de comprobante = Factura**, el **RUC** del cliente y el **IGV**.
- **Contabilidad → Configuración → Impuestos**: el IGV 18% (venta/compra).
- **Contabilidad → Informes**: libro de ventas, impuestos, etc.
- > Recuerda: es simulación; **no** transmite a SUNAT (falta certificado + OSE + módulo EDI).

### CRM
- **CRM → Ventas → Mi canalización** (Pipeline): las 12 oportunidades en columnas
  (Nuevo / Calificado / Propuesta / Ganado). Arrástralas entre etapas.

## 2.3 Los procedimientos ya construidos (flujos usables)

### A) Venta completa (Cotización → Pedido → Entrega → Factura con IGV)
1. **Ventas → Nuevo** → cliente + productos (cantidad en m²).
2. **Confirmar** → se crea la **entrega** en Inventario.
3. Botón **Entrega** → **Validar** (descuenta stock).
4. Botón **Crear factura** → **Confirmar** → factura **Factura** con **IGV 18%**.

### B) Compra (Pedido → Recepción)
1. **Compras → Nuevo** → proveedor + productos.
2. **Confirmar pedido** → se crea la **recepción**.
3. Botón **Recepción** → **Validar** (ingresa stock).

### C) Transferencia entre almacenes
- **Inventario → Operaciones → Transferencias → Nuevo**, tipo *Transferencia interna*:
  origen = un almacén, destino = otro. Validar mueve el stock entre sedes.

### D) Embudo comercial (CRM)
- **CRM → Nuevo** → oportunidad con cliente e ingreso esperado; muévela por el embudo;
  desde una oportunidad puedes generar una **cotización**.

## 2.4 Cómo EXPONER las funciones a los usuarios

### Modo desarrollador (para ver todo)
**Ajustes → Activar el modo de desarrollador**. Muestra menús técnicos, IDs y opciones avanzadas.

### Usuarios y permisos por rol
**Ajustes → Usuarios y compañías → Usuarios → Nuevo**. En la pestaña de permisos define el rol:
- **Vendedor**: Ventas = *Usuario*; CRM = *Usuario*.
- **Almacenero**: Inventario = *Usuario*.
- **Comprador**: Compras = *Usuario*.
- **Contador**: Contabilidad = *Contador/Asesor*.
- **Administrador**: acceso completo.

Cada usuario, al entrar, verá **solo las apps de su rol** (así "expones" cada módulo a quien corresponde).

### Mostrar/ocultar apps
Las apps aparecen en el menú superior/lanzador. Para ocultar una a un usuario, quítale ese permiso.
Para instalar apps nuevas: **Ajustes → Aplicaciones** (requiere modo desarrollador para ver todas).

## 2.5 Guion sugerido para demostrar al cliente (10 min)
1. **Login** con la marca (logo + dorado).
2. **CRM → Pipeline**: mostrar oportunidades por etapa.
3. **Ventas → Pedidos**: abrir un pedido; **Crear factura** → mostrar **IGV 18%** y tipo **Factura**.
4. **Contabilidad → Facturas**: abrir una factura posteada (RUC + IGV).
5. **Inventario → Existencias**: stock por los 5 almacenes; mostrar una **transferencia entre sedes**.
6. **Compras**: un pedido de compra recibido.
7. **Ventas → Informes**: el tablero (ventas por categoría de piedra).

## 2.6 Agregar datos manualmente (sin tocar código)
Todos los módulos permiten **crear registros a mano** con el botón **Nuevo**. Úsalo para
personalizar la demo en vivo (un cliente real, una cotización específica, etc.). Para cargas
masivas repetibles y reproducibles en el servidor, mejor amplía el **seed** (Parte 1.5).

---

## Documentos relacionados
- [GUIA.md](GUIA.md) — arranque y uso básico.
- [DEPLOY.md](DEPLOY.md) — desplegar en VPS / general.
- [RENDER.md](RENDER.md) — desplegar en Render.
- [seed_pe.py](seed_pe.py) — el script de datos comentado.
