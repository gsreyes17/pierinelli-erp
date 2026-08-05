# Guía operativa — paso a paso

Esta es la ruta exacta para operar el flujo diario. Regla principal: cada
plancha se registra una sola vez, desde su recepción de compra.

## 1. Preparar un producto

1. Abra **Inventario**.
2. Vaya a **Productos → Productos**.
3. Busque el material por nombre o Código SAP y ábralo.
4. Revise Código de referencia interna, precio de venta, categoría y tipo de
   material.
5. En la sección de planchas, confirme el **Prefijo de plancha**. Por ejemplo,
   `CIG` genera `CIG0826.01`, `CIG0826.02`, etc.
6. Pulse **Guardar**.

Para un material natural, la foto del producto no reemplaza la foto de cada
plancha: esa se carga después de recibirla.

## 2. Crear una Orden de Compra

1. Abra **Compras**.
2. Vaya a **Órdenes → Órdenes de compra**.
3. Pulse **Nuevo**.
4. Seleccione el proveedor.
5. En **Productos**, agregue cada material y coloque el total comprado en m².
   No registre aquí el número de planchas: el stock y el costo promedio se
   controlan en m². El número de planchas y sus medidas se detallan en la
   recepción.
6. Pulse **Confirmar orden**.
7. En la parte superior, pulse el botón inteligente **Recepciones**.

No valide la recepción todavía: primero deben registrarse las planchas físicas.

## 3. Registrar planchas dentro de la recepción

1. En la recepción abierta, pulse **Registrar planchas recibidas**.
2. En la ventana emergente verá una fila por producto recibido.
3. Para cada grupo de planchas con las mismas medidas, complete:
   - **Planchas**: cantidad de planchas iguales.
   - **Largo**, **Alto** y **Espesor**.
   - **Condición**: Estándar, Oferta o Liquidación.
   - **Ubicación referencial**, por ejemplo `Rack B · Zona 2`.
   - **Ref. importación**, por ejemplo el código del contenedor.
4. Revise **m² por plancha** y **m² total**. El total de las filas del mismo
   producto debe ser igual a **m² esperados**.
5. Si cambian las medidas, pulse **Agregar una línea**. En la nueva fila,
   seleccione primero el campo **Producto de la recepción**; luego complete
   cantidad de planchas y sus medidas. Este paso vincula la nueva fila con el
   material que se está recibiendo.
6. Pulse **Registrar en la recepción**.
7. De vuelta en el albarán, pulse **Validar** para ingresar el stock.

El sistema bloquea una recepción con productos por lote si no se registraron
sus planchas. No use **Inventario → Planchas → Alta de Planchas** para una
mercadería que ya tiene recepción de compra.

## 4. Cargar foto y revisar una plancha

1. Abra **Inventario → Planchas → Tabla de Operaciones**.
2. Busque por Código interno, Código SAP o Ref. importación.
3. Haga clic en la fila para abrir la ficha.
4. Cargue la foto en el recuadro de imagen superior izquierdo.
   Para verla a detalle después, pulse **Ver imagen grande**: se abrirá en otra
   pestaña del navegador.
5. Complete **Observaciones** si hay veta, quiñe, despunte o fisura.
6. Revise **Aptitud comercial**:
   - `Vendible`: aparece para ventas.
   - `Liquidación`: aparece para ventas identificada como tal.
   - `Pendiente de revisión` o `Muestra / no vendible`: no puede reservarse.
7. Pulse **Guardar**.

En la **Tabla de Operaciones** están visibles las columnas **Material**
(Natural/Artificial) y **Foto propia**. Filtre o ordene por esta última para
ubicar rápidamente las planchas naturales que aún necesitan fotografía.

Una plancha natural sin foto individual no puede reservarse ni venderse.

## 5. Aplicar costos de importación

1. Después de validar la recepción, abra **Inventario → Operaciones → Costos
   en destino**.
2. Pulse **Nuevo**.
3. En **Transferencias**, agregue la recepción o las recepciones del contenedor.
4. En **Líneas de costo**, agregue flete, seguro, aduana o manipuleo. Indique
   monto y método de reparto.
5. Pulse **Calcular**.
6. Revise las líneas de valoración generadas.
7. Pulse **Validar**.

Esto incorpora los gastos al costo promedio AVCO y genera su efecto contable.

## 6. Crear una cotización y reservar una plancha

1. Abra **Ventas**.
2. Vaya a **Órdenes → Cotizaciones** y pulse **Nuevo**.
3. Seleccione el cliente.
4. En **Líneas de pedido**, agregue el producto.
5. En la misma línea seleccione **Plancha**. Solo se muestran planchas con
   stock y aptas para vender.
6. Complete los m² o **Piezas** si son losas pre-cortadas.
7. En **Días de reserva**, escriba de `1` a `7`.
8. Marque **Requiere corte** si el cliente compra una medida a cortar. Déjelo
   vacío si se entrega completa.
9. Pulse **Confirmar**.

Al confirmar se bloquea esa plancha para el pedido, cliente y asesor. No se
puede reservar más m² de los disponibles ni reutilizarla en otro pedido vigente.

## 7. Consultar o liberar una reserva

1. Abra **Ventas → Planchas**.
2. Pulse el filtro **Reservadas** o busque por plancha/cliente.
3. Abra la ficha de la plancha.
4. En **Reserva / Venta**, revise cliente, pedido, inicio y fecha final.
5. Si el cliente desiste, pulse **Liberar reserva**.

El proceso automático diario libera una reserva vencida sin comprobante. Borra
cliente, pedido, asesor y fechas, y el estado vuelve a **Disponible**. El
historial queda en el chatter de la plancha.

## 8. Crear y ejecutar una Orden de Corte

1. Abra el pedido confirmado en **Ventas → Órdenes → Órdenes de venta**.
2. Pulse **Crear Orden de Corte** en la cabecera.
3. Verifique Plancha, Cliente y Asesor.
4. En **Cortes**, pulse **Agregar una línea** e indique pieza, cantidad, largo
   y alto. Repita para todas las piezas.
5. Complete **Retorno: largo** y **Retorno: alto** si sobrará material útil.
6. Elija **Destino de la merma**: asumida por el cliente o pérdida del negocio.
7. En **Modulación (PDF)**, adjunte los PDF exportados desde AutoCAD.
8. Pulse **Imprimir OP + Modulación** para entregar a producción un solo PDF
   con la orden y planos.
9. Al finalizar el trabajo, pulse **Ejecutar corte**.

El retorno recibe un código hijo. Si mide menos de 0.5 m en algún lado queda
**Pendiente de revisión** y no se ofrece a ventas.

## 9. Registrar una merma manual

1. Abra **Inventario → Planchas → Registrar Merma**.
2. Seleccione la plancha.
3. Indique m², motivo, destino y notas.
4. Pulse **Registrar**.
5. Si luego resulta aprovechable, vaya a **Inventario → Planchas → Mermas**,
   abra el registro y pulse **Reingresar**.

## 10. Entregar y facturar

1. Abra el pedido en **Ventas → Órdenes → Órdenes de venta**.
2. Pulse el botón inteligente **Entrega**.
3. Revise que las operaciones muestren la plancha reservada.
4. Pulse **Validar**.

Si la línea tenía activado **Requiere corte**, la entrega se bloquea hasta que
la Orden de Corte correspondiente esté en estado Hecho.

5. Regrese al pedido y pulse **Crear factura**.
6. Revise la factura; si está en dólares, elija el **Origen de la tasa**.
7. Pulse **Confirmar / Contabilizar**.

Al contabilizar, el número y fecha del comprobante se copian a la ficha de la
plancha.

## 11. Controles diarios por rol

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
- El escaneo móvil nativo es Enterprise; un lector USB puede ser alternativa.
- El OCR de facturas PDF es Enterprise; en Community se recomienda importar XML.
