# Chuleta de demo — botón por botón

Para tener al lado durante la presentación. Cada escena dice **dónde ir, qué
pulsar, qué decir y qué hacer si algo falla**. El recorrido completo toma 6-8
minutos; puedes cortar donde quieras, cada escena cierra sola.

**Regla de oro para los nervios:** nada de lo que toques rompe la base. Todo lo
que crees en vivo (cotización, gasto de caja, kardex) es un registro más de la
demo. Si algo se ve raro: `Ctrl+F5` y sigues.

---

## 0. Antes de empezar (2 minutos, sin público)

1. Arranca el servidor: `.\arrancar.ps1` → espera "Iniciando Odoo".
2. Abre http://localhost:8069 → entra con **gerente** / `pierinelli`.
3. `Ctrl+F5` una vez (recarga estilos).
4. Comprobación rápida: **Contabilidad → Configuración → Tipos de Cambio**
   debe tener la tasa de HOY (SUNAT y Corporativa). Si no está, pulsa
   **Actualizar desde SUNAT**, o créala con **Nuevo** (30 segundos).

## 1. Panorama de Almacenes (el impacto inicial)

- **Ve a:** menú de apps → **Inventario**. El Panorama abre solo.
- **Muestra:** las 5 sedes con su valor, el mapa del Perú, el ranking con fotos.
- **Di:** «Esto es lo primero que ve gerencia: cuánto inventario hay, dónde
  está y cuánto vale — en tiempo real.»
- **Toca:** una tarjeta de sede → se abre su stock. Vuelve con ← del navegador.

## 2. La plancha única (el corazón)

- **Ve a:** **Inventario → Planchas → Tabla de Operaciones**.
- **Muestra:** la tabla con las columnas del ERP anterior (almacén, código SAP,
  medidas, condición, estado…). Abre una plancha **natural** → su foto única.
- **Di:** «Cada plancha física es una ficha: su código, sus medidas, su foto,
  su historia. El problema del ERP anterior — dos vendedores vendiendo la misma
  plancha — aquí es imposible.»
- **Bonus losas:** en Filtros elige **Losas pre-cortadas** → planchas que se
  venden por pieza, con su columna Piezas.

## 3. Venta apartando LA plancha

- **Ve a:** **Ventas → Pedidos → Cotizaciones** → abre una en borrador
  (o **Nueva**: cliente + producto).
- **Pulsa:** en la línea, columna **Plancha** → elige una → la cantidad se
  propone sola → **Confirmar**.
- **Di:** «El vendedor aparta ESTA plancha, no "4 m² de algo". Queda reservada
  7 días a nombre del cliente; si otro vendedor la intenta, el sistema lo
  bloquea.»
- **Si falla:** la plancha elegida puede estar reservada — elige otra de la
  lista (solo muestra disponibles).

## 4. Venta en dólares y tipo de cambio

- **En la misma cotización** (o una nueva): campo **Lista de precios** → USD.
- **Muestra:** debajo aparece el panel dorado **Tipo de cambio** → **Cambiar**
  → elige **SUNAT venta** o **Corporativa** → se aplica y se pliega.
- **Di:** «El precio en dólares es el acuerdo comercial. La tasa —SUNAT o la
  nuestra— es solo la equivalencia contable en soles. Ambas decisiones quedan
  registradas.»

## 5. Factura y cobro

- **Desde el pedido confirmado:** **Crear factura** → Factura normal → en la
  factura revisa el **tipo de comprobante** (Factura 01 con RUC / Boleta 03
  con DNI) → **Confirmar**.
- **Pulsa:** **Registrar pago** → Crear pago.
- **Di:** «IGV 18%, numeración peruana, y el comprobante queda escrito en la
  ficha de la plancha vendida.»

## 6. Caja chica en vivo

- **Ve a:** **Contabilidad → Contabilidad → Caja Chica** → abre
  **Caja Chica Demo - Abierta**.
- **Pulsa:** en Movimientos **Agregar línea**: beneficiario, `PM · Planilla de
  movilidad`, cuenta de gasto, importe (p. ej. 35) → **Contabilizar**.
- **Muestra:** el enlace al asiento creado (gasto al Debe, efectivo al Haber).
- **Di:** «La caja chica opera en soles, con sustento por movimiento, arqueo
  físico y reposición desde el banco. Nada queda fuera de contabilidad.»

## 7. Libros, SIRE y balance

- **Ve a:** **Contabilidad → Reportes → Libros y SIRE**.
- **Pulsa:** **Libro Diario clásico** → fechas del mes → **Cargar vista
  previa**. Luego cambia a **Registro de Compras 8.1** y repite.
- **Muestra:** los botones **Excel** y **PDF** (descarga real). El **TXT PLE**
  solo si preguntan — y di que es demostrativo.
- **Di:** «Diario, Mayor, Balance de Comprobación y los formatos 7.1, 8.1,
  8.2, 13.1 y 14.1 — en pantalla, Excel y PDF con la marca.»

## 8. Kardex (el cierre técnico)

- **Ve a:** **Inventario → Productos** → abre cualquier piedra → botón
  **Kardex** (arriba).
- **Muestra:** llega calculado: entradas verdes, salidas rojas, saldo
  corriente. Cambia a **valorizado** → columnas en soles → **Ver kardex**.
- **Di:** «Kardex físico y valorizado por promedio, que cuadra al céntimo con
  el stock real. Exportable a Excel y PDF.»

## Mensaje de cierre

> «El sistema conecta venta, almacén, caja y contabilidad. Cada documento deja
> su asiento, su tercero y sus impuestos identificables. La última milla
> tributaria —facturación electrónica, GRE, SIRE en línea— se implementa con
> las credenciales reales de la empresa.»

---

## Si preguntan lo difícil (respuestas honestas de una línea)

| Pregunta | Respuesta |
|---|---|
| «¿Factura electrónicamente a SUNAT?» | «Registra y controla todo; la emisión electrónica requiere certificado y OSE — es la fase de integración, ya mapeada.» |
| «¿Guías de remisión electrónicas?» | «La guía interna de despacho sí; la GRE electrónica entra en esa misma fase.» |
| «¿El TXT sirve para SIRE?» | «Es demostrativo de estructura; el archivo oficial se genera cuando se conecte la API SIRE con las credenciales SOL.» |
| «¿Depreciación de activos?» | «El formato 7.1 lista los activos; el motor de depreciación automática es un módulo adicional.» |

## Usuarios de repuesto

`gerente` / `vendedor` / `almacen` / `contabilidad` — todos con contraseña
`pierinelli`. Si una pantalla no aparece, probablemente es el usuario: `gerente`
lo ve todo.
