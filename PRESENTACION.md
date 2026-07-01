# Speech de presentación — Pierinelli ERP

Guion hablado, un apartado por sección. En **negrita** lo que dices; entre paréntesis
**(→ dónde ir)** los pasos para ir mostrando mientras hablas.

> Consejo: antes de empezar, ten abiertas en pestañas **Ventas, Inventario y Contabilidad**,
> y entra al sistema con `Ctrl+F5`. Habla pausado; cada clic acompaña una frase.

---

## 0 · Apertura
**"Buenos días. Lo que van a ver no es un software genérico: es el ERP de Pierinelli. Un solo
lugar donde vive todo el negocio —desde que un arquitecto pide una cotización hasta que se cobra
la factura y se ve la ganancia— con el control del material en las cinco sedes. Fíjense que ya
tiene la identidad de la casa: el logo, los colores, el español."**
*(→ Muestra la pantalla de login con la marca; ingresa. Aparece el menú de aplicaciones a
pantalla completa.)*
**"Este es el tablero: cada botón es un área del negocio. Vamos a recorrerlo como ocurre en la
vida real, de la venta al cobro."**

---

## 1 · Cotización (el inicio de la venta)
**"Todo empieza con una cotización. El vendedor arma la propuesta eligiendo las piedras del
catálogo —con su foto real y su precio por metro cuadrado— y el sistema calcula el IGV solo.
Esa cotización se le envía al cliente en un PDF con la marca de Pierinelli, listo para aprobar."**
*(→ Ventas → Pedidos → Cotizaciones. Abre una cotización; muestra las líneas, el total y el
botón Vista previa / Imprimir para ver el PDF con el logo.)*
**"Cuando el cliente aprueba, con un clic la cotización se convierte en pedido en firme, y el
sistema genera automáticamente la orden de entrega al almacén. Nadie vuelve a digitar nada."**
*(→ En un pedido confirmado, señala el botón de Entrega que se generó solo.)*

---

## 2 · Inventario y logística en las 5 sedes
**"Al confirmar la venta, el almacén ya tiene la orden. Cuando se valida la entrega, el stock se
descuenta del almacén real: el inventario siempre refleja la verdad."**
*(→ Abre la entrega del pedido → botón Validar. Luego Inventario → Informes → Existencias.)*
**"Aquí ven el stock de cada material en las cinco sedes: Urban Gallery, Principal, Villa El
Salvador, Trujillo y Arequipa. Y si a una tienda le falta material, se hace una transferencia
entre sedes; el sistema mueve el inventario y deja el rastro de todo."**
*(→ Inventario → Operaciones → Transferencias; abre una transferencia interna entre almacenes.)*

---

## 3 · Material padre → materiales hijos (partir placas)
**"Y algo muy propio del rubro de la piedra: llega una placa grande y muchas veces hay que
partirla en piezas. El sistema lo entiende como un material padre que se transforma en materiales
hijos, y guarda la trazabilidad completa: de qué placa madre salió cada pieza, con su número de
lote. Control total, placa por placa."**
*(→ Fabricación → Órdenes de fabricación; abre la orden "Corte" de una placa. Muestra que
consumió 1 placa y produjo las piezas.)*
**"Y lo mejor: puedo pararme en cualquier pieza y ver su origen exacto."**
*(→ Inventario → Productos → abre una pieza → Números de serie/lote → botón Trazabilidad; se ve
el árbol placa madre → piezas hijas.)*

---

## 4 · Inventario valorizado (costos y margen)
**"El inventario no solo dice cuánto hay, dice cuánto vale. Cada producto tiene su costo, así que
la gerencia ve el valor real de lo que tiene en almacén y el margen de cada venta —lo que se gana
después de descontar el costo."**
*(→ Inventario → Informes → Valorización de inventario; muestra el valor total. Opcional: en un
producto, la pestaña donde figura el Costo.)*

---

## 5 · Facturación electrónica con IGV
**"Del pedido nace la factura, con todo lo que exige el Perú: tipo de comprobante Factura, el RUC
del cliente y el IGV del 18%, calculado automáticamente."**
*(→ En el pedido → Crear factura → Confirmar. Muestra el tipo de comprobante, el RUC y el IGV.)*
**"Y en un solo lugar veo el estado de cada comprobante: cuáles ya están pagados y cuáles siguen
pendientes."**
*(→ Contabilidad → Clientes → Facturas; muestra la columna Estado de pago: Pagado / No pagado.)*
> Nota honesta si preguntan: es una simulación funcional; el envío electrónico real a SUNAT se
> conecta después con el certificado digital y un OSE. Ya está preparado el terreno.

---

## 6 · Cuentas por cobrar (CxC)
**"Aquí está una de las claves para el flujo de caja: las cuentas por cobrar. Cada factura tiene
su fecha de vencimiento según el plazo que se pactó —contado, 30 o 45 días—, así que en todo
momento sé quién me debe y desde cuándo."**
*(→ Contabilidad → Clientes → Facturas; filtra por "Vencidas" o "Por pagar" y agrupa por Cliente.
Se ve el saldo por cobrar de cada uno.)*
**"Y puedo entrar al detalle de un cliente y ver toda su cuenta: lo que compró, lo que pagó y lo
que queda pendiente."**
*(→ Abre la ficha de un Cliente; muestra su total por cobrar / el libro mayor de socios.)*

---

## 7 · Cuentas por pagar (CxP) y abastecimiento
**"Del otro lado está el abastecimiento y las cuentas por pagar. Se emite la orden de compra a la
cantera o al importador, se recibe la mercadería —que entra al inventario— y se registra la
factura del proveedor, que queda como una obligación a pagar con su vencimiento."**
*(→ Compras → Pedidos de compra; abre una, muestra su Recepción validada. Luego Contabilidad →
Proveedores → Facturas.)*
**"Así el negocio equilibra los dos lados: lo que entra por cobrar y lo que sale por pagar, sin
perder de vista ningún vencimiento."**

---

## 8 · Tesorería (pagos y conciliación)
**"Cuando un cliente paga o cuando le pagamos a un proveedor, el pago se registra y se enlaza con
su factura. La factura cambia sola a 'Pagada' y el dinero queda reflejado en bancos o caja."**
*(→ Abre una factura Pagada; muestra el pago conciliado en la parte superior.)*

---

## 9 · Rentabilidad por obra (analítica)
**"Y para la gerencia, la pregunta de oro: ¿cuánto deja cada obra? Cada venta se etiqueta con su
proyecto, así que se puede ver la rentabilidad por obra: cuánto se facturó y cuánto costó en cada
una."**
*(→ Contabilidad → Informes → Informe analítico / o abre una obra en las cuentas analíticas.)*

---

## 10 · Estados financieros en tiempo real
**"Todo lo que acabamos de ver —vender, comprar, cobrar, pagar— genera su asiento contable
automáticamente. Por eso la gerencia tiene, sin Excel y sin doble digitación, el Estado de
Resultados y el Balance al día: cuánto se vendió, cuánto se debe, cuánto hay en caja."**
*(→ Contabilidad → Informes → Estado de resultados y Balance general.)*

---

## 11 · Usuarios, roles y comunicación
**"Y esto no es de una sola persona: es multiusuario con permisos por rol. El vendedor ve Ventas,
el almacenero ve Inventario, la contadora ve Contabilidad. Cada uno entra y ve solo lo suyo, y se
comunican dentro del propio sistema, sin salir a WhatsApp ni al correo."**
*(→ Ajustes → Usuarios y compañías → Usuarios; muestra la lista de roles. Opcional: entra con el
usuario 'vendedor' para mostrar que solo ve sus apps. Muestra el chatter al pie de una factura.)*

---

## 12 · Cierre
**"En resumen: un ERP que se ve como Pierinelli y opera como Pierinelli. De la cotización a la
entrega, de la factura al cobro, con el control del material placa por placa y las finanzas al
día. Todo conectado, en un solo lugar, y listo para crecer por capas —facturación electrónica
SUNAT, más reportes— a medida que lo necesiten."**

---

### Mini-recorrido de 5 minutos (si hay poco tiempo)
1. Login + menú de apps. 2. Una cotización → confirmar. 3. Existencias en las 5 sedes.
4. Trazabilidad placa→piezas. 5. Una factura con IGV pagada. 6. Facturas "Por pagar" (CxC).
7. Estado de resultados.
