# Guía operativa — Compra, planchas, corte, entrega y costo

Esta guía describe el flujo diario recomendado para Pierinelli. La regla
principal es simple: **una plancha se registra una sola vez, dentro de su
recepción de compra**. No se recibe primero en m² agregados para luego volver a
darla de alta.

## 1. Preparar el material

Antes de comprar, confirme que el producto tenga código SAP, familia y
subfamilia, precio de venta y costo configurado. Para materiales naturales,
complete también la foto de **cada plancha** al momento de recibirla; para
artificiales se usa la foto del producto.

El prefijo del código interno se genera desde el nombre del producto y puede
ajustarse en la ficha del producto. Por ejemplo, Cuarcita Iron Green usa `CIG`
y sus planchas se numeran como `CIG0826.01`, `CIG0826.02`, etc.

## 2. Comprar y recibir planchas

1. Cree y confirme la Orden de Compra normalmente.
2. Abra la **Recepción** generada por la orden. No la valide todavía.
3. Pulse **Registrar planchas recibidas**.
4. En cada fila indique cuántas planchas tienen esas mismas medidas, largo,
   alto, espesor, condición, ubicación referencial y referencia de
   importación. Agregue otra fila cuando cambien las medidas.
5. El total de m² de las filas debe coincidir con el m² de la recepción por
   producto. El asistente crea un lote por plancha y prepara las operaciones de
   recepción, pero aún no ingresa el stock.
6. Pulse **Registrar en la recepción** y luego valide el albarán estándar.
7. Abra las planchas creadas desde Inventario → Planchas → Tabla de
   Operaciones, suba la foto individual de cada material natural y complete
   observaciones si corresponde.

La validación de una recepción de productos controlados por lote se bloquea si
no se registraron sus planchas. Así se evita duplicar inventario.

> Para inventario inicial o una corrección excepcional existe Alta de Planchas.
> No debe usarse para mercadería que ya tiene una recepción de compra.

## 3. Aplicar costos de importación

Después de validar la recepción, agregue flete, seguro, aduana, manipuleo u
otros gastos al costo promedio:

1. En Inventario → Operaciones → **Costos en destino**, cree un registro.
2. Seleccione la recepción o las recepciones del contenedor.
3. Agregue las líneas de costo y el criterio de reparto adecuado (por cantidad,
   peso, volumen, costo actual o partes iguales).
4. Pulse **Calcular** y revise el prorrateo.
5. Pulse **Validar**.

Odoo incorpora el costo al AVCO de los productos y genera la valorización
contable correspondiente. Use la misma referencia de importación en las
planchas para poder rastrear el contenedor físico y su costo.

### Atajo desde la recepción o traslado entre locales

En lugar de abrir primero el menú de costos en destino, abra la recepción o la
transferencia interna ya validada y entre a la pestaña **Costos adicionales**.
Agregue flete/viaje, seguridad, seguro, aduana, maniobra u otro concepto,
importe, detalle y criterio de reparto. El usuario **Inventario: Administrador**
pulsa **Preparar costeo**; luego, en la pantalla que se abre, pulsa
**Calcular** y **Validar**.

Para planchas use **Por cantidad / m²**. No duplique un mismo gasto en esta
pestaña y en un costo en destino creado manualmente.

## 4. Reservar y vender una plancha

1. En Ventas, cree la cotización y agregue el producto.
2. En la línea elija la **Plancha** concreta. El sistema solo muestra planchas
   con stock, aptas para venta y del formato solicitado.
3. Indique los m² o las piezas. La cantidad no puede superar el saldo de la
   plancha.
4. En **Días de reserva** elija de 1 a 7 días. La fecha final se calcula sola;
   no se permiten reservas superiores a siete días.
5. Marque **Requiere corte** si el cliente compra una medida a cortar. Déjelo
   desmarcado si se entrega la plancha o losa tal cual.
6. Confirme el pedido. La plancha queda reservada para ese pedido, cliente y
   asesor por siete días, y el picking queda asignado a ese lote.

Una misma plancha no puede quedar bloqueada por otro pedido vigente, incluso
si es del mismo cliente. Si vence la reserva y no hay comprobante, el proceso
automático la libera: borra cliente, pedido, asesor y fechas, y la plancha
vuelve a estado Disponible.

Las planchas naturales sin foto individual y los retazos pendientes de revisión
no se pueden reservar ni vender.

## 5. Corte y decisión de retazos

El orden operativo recomendado es:

```
Pedido confirmado → Orden de Corte → Corte ejecutado → Entrega → Factura
```

1. Desde el pedido confirmado pulse **Crear Orden de Corte**.
2. Verifique cliente, plancha y asesor; agregue las piezas con sus medidas.
3. Indique las dimensiones del retorno y el destino de la merma: asumida por
   el cliente o pérdida del negocio.
4. Adjunte los planos de AutoCAD exportados a PDF e imprima **OP + Modulación**
   cuando necesite un único documento para producción.
5. Ejecute la orden. La parte vendida permanece vinculada al pedido, el retorno
   crea una plancha hija y la merma pasa a la Zona de Mermas.
6. Si el retorno tiene una dimensión menor a 0.5 m, queda como **Pendiente de
   revisión** y no aparece como material vendible. Operaciones debe decidir:
   Vendible, Liquidación o Muestra/no vendible. Si se desecha, use Registrar
   Merma para dejar el motivo y el valor trazables.

Una línea marcada como **Requiere corte** no puede validarse en la entrega sin
una Orden de Corte ejecutada para ese pedido y plancha. Esto no afecta ventas
de planchas completas.

## 6. Entregar, facturar y cerrar

1. Desde el pedido abra la entrega. Confirme que el lote mostrado sea la
   plancha reservada y valide el albarán.
2. Cree y contabilice la factura según la política comercial.
3. Al contabilizarse, el número y fecha del comprobante se escriben en la ficha
   de la plancha. La Tabla de Operaciones conserva el historial comercial.

Para ventas en dólares, elija en la factura el origen de la tasa (SUNAT,
corporativa o manual). El sistema registra la tasa usada.

## 7. Controles diarios por rol

| Rol | Control recomendado |
|---|---|
| Almacén | Recepciones pendientes, fotos naturales, ubicación, retazos pendientes y ajustes con motivo. |
| Comercial | Reservas próximas a vencer, planchas disponibles por sede y pedidos que requieren corte. |
| Producción | Órdenes de Corte pendientes, PDF con modulación y mermas del día. |
| Compras | Recepciones sin costo en destino aplicado y contenedores por referencia de importación. |
| Contabilidad | Costos en destino validados, AVCO, facturas, IGV y conciliación de inventario contra cuenta 201. |
| Gerencia | Panorama de Almacenes, Hueso, stock crítico, antigüedad, rotación y pérdidas por merma. |

## Límites conocidos

- La facturación electrónica real a SUNAT requiere OSE/PSE y certificado.
- El escaneo móvil nativo es Enterprise; un lector USB puede usarse como
  alternativa cuando se impriman etiquetas.
- El OCR de facturas PDF es Enterprise; en Community se recomienda importar el
  XML de la factura electrónica.
