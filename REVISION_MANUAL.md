# Revisión del Manual "Madre Selva" — estado y guía de capturas

Comparación del **Manual_Odoo19_Pierinelli_CasoDeUso.pdf** con el software **hoy**: qué ya está
listo, qué queda pendiente (menor) y dónde/cómo tomar cada captura.

Leyenda: ✅ listo · ⏳ pendiente menor.

---

## 1. ✅ Lo que YA está en el software (coincide con el manual)

| Tema | Detalle |
|---|---|
| **Login + marca** | Login con logo, fondo showroom y botón dorado |
| **Menú de apps** | Grilla a pantalla completa; el login **cae directo** en ella |
| **Idioma** | Español (Latinoamérica) |
| **Contactos** | 18 clientes con RUC + **Constructora Altavista SAC** (cliente del caso) y **María Fernanda Riva (Arquitecta)** |
| **CRM** | Embudo con **8 oportunidades**, incluida **"Encimeras Madre Selva — 12 dptos" (S/ 96,000)** |
| **Listas de precios** | Público · **Profesionales (−12%)** · **Proyectos por volumen** (asignada a Altavista) |
| **Ventas / Cotización** | 10 cotizaciones + 38 pedidos, y la **cotización modelo S00049 "Madre Selva"** con secciones MATERIALES/SERVICIOS |
| **Servicios** | Corte y fabricación · Instalación + flete · Flete a obra |
| **Inventario multi-almacén** | 5 sedes con stock y **valorización** |
| **Compras** | 5 órdenes + recepciones + **facturas de proveedor** |
| **Facturación (IGV)** | 26 facturas cliente (pagadas/pendientes) + **factura de anticipo 50%** (caso Madre Selva) |
| **Manufactura** | Lista de materiales + órdenes de fabricación (placa→piezas) con **trazabilidad por lote** |
| **Contabilidad** | Vencimientos (contado/30/45 días), pagos, analítica por obra, Balance / Estado de resultados |
| **Usuarios persona** | **Valeria, Diego, Carlos, Rosa, Aquino, don Jorge** creados (ver §4) |
| **Conversaciones** | Discuss + chatter con @menciones |

---

## 2. ⏳ Pendiente (menor — a tu criterio)

| Tema | Situación | Cómo resolverlo |
|---|---|---|
| **Lotes por bloque/tono (TAJ-B12-T2)** | El catálogo por m² **no** usa lote (para no romper las ventas). La trazabilidad se demuestra con el ejemplo **placa→piezas**. | Capturar la trazabilidad desde Manufactura / el lote de la placa. Si se quiere lote en planchas reales, es config de implementación. |
| **Tablero gerencial (Fig 10.1)** | La app **Tableros** está lista, pero el tablero no viene armado. | Armarlo en vivo: Informes → gráfico → **Agregar al tablero**, luego capturar. |
| **Etapa "Negociación" (CRM)** | El sistema trae 4 etapas (Nuevo/Calificado/Propuesta/Ganado); el manual menciona 5. | Ajuste de texto en el manual, o crear la etapa "Negociación". |
| **SUNAT / landed costs / reabastecimiento / variantes** | No implementados. | El manual ya los describe como **"fase de implementación"** → dejar como están. |

---

## 3. Correcciones ya aplicadas al documento (texto del manual)
*(B y C ya corregidos por ti — se listan solo como referencia.)*
- **Producto héroe:** "Cuarcita Taj Mahal" → **"Cuarcita Enigma"** (existe, con foto).
- **Almacenes:** "Showroom Miraflores (MIR)" → **"Pierinelli Urban Gallery" (UG)**; "Almacén Zárate (ZAR)" → **"Almacén Principal" (PRIN)**. VES/TRU/AQP coinciden.

---

## 4. Usuarios para las capturas
Contraseña de todos: **`pierinelli`** · el `admin` conserva la suya.

| Persona | Login | Rol / ve |
|---|---|---|
| **Valeria Campos** | `valeria@pierinelli.com` | Ventas + CRM |
| **Diego Torres** | `diego@pierinelli.com` | Ventas + CRM |
| **Carlos Ramos** | `carlos@pierinelli.com` | Inventario |
| **Rosa Delgado** | `rosa@pierinelli.com` | Facturación / Contabilidad |
| **Maestro Aquino** | `aquino@pierinelli.com` | Manufactura |
| **Jorge Pierinelli** | `jorge@pierinelli.com` | Gerencia (todo) |

> También existen los roles genéricos (`gerente`, `vendedor`, `almacen`, `compras`, `contabilidad`).
> Para las capturas de cada capítulo, entra con la persona que lo protagoniza.

---

## 5. Alineación capítulo por capítulo + dónde capturar

| Cap. / Figura | En el software | Estado | Captura |
|---|---|---|---|
| **1 / Fig 1.1** — Pantalla de apps | Grilla a pantalla completa | ✅ | Login → menú de apps. Encuadra toda la grilla con el buscador. |
| **2 / Fig 2.1** — Login | Login branded | ✅ | Pantalla de login (con `valeria@pierinelli.com`). Full-screen. |
| **2.3** — Chatter | Chatter en toda ficha | ✅ | Abre una cotización → encuadra el chatter. |
| **3 / Fig 3.1** — Contacto | Altavista SAC con RUC + arquitecta | ✅ | Contactos → **Constructora Altavista SAC** (RUC, contactos, dirección). |
| **4 / Fig 4.1** — Embudo CRM | 8 oportunidades incl. Madre Selva | ✅ | CRM → Mi flujo → Kanban con la tarjeta "Encimeras Madre Selva". |
| **5 / Fig 5.1** — Cotización | **S00049** con secciones + servicios + lista de precios | ✅ | Ventas → Pedidos → **S00049 (Altavista SAC)**. Se ven MATERIALES/SERVICIOS e IGV. |
| **5.2** — Listas de precios | 3 listas creadas | ✅ | Ventas → Productos → Listas de precios; la ficha de Altavista muestra "Proyectos por volumen". |
| **6 / Fig 6.1** — Stock en la red | 5 almacenes | ✅ | Inventario → Informes → Existencias → **Agrupar por Ubicación**. |
| **6.3 / 9** — Lotes | Trazabilidad placa→piezas | ⏳ | Inventario → Productos → placa → lote → **Trazabilidad**. |
| **7** — Compras | OC + recepción + factura proveedor | ✅ | Compras → Pedidos → abre una OC (con su Recepción). |
| **8 / Fig 8.1** — Factura anticipo 50% | Anticipo posteado (Madre Selva) | ✅ | Contabilidad → Clientes → Facturas → la **factura de anticipo** de Altavista. |
| **9** — Manufactura | LdM + OF (placa→piezas) | ✅ | Manufactura → Órdenes de fabricación → abre la de "Corte". |
| **10 / Fig 10.1** — Tableros | App presente, sin tablero armado | ⏳ | Armar el tablero (Informes → Agregar al tablero) y capturar. |
| **11** — Conversaciones | Discuss + chatter | ✅ | App Conversaciones y una @mención en el chatter de un documento. |
| **12** — Recorrido integral | Todo el flujo | ✅ | Es guion; se valida haciendo el recorrido. |

---

## 6. Guía para tomar buenas capturas
**Preparación:** Chrome/Edge en pantalla completa (F11), 1920×1080, zoom 100% (Ctrl+0), datos del seed cargados, entra con la **persona** del capítulo.
**Encuadre:** captura solo la ventana de Odoo (**Win+Shift+S**); deja visibles la **miga de pan** y los **smart buttons** superiores; activa el **Agrupar por** que menciona el manual antes de capturar.
**Consistencia:** misma resolución/zoom/idioma en todas; nombra los archivos por figura (`fig-1-1_apps.png`, `fig-5-1_cotizacion.png`…) para reemplazar fácil las maquetas.

---

*Para aplicar todo: `git push` + recrear la BD (o correr el seed). Debe terminar en **`SEED COMPLETO (version 10)`**.*
