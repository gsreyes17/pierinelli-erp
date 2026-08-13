# Guion de demostración: operación, comprobantes y contabilidad

Este guion sirve para una demostración de 4 a 6 minutos. Debe mostrarse con un
periodo que contenga datos de prueba y dejar claro que el ERP registra y
controla la operación; la presentación electrónica SUNAT se habilita en una
fase posterior con conector, credenciales y validación oficial.

## 1. Venta, entrega y factura

1. Ir a **Ventas → Pedidos → Cotizaciones** y abrir una cotización o crear una
   nueva con cliente, productos, cantidades y precio.
2. Confirmar el pedido. Abrir el botón de **Entrega**, revisar lote, almacén y
   cantidades, y pulsar **Validar**.
3. Volver al pedido y pulsar **Crear factura**. En la factura revisar cliente,
   diario de ventas, fecha, moneda y líneas; seleccionar el tipo de comprobante
   cuando corresponda y pulsar **Confirmar**.
4. Usar **Registrar pago** para asociar el cobro a Caja o Banco.

Qué decir: “La operación nace una sola vez. El pedido desencadena la salida de
almacén; la factura genera el asiento; y el cobro deja trazabilidad financiera.”

## 2. Tipos de comprobante y notas

1. Ir a **Contabilidad → Configuración → Tipos de Comprobantes** para mostrar
   los tipos internos: factura `01`, boleta `03`, nota de crédito `07`, nota de
   débito `08`, recibo por honorarios, importación y planilla de movilidad.
2. Para una nota de crédito, abrir una factura publicada y usar la acción de
   **Nota de crédito / Revertir**. Revisar el documento resultante antes de
   publicarlo.
3. Para una nota de débito, usar el flujo de nota de débito disponible en la
   factura y revisar el documento tipo `08` antes de publicarlo.

Qué decir: “El tipo de comprobante clasifica el sustento y el flujo Odoo genera
el efecto contable. La emisión electrónica ante SUNAT requiere un conector CPE.”

## 3. Compra y detracción

1. Ir a **Compras → Pedidos → Solicitudes de presupuesto**, crear o abrir una
   orden, confirmar y validar la recepción.
2. Desde el pedido usar **Crear factura**; revisar proveedor, moneda, IGV y
   clasificar la compra como mercadería, servicio, gasto o activo fijo.
3. En la factura abrir la pestaña **Control tributario**. Agregar una línea de
   tipo **Detracción**, indicar porcentaje, base, fecha y constancia. El importe
   se calcula automáticamente.
4. Cambiar a **Pagado** solamente después de realizar y comprobar el depósito.

Qué decir: “La detracción queda controlada contra el comprobante: base,
porcentaje, importe y constancia. El depósito bancario y su integración SUNAT
se activan cuando se implemente el conector tributario.”

## 4. Guía y almacén

1. Ir a **Inventario → Operaciones → Entregas** y abrir la entrega creada por
   el pedido. Mostrar origen, destino, cliente, productos y lotes.
2. Ir a **Contabilidad → Reportes → Libros y SIRE**, seleccionar **Guías de
   remisión y entregas** y pulsar **Cargar vista previa**.

Qué decir: “Aquí está la trazabilidad física del despacho. Es una guía interna
de entrega; la GRE SUNAT requiere XML, firma digital, envío y CDR.”

## 5. Terceros y asiento manual

1. Ir a **Contabilidad → Contabilidad → Asientos contables → Nuevo**.
2. Elegir un diario misceláneo y, en el campo de cabecera, seleccionar el
   **Contacto / contraparte**. En las líneas se puede elegir un tercero distinto
   cuando la naturaleza del asiento lo requiera.
3. Registrar cuenta, glosa, Debe y Haber; comprobar que ambos totales cuadren y
   publicar solo después de revisión.
4. Para carga masiva ir a **Contabilidad → Contabilidad → Importar asientos**,
   descargar la plantilla y completar **Contacto o RUC** con un contacto ya
   creado. La importación crea borradores, nunca publica automáticamente.

Qué decir: “Todo asiento puede llevar su contraparte. En caja chica el
proveedor o beneficiario ahora se transfiere también al asiento generado.”

## 6. Caja chica y contacto

1. Ir a **Contabilidad → Contabilidad → Caja Chica** y abrir una caja.
2. En **Movimientos**, registrar fecha, proveedor o beneficiario, sustento,
   documento, cuenta de gasto e importe. Pulsar **Contabilizar**.
3. Abrir el vínculo del asiento creado y comprobar que el contacto aparece en
   la cabecera y en sus líneas.
4. Registrar el efectivo contado, confirmar arqueo y usar **Cerrar caja**;
   si hay gasto pendiente, usar **Reponer desde banco**.

## 7. Libro Diario, Mayor y Balance

1. Ir a **Contabilidad → Reportes → Libros y SIRE**.
2. Elegir **Libro Diario clásico**, seleccionar el periodo y pulsar **Cargar
   vista previa**. Mostrar: contacto, cuenta, Debe, Haber, impuesto aplicado,
   importe de impuesto, cuenta de impuesto y, si existe, detracción/constancia.
3. Explicar que el monto de IGV se muestra solo en la línea tributaria para no
   duplicarlo; la cuenta de esa línea revela la cuenta de IGV utilizada.
4. Elegir **Libro Mayor clásico**, seleccionar una cuenta y cargar la vista.
   Mostrar **Saldo anterior**, movimientos cronológicos y saldo deudor o
   acreedor.
5. Elegir **Balance de Comprobación**. Mostrar saldos iniciales, movimientos y
   saldos finales separados en deudor/acreedor, siempre como importes positivos.
6. Usar **Excel** o **PDF** para revisión y exposición. El botón **TXT PLE**
   demuestra el archivo plano y su nombre, pero no implica presentación SUNAT.

## Mensaje de cierre

> “El sistema conecta venta, compra, almacén, caja y contabilidad. Cada
> documento deja su asiento, tercero, cuentas e impuestos identificables; los
> libros permiten revisarlo por movimiento o por cuenta. Excel y PDF dan una
> salida clara para control. La última milla tributaria —CPE, GRE, validación
> PVSIRE, envío y CDR— se implementa con la configuración y credenciales reales
> de la empresa.”

## Alcance tributario que no se debe prometer aún

- El TXT no debe cargarse en SIRE sin adaptar todos los campos y reglas vigentes
  de SUNAT, y validarlo con PVSIRE.
- No existe emisión de factura, boleta, nota, GRE ni detracción electrónica ante
  SUNAT/OSE; tampoco recepción de CDR.
- La detracción actual es control operativo. No genera por sí sola el depósito
  al Banco de la Nación ni un asiento automático de pago.
