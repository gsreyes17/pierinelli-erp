# Guía Pierinelli ERP — presentación, uso y datos

Odoo 19 Community personalizado para **Pierinelli** (revestimientos de piedra): backend en
español, marca propia, catálogo real por m² con fotos. Foco: **Cotización (Ventas)**,
**Logística (Inventario)** y **Facturación con IGV + estados financieros (simulación SUNAT)**.

- Ejecutar en local → **[LOCAL.md](LOCAL.md)** · Desplegar en la nube → **[RENDER.md](RENDER.md)**
- El CRM no se incluye: lo gestiona la empresa en su propio sistema.

---

# 1. DISCURSO DE PRESENTACIÓN (para el cliente)

> Léelo de corrido mientras navegas. En cursiva, **a dónde ir**.

**Apertura — *(pantalla de login)***
"Buenos días. Lo que verán es el ERP de Pierinelli: un solo sistema donde vive todo el negocio,
desde que un cliente pide una cotización hasta que se cobra la factura, con control de inventario
en las cinco sedes. Fíjense que ya tiene la identidad de Pierinelli —el logo, los colores, el
español— no es un Odoo genérico."
*→ Entra al sistema. Aparece el menú de aplicaciones a pantalla completa.*
"Este es el tablero principal: cada botón es un área del negocio."

**1) La venta empieza por una cotización — *Ventas → Pedidos → Cotizaciones***
"Todo arranca aquí. El vendedor arma una cotización eligiendo las piedras del catálogo —con su
foto real y su precio por metro cuadrado— y el sistema calcula el IGV automáticamente. La
cotización se envía al cliente en un PDF con la marca de Pierinelli."
*→ Abre una cotización, muestra las líneas, el total y el PDF.*
"Cuando el cliente aprueba, con un clic la cotización se convierte en pedido y genera la orden
de entrega. Nadie vuelve a escribir los datos: fluye solo."

**2) La logística y el inventario en las 5 sedes — *Inventario***
"Al confirmar la venta, el almacén recibe la orden de entrega. Al validarla, el stock se
descuenta del almacén real."
*→ Inventario → Informes → Existencias.*
"Aquí ven el stock de cada material en las cinco sedes: Urban Gallery, Principal, Villa El
Salvador, Trujillo y Arequipa. Y si falta material en una tienda, se hace una transferencia
entre sedes —el sistema mueve el inventario y deja el rastro."
*→ Inventario → Operaciones → Transferencias.*
"Y algo muy del rubro: cuando llega una **placa grande**, a veces hay que **partirla en piezas**.
El sistema lo maneja como **material padre → materiales hijos** y guarda la **trazabilidad**:
de qué placa madre salió cada pieza, con su lote."
*→ Fabricación → Órdenes de fabricación (corte de placa). Luego Inventario → Productos → una
pieza → Nº de serie/lote → botón **Trazabilidad**.*

**3) La facturación con IGV — *Contabilidad → Clientes → Facturas***
"Del pedido se genera la factura electrónica: tipo de comprobante Factura, el RUC del cliente y
el IGV del 18%, tal como lo exige el Perú. Unas facturas ya están pagadas y otras pendientes,
así que en todo momento se sabe quién debe."
*→ Abre una factura pagada; muestra el pago conciliado.*
"Aclaro con transparencia: esto es una simulación funcional; el envío real a SUNAT se conecta
después con el certificado digital y un OSE."

**4) La foto financiera — *Contabilidad → Informes***
"Cada factura tiene su **vencimiento** según el plazo pactado —contado, 30, 45 días— así que hay
**antigüedad de saldos**: quién debe y desde cuándo, tanto por cobrar como por pagar. Y como cada
venta se etiqueta con su **obra o proyecto**, la gerencia ve la **rentabilidad por obra**."
*→ Contabilidad → Informes → Anticuamiento de clientes / proveedores.*
"Y como cada venta, compra y pago genera su asiento contable automáticamente, se tiene en tiempo
real el **Estado de resultados** y el **Balance**, y el inventario queda **valorizado** con su
costo. Sin Excel, sin doble digitación."

**5) El abastecimiento — *Compras***
"Del otro lado, las compras a las canteras e importadores: se emite la orden, se recibe la
mercadería —que ingresa al inventario— y se registra la factura del proveedor."

**6) Cada quien ve lo suyo — *(mencionar)***
"El sistema es multiusuario con permisos por rol: el vendedor ve Ventas, el almacenero ve
Inventario, la contadora ve Contabilidad. Cada uno entra y ve solo lo que le corresponde, y se
comunican dentro del propio sistema."

**Cierre**
"En resumen: un ERP que se ve como Pierinelli y opera como Pierinelli —cotización, entrega,
factura y finanzas, todo conectado y en un solo lugar."

> **Tip:** antes de empezar, ten abiertas en pestañas las apps **Ventas, Inventario y
> Contabilidad**, y haz un `Ctrl+F5` en el login.

---

# 2. CÓMO USAR CADA MÓDULO (navegación)

> Activa el **Modo desarrollador**: **Ajustes → Activar el modo de desarrollador**.

| Área | Dónde | Qué hay |
|---|---|---|
| **Ventas / Cotización** | Ventas → Pedidos (Cotizaciones / Pedidos), Clientes, Productos | 10 cotizaciones + 38 pedidos, 18 clientes con RUC, 33 productos reales (con foto) por m² |
| **Inventario / Logística** | Inventario → Operaciones (Entregas, Recepciones, Transferencias), Informes → Existencias / **Valorización** | 5 almacenes, 37 entregas, 3 transferencias, inventario **valorizado** (costo) |
| **Trazabilidad (placa→piezas)** | Fabricación → Órdenes / Listas de materiales · Inventario → Productos → lote → **Trazabilidad** | 2 cortes de placa madre en piezas hijas, genealogía por lote |
| **Compras** | Compras → Pedidos, Proveedores | 5 compras recibidas y facturadas |
| **Facturación** | Contabilidad → Clientes/Proveedores → Facturas | 26 facturas cliente (pagadas/pendientes) + 5 de proveedor, IGV 18% |
| **Cuentas por cobrar/pagar** | Contabilidad → Informes → Anticuamiento | Vencimientos por plazo (contado/30/45 días), antigüedad de saldos |
| **Estados financieros** | Contabilidad → Informes (Balance, Estado de resultados) | Asientos de ventas, compras y pagos |
| **Rentabilidad por obra** | Contabilidad → Informes → Informe analítico | Ventas etiquetadas por obra/proyecto |

### Flujos usables
- **Cotización → venta:** Cotización → Confirmar → Pedido.
- **Logística:** Pedido → Entrega (validar) → descuenta stock; Recepción de compra (validar) → ingresa stock; Transferencia interna entre sedes.
- **Trazabilidad:** Fabricación → Orden (corte de placa) → produce piezas con lote ligado a la placa madre.
- **Facturación:** Pedido → Crear factura → Confirmar (IGV) → Registrar pago.

---

# 3. USUARIOS Y ROLES (referencia)

El sistema es multiusuario con permisos por rol: cada usuario ve **solo sus apps**. Vienen
creados estos de ejemplo (contraseña **`pierinelli`**; el `admin` conserva la tuya):

| Login | Rol | Ve |
|---|---|---|
| `gerente` | Gerente General | Todo (Ventas, Inventario, Compras, Contabilidad — nivel responsable) |
| `vendedor` | Vendedor | Ventas |
| `almacen` | Almacenero | Inventario |
| `compras` | Comprador | Compras |
| `contabilidad` | Contadora | Contabilidad |

Crear/editar usuarios: **Ajustes → Usuarios y compañías → Usuarios**. La comunicación interna
es por **Conversaciones (Discuss)** y por el **chatter** al pie de cada documento (notas,
menciones @, seguidores, actividades).

---

# 4. LOS DATOS DE EJEMPLO (el seed)

Se cargan con **[seed_pe.py](seed_pe.py)** (post-instalación). En Render corre **solo**; en local
se ejecuta a mano (ver [LOCAL.md](LOCAL.md)).

**Qué carga:** plan contable peruano (**IGV 18%**), RUC, **33 productos reales con foto**
(traídos de la web de Pierinelli), con **costo** para valorización, 18 clientes con RUC y
**términos de pago**, 5 proveedores, stock en 5 almacenes, 5 compras + 5 facturas de proveedor,
48 ventas (10 cotizaciones + 38 pedidos) etiquetadas por **obra/proyecto**, 26 facturas de
cliente (≈13 pagadas) con **vencimientos**, 13 pagos, 3 transferencias, **2 cortes de placa→piezas
con trazabilidad** y 5 usuarios por rol.

**Idempotente:** guarda `pierinelli.seed_pe_version`; con la misma versión no duplica. Para
recargar con cambios, sube `SEED_VERSION` y vuelve a correrlo.

---

# 5. CONTABILIDAD Y CICLOS ECONÓMICOS

Lo que **ya está montado y demostrable** en la demo (todo con el paquete Community actual):

| Ciclo | Qué hace | Dónde verlo |
|---|---|---|
| **Ingresos (CxC)** | Factura de cliente con IGV → asiento automático; vencimiento por plazo pactado | Contabilidad → Clientes → Facturas · Informes → Anticuamiento de clientes |
| **Egresos / compras (CxP)** | Factura de proveedor → cuenta por pagar; vencimiento a 30 días | Contabilidad → Proveedores → Facturas · Informes → Anticuamiento de proveedores |
| **Tesorería (bancos/caja)** | Pagos registrados y conciliados con las facturas | Contabilidad → (diarios Banco/Caja) · una factura pagada |
| **Impuestos (IGV/SUNAT)** | IGV 18% en ventas y compras, tipo de comprobante Factura, RUC | Contabilidad → Informes → Impuestos |
| **Inventario valorizado** | Cada producto con **costo** → valor del stock y margen (venta − costo) | Inventario → Informes → Valorización |
| **Rentabilidad por obra** | Ventas etiquetadas con su obra/proyecto (contabilidad analítica) | Contabilidad → Informes → Informe analítico |
| **Estados financieros** | Balance general y Estado de resultados en tiempo real | Contabilidad → Informes |

**Cómo se profundiza más adelante** (siguiente fase, con módulos de localización/OCA/Enterprise):
- **SUNAT real:** envío electrónico (certificado + OSE), **detracciones, retenciones, percepciones**, **libros electrónicos (PLE)**.
- **Conciliación bancaria automática** (importar extractos), **recordatorios de cobro** (follow-ups).
- **Activos fijos** (depreciación), **presupuestos**, **multimoneda**, **cierre de periodo**.

> En resumen: el ciclo económico completo —vender, comprar, cobrar, pagar, declarar IGV y ver
> resultados— **ya opera**; las piezas peruanas avanzadas y la automatización bancaria se suman
> por capas sobre lo que ya está, sin rehacer nada.

---

# 6. LA MARCA
- **Login:** foto de showroom difuminada + card blanca + logo negro + botón dorado.
- **Backend:** acento dorado + barra superior negra. **PDF:** logo + colores Pierinelli.
- **Idioma:** Español (Latinoamérica). **Colores:** negro `#111111` · blanco `#FFFFFF` · dorado `#C9962F`.
